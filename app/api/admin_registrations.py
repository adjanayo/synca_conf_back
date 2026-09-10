from typing import Literal

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.pagination import Pagination, pagination_params
from app.deps.rbac import require_permission
from app.models import PassType, Payment, Ticket, User
from app.models.payments import PAYMENT_STATUS_VALUES
from app.schemas.admin_registrations import RegistrationListRead, RegistrationRead

router = APIRouter(prefix="/api/admin", tags=["admin-registrations"])


@router.get("/registrations", response_model=RegistrationListRead)
@limiter.limit("30/minute")
async def list_registrations(
    request: Request,
    payment_status: Literal[*PAYMENT_STATUS_VALUES] | None = None,
    pagination: Pagination = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("payments.view")),
) -> RegistrationListRead:
    # Inscription (User) et paiement (Payment/Ticket) sont deux étapes
    # distinctes -- LEFT JOIN depuis User pour que les inscrits qui n'ont pas
    # encore payé apparaissent aussi, pas seulement ceux avec un Payment.
    base_query = (
        select(User, Payment, PassType, Ticket.ticket_number)
        .outerjoin(Payment, Payment.user_id == User.id)
        .outerjoin(PassType, PassType.id == Payment.pass_type_id)
        .outerjoin(Ticket, Ticket.payment_id == Payment.id)
    )
    count_query = (
        select(func.count(func.distinct(User.id)))
        .select_from(User)
        .outerjoin(Payment, Payment.user_id == User.id)
    )
    if payment_status is not None:
        base_query = base_query.where(Payment.status == payment_status)
        count_query = count_query.where(Payment.status == payment_status)

    query = base_query.order_by(User.created_at.desc()).limit(pagination.limit).offset(
        pagination.offset
    )

    rows = (await db.execute(query)).all()
    total = (await db.execute(count_query)).scalar_one()
    items = [
        RegistrationRead(
            payment_id=payment.id if payment is not None else None,
            user_id=user.id,
            user_name=f"{user.first_name} {user.last_name}",
            user_email=user.email,
            pass_type_name=pass_type.name if pass_type is not None else None,
            amount_paid=payment.amount_paid if payment is not None else None,
            status=payment.status if payment is not None else "registered",
            ticket_number=ticket_number,
            created_at=user.created_at,
        )
        for user, payment, pass_type, ticket_number in rows
    ]
    return RegistrationListRead(items=items, total=total)
