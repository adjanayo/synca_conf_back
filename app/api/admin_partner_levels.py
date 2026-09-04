from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.rbac import require_permission
from app.models.applications import Partner
from app.models.referentials import PartnerBenefit, PartnerLevel
from app.schemas.referentials import (
    PartnerBenefitCreate,
    PartnerBenefitRead,
    PartnerBenefitUpdate,
    PartnerLevelCreate,
    PartnerLevelRead,
    PartnerLevelUpdate,
)

router = APIRouter(prefix="/api/admin/partner-levels", tags=["admin-partner-levels"])
benefits_router = APIRouter(prefix="/api/admin/partner-benefits", tags=["admin-partner-benefits"])


async def _resolve_benefits(db: AsyncSession, benefit_ids: list[int]) -> list[PartnerBenefit]:
    if not benefit_ids:
        return []
    benefits = (
        (await db.execute(select(PartnerBenefit).where(PartnerBenefit.id.in_(benefit_ids))))
        .scalars()
        .all()
    )
    found_ids = {b.id for b in benefits}
    missing = set(benefit_ids) - found_ids
    if missing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Avantage(s) introuvable(s) : {sorted(missing)}.",
        )
    return benefits


async def _get_level_or_404(db: AsyncSession, level_id: int) -> PartnerLevel:
    level = (
        await db.execute(
            select(PartnerLevel)
            .where(PartnerLevel.id == level_id)
            .options(selectinload(PartnerLevel.benefits))
        )
    ).scalar_one_or_none()
    if level is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Palier introuvable.")
    return level


# --- Partner levels -----------------------------------------------------


@router.get("", response_model=list[PartnerLevelRead])
@limiter.limit("30/minute")
async def list_partner_levels_admin(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("partner_levels.manage")),
) -> list[PartnerLevelRead]:
    levels = (
        (
            await db.execute(
                select(PartnerLevel)
                .order_by(PartnerLevel.sort_order)
                .options(selectinload(PartnerLevel.benefits))
            )
        )
        .scalars()
        .all()
    )
    return [PartnerLevelRead.model_validate(level) for level in levels]


@router.post("", response_model=PartnerLevelRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_partner_level(
    request: Request,
    body: PartnerLevelCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("partner_levels.manage")),
) -> PartnerLevelRead:
    existing = (
        await db.execute(select(PartnerLevel).where(PartnerLevel.name == body.name))
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce palier de partenariat existe déjà.",
        )

    benefits = await _resolve_benefits(db, body.benefit_ids)
    level = PartnerLevel(
        name=body.name, price=body.price, sort_order=body.sort_order, benefits=benefits
    )
    db.add(level)
    await db.commit()
    level = await _get_level_or_404(db, level.id)
    return PartnerLevelRead.model_validate(level)


@router.patch("/{level_id}", response_model=PartnerLevelRead)
@limiter.limit("30/minute")
async def update_partner_level(
    request: Request,
    level_id: int,
    body: PartnerLevelUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("partner_levels.manage")),
) -> PartnerLevelRead:
    level = await _get_level_or_404(db, level_id)

    if body.name is not None and body.name != level.name:
        existing = (
            await db.execute(select(PartnerLevel).where(PartnerLevel.name == body.name))
        ).scalar_one_or_none()
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce palier de partenariat existe déjà.",
            )
        level.name = body.name

    if body.price is not None:
        level.price = body.price
    if body.sort_order is not None:
        level.sort_order = body.sort_order
    if body.benefit_ids is not None:
        level.benefits = await _resolve_benefits(db, body.benefit_ids)

    await db.commit()
    level = await _get_level_or_404(db, level_id)
    return PartnerLevelRead.model_validate(level)


@router.delete("/{level_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
async def delete_partner_level(
    request: Request,
    level_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("partner_levels.manage")),
) -> None:
    level = await _get_level_or_404(db, level_id)

    has_partners = (
        await db.execute(select(Partner.id).where(Partner.level_id == level_id).limit(1))
    ).scalar_one_or_none()
    if has_partners is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de supprimer un palier ayant des partenaires rattachés.",
        )

    await db.delete(level)
    await db.commit()


# --- Partner benefits (catalogue d'avantages) -----------------------------


@benefits_router.get("", response_model=list[PartnerBenefitRead])
@limiter.limit("30/minute")
async def list_partner_benefits_admin(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("partner_levels.manage")),
) -> list[PartnerBenefitRead]:
    benefits = (
        await db.execute(select(PartnerBenefit).order_by(PartnerBenefit.label))
    ).scalars().all()
    return [PartnerBenefitRead.model_validate(b) for b in benefits]


@benefits_router.post("", response_model=PartnerBenefitRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_partner_benefit(
    request: Request,
    body: PartnerBenefitCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("partner_levels.manage")),
) -> PartnerBenefitRead:
    existing = (
        await db.execute(select(PartnerBenefit).where(PartnerBenefit.label == body.label))
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet avantage existe déjà.",
        )

    benefit = PartnerBenefit(label=body.label)
    db.add(benefit)
    await db.commit()
    await db.refresh(benefit)
    return PartnerBenefitRead.model_validate(benefit)


@benefits_router.patch("/{benefit_id}", response_model=PartnerBenefitRead)
@limiter.limit("30/minute")
async def update_partner_benefit(
    request: Request,
    benefit_id: int,
    body: PartnerBenefitUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("partner_levels.manage")),
) -> PartnerBenefitRead:
    benefit = await db.get(PartnerBenefit, benefit_id)
    if benefit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avantage introuvable.")

    if body.label is not None and body.label != benefit.label:
        existing = (
            await db.execute(select(PartnerBenefit).where(PartnerBenefit.label == body.label))
        ).scalar_one_or_none()
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet avantage existe déjà.",
            )
        benefit.label = body.label

    await db.commit()
    await db.refresh(benefit)
    return PartnerBenefitRead.model_validate(benefit)


@benefits_router.delete("/{benefit_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
async def delete_partner_benefit(
    request: Request,
    benefit_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("partner_levels.manage")),
) -> None:
    benefit = await db.get(PartnerBenefit, benefit_id)
    if benefit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avantage introuvable.")

    # Table d'association pure (ondelete=CASCADE des deux côtés) -- retire
    # silencieusement l'avantage des paliers qui l'avaient coché, pas de
    # garde-fou bloquant comme days/sessions (même choix que pass_contents).
    await db.delete(benefit)
    await db.commit()
