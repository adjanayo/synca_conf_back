from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.pagination import Pagination, pagination_params
from app.deps.rbac import require_permission
from app.models import Ambassador, Exhibitor, Partner, PartnerLevel, Speaker
from app.schemas.admin_applications import (
    AmbassadorAdminCreate,
    AmbassadorStatusUpdate,
    ExhibitorAdminCreate,
    ExhibitorStatusUpdate,
    PartnerAdminCreate,
    PartnerStatusUpdate,
    SpeakerAdminCreate,
    SpeakerStatusUpdate,
)
from app.schemas.applications import (
    AmbassadorRead,
    ExhibitorRead,
    PartnerRead,
    SpeakerRead,
)
from app.services.promo_service import generate_ambassador_promo_code

router = APIRouter(prefix="/api/admin", tags=["admin-applications"])


@router.get("/speakers", response_model=list[SpeakerRead])
@limiter.limit("30/minute")
async def list_speakers(
    request: Request,
    status: str | None = None,
    theme: str | None = None,
    format: str | None = None,
    pagination: Pagination = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("speakers.approve")),
) -> list[SpeakerRead]:
    # Unlike the public /api/speakers route, this one is not filtered on
    # is_public -- moderation needs to see pending/rejected candidates too.
    query = select(Speaker)
    if status is not None:
        query = query.where(Speaker.status == status)
    if theme is not None:
        query = query.where(Speaker.theme == theme)
    if format is not None:
        query = query.where(Speaker.intervention_format == format)
    query = query.order_by(Speaker.created_at.desc()).limit(pagination.limit).offset(
        pagination.offset
    )

    speakers = (await db.execute(query)).scalars().all()
    return [SpeakerRead.model_validate(speaker) for speaker in speakers]


@router.post("/speakers", response_model=SpeakerRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_speaker_admin(
    request: Request,
    body: SpeakerAdminCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("speakers.approve")),
) -> SpeakerRead:
    # Same is_public-on-acceptance rule as the PATCH route above -- a
    # direct-create with status="accepted" must publish immediately too.
    is_public = True if body.status == "accepted" else body.is_public

    speaker = Speaker(
        first_name=body.first_name,
        last_name=body.last_name,
        title_role=body.title_role,
        company=body.company,
        country=body.country,
        email=body.email,
        phone_whatsapp=body.phone_whatsapp,
        linkedin_url=body.linkedin_url,
        website_url=body.website_url,
        photo_url=body.photo_url,
        intervention_format=body.intervention_format,
        intervention_title=body.intervention_title,
        theme=body.theme,
        summary=body.summary,
        audience_level=body.audience_level,
        language=body.language,
        past_experience=body.past_experience,
        video_link=body.video_link,
        availability=body.availability,
        departure_city=body.departure_city,
        needs_accommodation=body.needs_accommodation,
        motivation=body.motivation,
        video_consent=body.video_consent,
        gdpr_consent=body.gdpr_consent,
        status=body.status,
        is_public=is_public,
    )
    db.add(speaker)
    await db.commit()
    await db.refresh(speaker)
    return SpeakerRead.model_validate(speaker)


@router.patch("/speakers/{speaker_id}", response_model=SpeakerRead)
@limiter.limit("30/minute")
async def update_speaker_status(
    request: Request,
    speaker_id: int,
    body: SpeakerStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("speakers.approve")),
) -> SpeakerRead:
    speaker = await db.get(Speaker, speaker_id)
    if speaker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Speaker introuvable.")

    speaker.status = body.status
    # Publishing to the public speakers list (3.3) is a direct consequence
    # of acceptance -- there's no separate publish step in the roadmap.
    speaker.is_public = body.status == "accepted"
    await db.commit()
    await db.refresh(speaker)
    return SpeakerRead.model_validate(speaker)


@router.get("/ambassadors", response_model=list[AmbassadorRead])
@limiter.limit("30/minute")
async def list_ambassadors(
    request: Request,
    status: str | None = None,
    current_profile: str | None = None,
    pagination: Pagination = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("ambassadors.approve")),
) -> list[AmbassadorRead]:
    query = select(Ambassador)
    if status is not None:
        query = query.where(Ambassador.status == status)
    if current_profile is not None:
        query = query.where(Ambassador.current_profile == current_profile)
    query = query.order_by(Ambassador.created_at.desc()).limit(pagination.limit).offset(
        pagination.offset
    )

    ambassadors = (await db.execute(query)).scalars().all()
    return [AmbassadorRead.model_validate(ambassador) for ambassador in ambassadors]


@router.post("/ambassadors", response_model=AmbassadorRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_ambassador_admin(
    request: Request,
    body: AmbassadorAdminCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("ambassadors.approve")),
) -> AmbassadorRead:
    ambassador = Ambassador(
        first_name=body.first_name,
        last_name=body.last_name,
        age=body.age,
        country=body.country,
        city=body.city,
        email=body.email,
        phone_whatsapp=body.phone_whatsapp,
        current_profile=body.current_profile,
        institution_company=body.institution_company,
        linkedin_url=body.linkedin_url,
        social_handles=body.social_handles,
        followers_range=body.followers_range,
        motivation=body.motivation,
        mobilization_plan=body.mobilization_plan,
        estimated_reach=body.estimated_reach,
        previous_synca=body.previous_synca,
        preferred_channels=body.preferred_channels,
        availability_pre=body.availability_pre,
        gdpr_consent=body.gdpr_consent,
        status=body.status,
    )
    db.add(ambassador)
    await db.flush()
    # Same auto-promo-code rule as the PATCH route below.
    if body.status == "accepted" and ambassador.promo_code_id is None:
        await generate_ambassador_promo_code(db, ambassador)
    await db.commit()
    await db.refresh(ambassador)
    return AmbassadorRead.model_validate(ambassador)


