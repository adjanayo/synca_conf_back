from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.models import PassType, Payment, PromoCode, Ticket, User
from app.schemas.payment_create import PaymentCreate
from app.schemas.payment_webhook import PaymentWebhookPayload
from app.schemas.payments import PaymentRead
from app.schemas.promo import PromoValidateRequest, PromoValidateResponse
from app.services.promo_service import compute_discounted_amount, get_valid_promo_code
from app.services.ticket_finalization import finalize_ticket
from app.services.ticketing import generate_qr_code_hash, generate_ticket_number
from app.services.webhook_verification import (
    InvalidWebhookSignatureError,
    verify_hmac_signature,
    verify_stripe_signature,
)

router = APIRouter(prefix="/api", tags=["payments"])


@router.post("/promo/validate", response_model=PromoValidateResponse)
@limiter.limit("60/minute")
async def validate_promo(
    request: Request, body: PromoValidateRequest, db: AsyncSession = Depends(get_db)
) -> PromoValidateResponse:
    promo = await get_valid_promo_code(db, body.code)
    if promo is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce code promo n'est pas valide.",
        )

    return PromoValidateResponse(
        code=promo.code, discount_pct=promo.discount_pct, discount_fixed=promo.discount_fixed
    )


@router.post("/payments", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("60/minute")
async def create_payment(
    request: Request, body: PaymentCreate, db: AsyncSession = Depends(get_db)
) -> PaymentRead:
    user = await db.get(User, body.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Utilisateur introuvable."
        )

    pass_type = await db.get(PassType, body.pass_type_id)
    if pass_type is None or not pass_type.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce type de billet n'est pas valide.",
        )

    promo_code_id = None
    amount_paid = pass_type.price
    if body.promo_code is not None:
        promo = await get_valid_promo_code(db, body.promo_code)
        if promo is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce code promo n'est pas valide.",
            )
        promo_code_id = promo.id
        amount_paid = compute_discounted_amount(pass_type.price, promo)

    payment = Payment(
        user_id=user.id,
        pass_type_id=pass_type.id,
        promo_code_id=promo_code_id,
        amount_original=pass_type.price,
        amount_paid=amount_paid,
        payment_method=body.payment_method,
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)

    return PaymentRead.model_validate(payment)


@router.post("/payments/webhook/{provider}")
@limiter.limit("60/minute")
async def payment_webhook(
    provider: Literal["stripe", "wave", "orange_money"],
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> dict[str, bool]:
    settings = get_settings()
    raw_body = await request.body()

    try:
        if provider == "stripe":
            verify_stripe_signature(
                raw_body,
                request.headers.get("Stripe-Signature", ""),
                settings.stripe_webhook_secret,
            )
        else:
            secret = (
                settings.wave_webhook_secret
                if provider == "wave"
                else settings.orange_money_webhook_secret
            )
            verify_hmac_signature(
                raw_body, request.headers.get("X-Webhook-Signature", ""), secret
            )
    except InvalidWebhookSignatureError as exc:
        logger.bind(channel="security").warning(
            f"Signature webhook invalide (provider={provider})"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Signature invalide."
        ) from exc

    payload = PaymentWebhookPayload.model_validate_json(raw_body)

    payment = await db.get(Payment, payload.payment_id)
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paiement introuvable.")

    # Idempotence (5.4): a replayed webhook for an already-completed payment
    # must not flip status again or create a second ticket.
    if payment.status == "completed":
        return {"received": True}

    if payload.status == "failed":
        payment.status = "failed"
        await db.commit()
        logger.bind(channel="payment").warning(f"Paiement {payment.id} échoué")
        return {"received": True}

    # Insufficient-validation fix: a transaction_ref must not be attachable
    # to more than one payment -- without this check, replaying the same
    # ref against a *different* payment_id would complete it and mint a
    # second ticket for a transaction that only ever paid once.
    conflicting = (
        await db.execute(
            select(Payment.id).where(
                Payment.transaction_ref == payload.transaction_ref, Payment.id != payment.id
            )
        )
    ).scalar_one_or_none()
    if conflicting is not None:
        logger.bind(channel="security").warning(
            f"transaction_ref {payload.transaction_ref!r} déjà utilisé par le paiement "
            f"{conflicting}, refusé pour le paiement {payment.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette référence de transaction est déjà utilisée.",
        )

    # Atomic (5.5): payment status + ticket creation commit together, or not
    # at all -- a single db.commit() after both mutations is enough since
    # nothing else has touched this session in between.
    payment.status = "completed"
    payment.transaction_ref = payload.transaction_ref
    payment.paid_at = datetime.now(UTC)

    if payment.promo_code_id is not None:
        promo = await db.get(PromoCode, payment.promo_code_id)
        if promo is not None:
            promo.usage_count += 1

    ticket = Ticket(
        user_id=payment.user_id,
        payment_id=payment.id,
        pass_type_id=payment.pass_type_id,
        ticket_number=generate_ticket_number(payment.id),
        qr_code_hash=generate_qr_code_hash(),
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)

    logger.bind(channel="payment").info(
        f"Paiement {payment.id} complété, ticket {ticket.ticket_number} généré"
    )
    # 5.6/5.7: PDF+QR generation and the ticket email happen after the
    # response, via their own DB session -- see finalize_ticket's docstring
    # for why this is deliberately outside the atomic transaction above.
    background_tasks.add_task(finalize_ticket, ticket.id)
    return {"received": True}
