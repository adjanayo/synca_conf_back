from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.rbac import require_permission
from app.models.applications import Partner
from app.models.referentials import PartnerLevel
from app.schemas.referentials import PartnerLevelCreate, PartnerLevelRead, PartnerLevelUpdate

router = APIRouter(prefix="/api/admin/partner-levels", tags=["admin-partner-levels"])


@router.get("", response_model=list[PartnerLevelRead])
@limiter.limit("30/minute")
async def list_partner_levels_admin(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("partner_levels.manage")),
) -> list[PartnerLevelRead]:
    levels = (
        await db.execute(select(PartnerLevel).order_by(PartnerLevel.sort_order))
    ).scalars().all()
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

    level = PartnerLevel(
        name=body.name, price=body.price, benefits=body.benefits, sort_order=body.sort_order
    )
    db.add(level)
    await db.commit()
    await db.refresh(level)
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
    level = await db.get(PartnerLevel, level_id)
    if level is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Palier introuvable.")

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
    if body.benefits is not None:
        level.benefits = body.benefits
    if body.sort_order is not None:
        level.sort_order = body.sort_order

    await db.commit()
    await db.refresh(level)
    return PartnerLevelRead.model_validate(level)


@router.delete("/{level_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
async def delete_partner_level(
    request: Request,
    level_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("partner_levels.manage")),
) -> None:
    level = await db.get(PartnerLevel, level_id)
    if level is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Palier introuvable.")

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