@router.patch("/ambassadors/{ambassador_id}", response_model=AmbassadorRead)
@limiter.limit("30/minute")
async def update_ambassador_status(
    request: Request,
    ambassador_id: int,
    body: AmbassadorStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("ambassadors.approve")),
) -> AmbassadorRead:
    ambassador = await db.get(Ambassador, ambassador_id)
    if ambassador is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ambassadeur introuvable."
        )

    ambassador.status = body.status
    if body.status == "accepted" and ambassador.promo_code_id is None:
        await generate_ambassador_promo_code(db, ambassador)
    await db.commit()
    await db.refresh(ambassador)
    return AmbassadorRead.model_validate(ambassador)


@router.get("/partners", response_model=list[PartnerRead])
@limiter.limit("30/minute")
async def list_partners(
    request: Request,
    status: str | None = None,
    level_id: int | None = None,
    pagination: Pagination = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("partners.manage")),
) -> list[PartnerRead]:
    query = select(Partner)
    if status is not None:
        query = query.where(Partner.status == status)
    if level_id is not None:
        query = query.where(Partner.level_id == level_id)
    query = query.order_by(Partner.created_at.desc()).limit(pagination.limit).offset(
        pagination.offset
    )

    partners = (await db.execute(query)).scalars().all()
    return [PartnerRead.model_validate(partner) for partner in partners]


@router.post("/partners", response_model=PartnerRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_partner_admin(
    request: Request,
    body: PartnerAdminCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("partners.manage")),
) -> PartnerRead:
    level = await db.get(PartnerLevel, body.level_id)
    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Palier de partenariat introuvable."
        )

    # Same is_public-on-confirmation rule as the PATCH route below.
    is_public = True if body.status == "confirmed" else body.is_public

    partner = Partner(
        organization_name=body.organization_name,
        sector=body.sector,
        country=body.country,
        city=body.city,
        website_url=body.website_url,
        contact_name=body.contact_name,
        contact_position=body.contact_position,
        contact_email=body.contact_email,
        contact_phone=body.contact_phone,
        level_id=body.level_id,
        has_budget=body.has_budget,
        objectives=body.objectives,
        previous_sponsor=body.previous_sponsor,
        message=body.message,
        heard_from=body.heard_from,
        gdpr_consent=body.gdpr_consent,
        status=body.status,
        logo_url=body.logo_url,
        is_public=is_public,
    )
    db.add(partner)
    await db.commit()
    await db.refresh(partner)
    return PartnerRead.model_validate(partner)


@router.patch("/partners/{partner_id}", response_model=PartnerRead)
@limiter.limit("30/minute")
async def update_partner_status(
    request: Request,
    partner_id: int,
    body: PartnerStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("partners.manage")),
) -> PartnerRead:
    partner = await db.get(Partner, partner_id)
    if partner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partenaire introuvable.")

    partner.status = body.status
    partner.is_public = body.status == "confirmed"
    await db.commit()
    await db.refresh(partner)
    return PartnerRead.model_validate(partner)


@router.get("/exhibitors", response_model=list[ExhibitorRead])
@limiter.limit("30/minute")
async def list_exhibitors(
    request: Request,
    status: str | None = None,
    stand_type: str | None = None,
    pagination: Pagination = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("exhibitors.manage")),
) -> list[ExhibitorRead]:
    query = select(Exhibitor)
    if status is not None:
        query = query.where(Exhibitor.status == status)
    if stand_type is not None:
        query = query.where(Exhibitor.stand_type == stand_type)
    query = query.order_by(Exhibitor.created_at.desc()).limit(pagination.limit).offset(
        pagination.offset
    )

    exhibitors = (await db.execute(query)).scalars().all()
    return [ExhibitorRead.model_validate(exhibitor) for exhibitor in exhibitors]


@router.post("/exhibitors", response_model=ExhibitorRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_exhibitor_admin(
    request: Request,
    body: ExhibitorAdminCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("exhibitors.manage")),
) -> ExhibitorRead:
    # Same is_public-on-confirmation rule as the PATCH route below.
    is_public = True if body.status == "confirmed" else body.is_public

    exhibitor = Exhibitor(
        organization_name=body.organization_name,
        sector=body.sector,
        country=body.country,
        city=body.city,
        website_url=body.website_url,
        contact_name=body.contact_name,
        contact_position=body.contact_position,
        contact_email=body.contact_email,
        contact_phone=body.contact_phone,
        stand_type=body.stand_type,
        reps_count=body.reps_count,
        linked_partner_level=body.linked_partner_level,
        products_services=body.products_services,
        equipment_needs=body.equipment_needs,
        side_activities=body.side_activities,
        visuals_url=body.visuals_url,
        payment_method=body.payment_method,
        rules_accepted=body.rules_accepted,
        gdpr_consent=body.gdpr_consent,
        status=body.status,
        is_public=is_public,
    )
    db.add(exhibitor)
    await db.commit()
    await db.refresh(exhibitor)
    return ExhibitorRead.model_validate(exhibitor)


@router.patch("/exhibitors/{exhibitor_id}", response_model=ExhibitorRead)
@limiter.limit("30/minute")
async def update_exhibitor_status(
    request: Request,
    exhibitor_id: int,
    body: ExhibitorStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("exhibitors.manage")),
) -> ExhibitorRead:
    exhibitor = await db.get(Exhibitor, exhibitor_id)
    if exhibitor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exposant introuvable.")

    exhibitor.status = body.status
    exhibitor.is_public = body.status == "confirmed"
    await db.commit()
    await db.refresh(exhibitor)
    return ExhibitorRead.model_validate(exhibitor)
