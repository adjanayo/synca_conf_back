from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.deps.pagination import Pagination, pagination_params
from app.models import Day, Exhibitor, Partner, PassType, Session, Speaker
from app.schemas import DayRead, ExhibitorRead, PartnerRead, PassTypeRead, SessionRead, SpeakerRead

router = APIRouter(prefix="/api", tags=["public"])


@router.get("/days", response_model=list[DayRead])
async def list_days(db: AsyncSession = Depends(get_db)) -> list[DayRead]:
    days = (await db.execute(select(Day).order_by(Day.date))).scalars().all()
    return [DayRead.model_validate(day) for day in days]


@router.get("/sessions", response_model=list[SessionRead])
async def list_sessions(
    day: int | None = None,
    category: str | None = None,
    pagination: Pagination = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> list[SessionRead]:
    query = select(Session).where(Session.is_public.is_(True))
    if day is not None:
        query = query.where(Session.day_id == day)
    if category is not None:
        query = query.where(Session.category == category)
    query = query.order_by(Session.day_id, Session.start_time).limit(pagination.limit).offset(
        pagination.offset
    )

    sessions = (await db.execute(query)).scalars().all()
    return [SessionRead.model_validate(session) for session in sessions]


@router.get("/pass-types", response_model=list[PassTypeRead])
async def list_pass_types(db: AsyncSession = Depends(get_db)) -> list[PassTypeRead]:
    query = select(PassType).where(PassType.is_active.is_(True)).order_by(PassType.price)
    pass_types = (await db.execute(query)).scalars().all()
    return [PassTypeRead.model_validate(pass_type) for pass_type in pass_types]


@router.get("/speakers", response_model=list[SpeakerRead])
async def list_speakers(
    theme: str | None = None,
    format: str | None = None,
    pagination: Pagination = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> list[SpeakerRead]:
    query = select(Speaker).where(Speaker.is_public.is_(True))
    if theme is not None:
        query = query.where(Speaker.theme == theme)
    if format is not None:
        query = query.where(Speaker.intervention_format == format)
    query = query.order_by(Speaker.last_name).limit(pagination.limit).offset(pagination.offset)

    speakers = (await db.execute(query)).scalars().all()
    return [SpeakerRead.model_validate(speaker) for speaker in speakers]


@router.get("/partners", response_model=list[PartnerRead])
async def list_partners(
    level: int | None = None,
    pagination: Pagination = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> list[PartnerRead]:
    query = select(Partner).where(Partner.is_public.is_(True))
    if level is not None:
        query = query.where(Partner.level_id == level)
    query = query.order_by(Partner.organization_name).limit(pagination.limit).offset(
        pagination.offset
    )

    partners = (await db.execute(query)).scalars().all()
    return [PartnerRead.model_validate(partner) for partner in partners]


@router.get("/exhibitors", response_model=list[ExhibitorRead])
async def list_exhibitors(
    pagination: Pagination = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> list[ExhibitorRead]:
    # `public=true` per schema.md's endpoint recap is the only mode this
    # endpoint supports -- is_public=true is enforced unconditionally,
    # there's no "show private exhibitors" toggle on a public endpoint.
    query = (
        select(Exhibitor)
        .where(Exhibitor.is_public.is_(True))
        .order_by(Exhibitor.organization_name)
        .limit(pagination.limit)
        .offset(pagination.offset)
    )
    exhibitors = (await db.execute(query)).scalars().all()
    return [ExhibitorRead.model_validate(exhibitor) for exhibitor in exhibitors]
