from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.deps.rbac import require_permission
from app.models import Ambassador, Exhibitor, Partner, Payment, Speaker, Ticket
from app.schemas.admin_stats import AdminStatsRead

router = APIRouter(prefix="/api/admin", tags=["admin-stats"])

_APPLICATION_MODELS = {
    "speakers": Speaker,
    "ambassadors": Ambassador,
    "partners": Partner,
    "exhibitors": Exhibitor,
}


@router.get("/stats", response_model=AdminStatsRead)
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    # Revenue is the most sensitive figure on this dashboard -- reuse the
    # existing payments.view code rather than inventing a new one for a
    # single read-only endpoint.
    _admin=Depends(require_permission("payments.view")),
) -> AdminStatsRead:
    total_registrations = (await db.execute(select(func.count(Ticket.id)))).scalar_one()

    total_revenue = (
        await db.execute(
            select(func.coalesce(func.sum(Payment.amount_paid), 0)).where(
                Payment.status == "completed"
            )
        )
    ).scalar_one()
    completed_payments = (
        await db.execute(
            select(func.count(Payment.id)).where(Payment.status == "completed")
        )
    ).scalar_one()
    payments_with_promo = (
        await db.execute(
            select(func.count(Payment.id)).where(
                Payment.status == "completed", Payment.promo_code_id.is_not(None)
            )
        )
    ).scalar_one()
    promo_conversion_rate = (
        round(payments_with_promo / completed_payments, 4) if completed_payments else 0.0
    )

    applications_by_status: dict[str, dict[str, int]] = {}
    for name, model in _APPLICATION_MODELS.items():
        rows = (
            await db.execute(select(model.status, func.count()).group_by(model.status))
        ).all()
        applications_by_status[name] = {status: count for status, count in rows}

    return AdminStatsRead(
        total_registrations=total_registrations,
        total_revenue=total_revenue,
        completed_payments=completed_payments,
        payments_with_promo=payments_with_promo,
        promo_conversion_rate=promo_conversion_rate,
        applications_by_status=applications_by_status,
    )
