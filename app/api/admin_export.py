import csv
import io

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.rbac import require_permission
from app.models import PassType, Payment, Ticket, User

router = APIRouter(prefix="/api/admin/export", tags=["admin-export"])


def _csv_response(rows: list[list[str]], header: list[str], filename: str) -> Response:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    writer.writerows(rows)

    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/registrations")
@limiter.limit("30/minute")
async def export_registrations_csv(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("export.data")),
) -> Response:
    query = (
        select(Payment, User, PassType, Ticket.ticket_number)
        .join(User, User.id == Payment.user_id)
        .join(PassType, PassType.id == Payment.pass_type_id)
        .outerjoin(Ticket, Ticket.payment_id == Payment.id)
        .order_by(Payment.created_at)
    )
    rows = (await db.execute(query)).all()

    csv_rows = [
        [
            str(payment.id),
            f"{user.first_name} {user.last_name}",
            user.email,
            pass_type.name,
            str(payment.amount_paid),
            payment.status,
            ticket_number or "",
            payment.created_at.isoformat(),
        ]
        for payment, user, pass_type, ticket_number in rows
    ]
    header = [
        "payment_id",
        "user_name",
        "user_email",
        "pass_type_name",
        "amount_paid",
        "status",
        "ticket_number",
        "created_at",
    ]
    return _csv_response(csv_rows, header, "registrations.csv")


@router.get("/payments")
@limiter.limit("30/minute")
async def export_payments_csv(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("export.data")),
) -> Response:
    query = select(Payment).order_by(Payment.created_at)
    payments = (await db.execute(query)).scalars().all()

    csv_rows = [
        [
            str(payment.id),
            str(payment.user_id),
            str(payment.pass_type_id),
            str(payment.promo_code_id or ""),
            str(payment.amount_original),
            str(payment.amount_paid),
            payment.currency,
            payment.payment_method,
            payment.transaction_ref or "",
            payment.status,
            payment.paid_at.isoformat() if payment.paid_at else "",
            payment.created_at.isoformat(),
        ]
        for payment in payments
    ]
    header = [
        "payment_id",
        "user_id",
        "pass_type_id",
        "promo_code_id",
        "amount_original",
        "amount_paid",
        "currency",
        "payment_method",
        "transaction_ref",
        "status",
        "paid_at",
        "created_at",
    ]
    return _csv_response(csv_rows, header, "payments.csv")
