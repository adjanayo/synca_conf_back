from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.pagination import Pagination, pagination_params
from app.deps.rbac import require_permission
from app.models import Ambassador, Exhibitor, Partner, Speaker
from app.schemas.admin_applications import (
    AmbassadorStatusUpdate,
    ExhibitorStatusUpdate,
    PartnerStatusUpdate,
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
