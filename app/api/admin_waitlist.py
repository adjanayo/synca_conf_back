from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.pagination import Pagination, pagination_params
from app.deps.rbac import require_permission
from app.models import Waitlist
from app.schemas.payments import WaitlistRead

router = APIRouter(prefix="/api/admin", tags=["admin-waitlist"])


@router.get("/waitlist", response_model=list[WaitlistRead])
@limiter.limit("30/minute")
async def list_waitlist(
    request: Request,
    notified: bool | None = None,
    registered: bool | None = None,
    pagination: Pagination = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("waitlist.view")),
) -> list[WaitlistRead]:
    query = select(Waitlist)
    if notified is not None:
        query = query.where(Waitlist.notified == notified)
    if registered is not None:
        query = query.where(Waitlist.registered == registered)
    query = query.order_by(Waitlist.created_at.desc()).limit(pagination.limit).offset(
        pagination.offset
    )

    entries = (await db.execute(query)).scalars().all()
    return [WaitlistRead.model_validate(entry) for entry in entries]
