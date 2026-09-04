from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.pagination import Pagination, pagination_params
from app.models import (
    Ambassador,
    CampaignWindow,
    Day,
    Exhibitor,
    Faq,
    FaqCategory,
    HackathonTeam,
    Partner,
    PartnerLevel,
    PassType,
    Session,
    Speaker,
)
from app.models.referentials import EventSettings
from app.schemas import (
    AmbassadorPublicRead,
    CampaignWindowRead,
    DayRead,
    ExhibitorPublicRead,
    FaqCategoryRead,
    FaqRead,
    HackathonTeamRead,
    PartnerLevelRead,
    PartnerPublicRead,
    PassTypeRead,
    SessionRead,
    SpeakerPublicRead,
)
from app.schemas.referentials import EventSettingsRead

router = APIRouter(prefix="/api", tags=["public"])

# La ligne singleton est toujours seedée par la migration (id=1), même id que
# côté admin (admin_event_settings.py).
_EVENT_SETTINGS_ID = 1


@router.get("/event-settings", response_model=EventSettingsRead)
@limiter.limit("60/minute")
async def get_event_settings(
    request: Request, db: AsyncSession = Depends(get_db)
) -> EventSettingsRead:
    settings = await db.get(EventSettings, _EVENT_SETTINGS_ID)
    if settings is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paramètres de l'événement introuvables.",
        )
    return EventSettingsRead.model_validate(settings)


@router.get("/days", response_model=list[DayRead])
@limiter.limit("60/minute")
async def list_days(request: Request, db: AsyncSession = Depends(get_db)) -> list[DayRead]:
    days = (await db.execute(select(Day).order_by(Day.date))).scalars().all()
    return [DayRead.model_validate(day) for day in days]


