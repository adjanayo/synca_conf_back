from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
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
