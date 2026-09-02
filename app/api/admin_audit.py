from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.pagination import Pagination, pagination_params
from app.deps.rbac import get_current_admin
from app.models import AuditLog
from app.schemas.audit import AuditLogRead

router = APIRouter(prefix="/api/admin", tags=["admin-audit"])


@router.get("/audit-logs", response_model=list[AuditLogRead])
@limiter.limit("30/minute")
async def list_audit_logs(
    request: Request,
    event: str | None = None,
    email: str | None = None,
    success: bool | None = None,
    pagination: Pagination = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
    # No dedicated RBAC code for audit logs (same as contacts) -- informational,
    # not a workflow to gate, so any authenticated admin may read it.
    _admin=Depends(get_current_admin),
) -> list[AuditLogRead]:
    query = select(AuditLog).order_by(AuditLog.created_at.desc())
    if event is not None:
        query = query.where(AuditLog.event == event)
    if email is not None:
        query = query.where(AuditLog.email == email)
    if success is not None:
        query = query.where(AuditLog.success == success)
    query = query.limit(pagination.limit).offset(pagination.offset)

    logs = (await db.execute(query)).scalars().all()
    return [AuditLogRead.model_validate(log) for log in logs]