@router.get("/sessions", response_model=list[SessionRead])
@limiter.limit("60/minute")
async def list_sessions(
    request: Request,
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
@limiter.limit("60/minute")
async def list_pass_types(
    request: Request, db: AsyncSession = Depends(get_db)
) -> list[PassTypeRead]:
    query = (
        select(PassType)
        .where(PassType.is_active.is_(True))
        .order_by(PassType.price)
        .options(selectinload(PassType.contents))
    )
    pass_types = (await db.execute(query)).scalars().all()
    return [PassTypeRead.model_validate(pass_type) for pass_type in pass_types]


@router.get("/speakers", response_model=list[SpeakerPublicRead])
@limiter.limit("60/minute")
async def list_speakers(
    request: Request,
    theme: str | None = None,
    format: str | None = None,
    pagination: Pagination = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> list[SpeakerPublicRead]:
    query = select(Speaker).where(Speaker.is_public.is_(True))
    if theme is not None:
        query = query.where(Speaker.theme == theme)
    if format is not None:
        query = query.where(Speaker.intervention_format == format)
    query = query.order_by(Speaker.last_name).limit(pagination.limit).offset(pagination.offset)

    speakers = (await db.execute(query)).scalars().all()
    return [SpeakerPublicRead.model_validate(speaker) for speaker in speakers]


@router.get("/speakers/{speaker_id}", response_model=SpeakerPublicRead)
@limiter.limit("60/minute")
async def get_speaker(
    request: Request, speaker_id: int, db: AsyncSession = Depends(get_db)
) -> SpeakerPublicRead:
    speaker = await db.get(Speaker, speaker_id)
    if speaker is None or not speaker.is_public:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Speaker introuvable.")
    return SpeakerPublicRead.model_validate(speaker)


@router.get("/ambassadors", response_model=list[AmbassadorPublicRead])
@limiter.limit("60/minute")
async def list_ambassadors(
    request: Request,
    pagination: Pagination = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> list[AmbassadorPublicRead]:
    query = (
        select(Ambassador)
        .where(Ambassador.is_public.is_(True))
        .order_by(Ambassador.last_name)
        .limit(pagination.limit)
        .offset(pagination.offset)
    )
    ambassadors = (await db.execute(query)).scalars().all()
    return [AmbassadorPublicRead.model_validate(ambassador) for ambassador in ambassadors]


@router.get("/ambassadors/{ambassador_id}", response_model=AmbassadorPublicRead)
@limiter.limit("60/minute")
async def get_ambassador(
    request: Request, ambassador_id: int, db: AsyncSession = Depends(get_db)
) -> AmbassadorPublicRead:
    ambassador = await db.get(Ambassador, ambassador_id)
    if ambassador is None or not ambassador.is_public:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ambassadeur introuvable."
        )
    return AmbassadorPublicRead.model_validate(ambassador)


@router.get("/partner-levels", response_model=list[PartnerLevelRead])
@limiter.limit("60/minute")
async def list_partner_levels(
    request: Request, db: AsyncSession = Depends(get_db)
) -> list[PartnerLevelRead]:
    query = (
        select(PartnerLevel)
        .order_by(PartnerLevel.sort_order)
        .options(selectinload(PartnerLevel.benefits))
    )
    levels = (await db.execute(query)).scalars().all()
    return [PartnerLevelRead.model_validate(level) for level in levels]


@router.get("/partners", response_model=list[PartnerPublicRead])
@limiter.limit("60/minute")
async def list_partners(
    request: Request,
    level: int | None = None,
    pagination: Pagination = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> list[PartnerPublicRead]:
    query = select(Partner).where(Partner.is_public.is_(True))
    if level is not None:
        query = query.where(Partner.level_id == level)
    query = query.order_by(Partner.organization_name).limit(pagination.limit).offset(
        pagination.offset
    )

    partners = (await db.execute(query)).scalars().all()
    return [PartnerPublicRead.model_validate(partner) for partner in partners]


@router.get("/exhibitors", response_model=list[ExhibitorPublicRead])
@limiter.limit("60/minute")
async def list_exhibitors(
    request: Request,
    pagination: Pagination = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> list[ExhibitorPublicRead]:
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
    return [ExhibitorPublicRead.model_validate(exhibitor) for exhibitor in exhibitors]


@router.get("/faq-categories", response_model=list[FaqCategoryRead])
@limiter.limit("60/minute")
async def list_faq_categories(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> list[FaqCategoryRead]:
    query = select(FaqCategory).order_by(FaqCategory.id)
    categories = (await db.execute(query)).scalars().all()
    return [FaqCategoryRead.model_validate(category) for category in categories]


@router.get("/faqs", response_model=list[FaqRead])
@limiter.limit("60/minute")
async def list_faqs(
    request: Request,
    category: int | None = None,
    pagination: Pagination = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> list[FaqRead]:
    query = select(Faq)
    if category is not None:
        query = query.where(Faq.category_id == category)
    query = query.order_by(Faq.sort_order).limit(pagination.limit).offset(pagination.offset)

    faqs = (await db.execute(query)).scalars().all()
    return [FaqRead.model_validate(faq) for faq in faqs]


@router.get("/campaign-windows", response_model=list[CampaignWindowRead])
@limiter.limit("60/minute")
async def list_campaign_windows(
    request: Request, db: AsyncSession = Depends(get_db)
) -> list[CampaignWindowRead]:
    query = select(CampaignWindow).order_by(CampaignWindow.start_at)
    windows = (await db.execute(query)).scalars().all()
    return [CampaignWindowRead.model_validate(window) for window in windows]


@router.get("/hackathon-teams", response_model=list[HackathonTeamRead])
@limiter.limit("60/minute")
async def list_hackathon_teams(
    request: Request,
    pagination: Pagination = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> list[HackathonTeamRead]:
    query = (
        select(HackathonTeam)
        .options(selectinload(HackathonTeam.members))
        .order_by(HackathonTeam.university_name, HackathonTeam.name)
        .limit(pagination.limit)
        .offset(pagination.offset)
    )
    teams = (await db.execute(query)).scalars().all()
    return [HackathonTeamRead.model_validate(team) for team in teams]
