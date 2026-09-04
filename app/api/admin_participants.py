from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.rbac import require_permission
from app.models.users import User
from app.schemas.participants import ParticipantCreate, ParticipantRead

router = APIRouter(prefix="/api/admin/participants", tags=["admin-participants"])


@router.get("", response_model=list[ParticipantRead])
@limiter.limit("30/minute")
async def search_participants(
    request: Request,
    q: str | None = None,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("participants.manage")),
) -> list[ParticipantRead]:
    query = select(User).order_by(User.first_name, User.last_name).limit(20)
    if q:
        like = f"%{q}%"
        query = query.where(
            or_(User.first_name.ilike(like), User.last_name.ilike(like), User.email.ilike(like))
        )
    users = (await db.execute(query)).scalars().all()
    return [ParticipantRead.model_validate(user) for user in users]


@router.post("", response_model=ParticipantRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_participant(
    request: Request,
    body: ParticipantCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("participants.manage")),
) -> ParticipantRead:
    existing = (
        await db.execute(select(User).where(User.email == body.email))
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte participant existe déjà avec cet email.",
        )

    user = User(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        phone_whatsapp=body.phone_whatsapp,
        country=body.country,
        city=body.city,
        gdpr_consent=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return ParticipantRead.model_validate(user)
