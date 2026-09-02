from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.pagination import Pagination, pagination_params
from app.deps.rbac import get_current_admin
from app.models import ContactMessage
from app.schemas.content import ContactMessageRead, ContactMessageUpdate

router = APIRouter(prefix="/api/admin", tags=["admin-contacts"])


@router.get("/contacts", response_model=list[ContactMessageRead])
@limiter.limit("30/minute")
async def list_contacts(
    request: Request,
    is_read: bool | None = None,
    pagination: Pagination = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
    # No dedicated RBAC code for contact messages (same call as 6.1's
    # ContactMessageAdmin) -- informational, not a workflow to gate, so any
    # authenticated admin may read it.
    _admin=Depends(get_current_admin),
) -> list[ContactMessageRead]:
    query = select(ContactMessage).order_by(ContactMessage.created_at.desc())
    if is_read is not None:
        query = query.where(ContactMessage.is_read == is_read)
    query = query.limit(pagination.limit).offset(pagination.offset)

    messages = (await db.execute(query)).scalars().all()
    return [ContactMessageRead.model_validate(message) for message in messages]


@router.patch("/contacts/{contact_id}", response_model=ContactMessageRead)
@limiter.limit("30/minute")
async def update_contact_read_status(
    request: Request,
    contact_id: int,
    body: ContactMessageUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ContactMessageRead:
    message = await db.get(ContactMessage, contact_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message de contact introuvable.")
    message.is_read = body.is_read
    await db.commit()
    await db.refresh(message)
    return ContactMessageRead.model_validate(message)
