from typing import Literal

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.pagination import Pagination, pagination_params
from app.deps.rbac import require_permission
from app.models import PassType, Payment, Ticket, User
from app.models.payments import PAYMENT_STATUS_VALUES
from app.schemas.admin_registrations import RegistrationRead

router = APIRouter(prefix="/api/admin", tags=["admin-registrations"])


@router.get("/registrations", response_model=list[RegistrationRead])
@limiter.limit("30/minute")
async def list_registrations(
    request: Request,
    payment_status: Literal[*PAYMENT_STATUS_VALUES] | None = None,
    pagination: Pagination = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("payments.view")),
) -> list[RegistrationRead]:
    query = (
        select(Payment, User, PassType, Ticket.ticket_number)
        .join(User, User.id == Payment.user_id)
        .join(PassType, PassType.id == Payment.pass_type_id)
        .outerjoin(Ticket, Ticket.payment_id == Payment.id)
        .order_by(Payment.created_at.desc())
        .limit(pagination.limit)
        .offset(pagination.offset)
    )
    if payment_status is not None:
        query = query.where(Payment.status == payment_status)

    rows = (await db.execute(query)).all()
    return [
        RegistrationRead(
            payment_id=payment.id,
            user_id=user.id,
            user_name=f"{user.first_name} {user.last_name}",
            user_email=user.email,
            pass_type_name=pass_type.name,
            amount_paid=payment.amount_paid,
            status=payment.status,
            ticket_number=ticket_number,
            created_at=payment.created_at,
        )
        for payment, user, pass_type, ticket_number in rows
    ]
