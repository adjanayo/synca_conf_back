from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import PassType, Payment, User
from app.schemas.payment_create import PaymentCreate
from app.schemas.payments import PaymentRead
from app.schemas.promo import PromoValidateRequest, PromoValidateResponse
from app.services.promo_service import compute_discounted_amount, get_valid_promo_code

router = APIRouter(prefix="/api", tags=["payments"])


@router.post("/promo/validate", response_model=PromoValidateResponse)
async def validate_promo(
    body: PromoValidateRequest, db: AsyncSession = Depends(get_db)
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
async def create_payment(
    body: PaymentCreate, db: AsyncSession = Depends(get_db)
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
