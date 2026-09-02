from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.rbac import require_permission
from app.models.payments import PromoCode
from app.schemas.payments import PromoCodeCreate, PromoCodeRead, PromoCodeUpdate

router = APIRouter(prefix="/api/admin/promo-codes", tags=["admin-promo-codes"])


@router.get("", response_model=list[PromoCodeRead])
@limiter.limit("30/minute")
async def list_promo_codes(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("promo_codes.manage")),
) -> list[PromoCodeRead]:
    promo_codes = (
        await db.execute(select(PromoCode).order_by(PromoCode.created_at.desc()))
    ).scalars().all()
    return [PromoCodeRead.model_validate(promo) for promo in promo_codes]


@router.post("", response_model=PromoCodeRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_promo_code(
    request: Request,
    body: PromoCodeCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("promo_codes.manage")),
) -> PromoCodeRead:
    existing = (
        await db.execute(select(PromoCode).where(PromoCode.code == body.code))
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce code promo existe déjà.",
        )

    promo_code = PromoCode(
        code=body.code,
        discount_pct=body.discount_pct,
        discount_fixed=body.discount_fixed,
        usage_limit=body.usage_limit,
        valid_from=body.valid_from,
        valid_until=body.valid_until,
        is_active=body.is_active,
    )
    db.add(promo_code)
    await db.commit()
    await db.refresh(promo_code)
    return PromoCodeRead.model_validate(promo_code)


@router.patch("/{promo_code_id}", response_model=PromoCodeRead)
@limiter.limit("30/minute")
async def update_promo_code(
    request: Request,
    promo_code_id: int,
    body: PromoCodeUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("promo_codes.manage")),
) -> PromoCodeRead:
    promo_code = await db.get(PromoCode, promo_code_id)
    if promo_code is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Code promo introuvable."
        )

    if body.discount_pct is not None:
        promo_code.discount_pct = body.discount_pct
    if body.discount_fixed is not None:
        promo_code.discount_fixed = body.discount_fixed
    if body.usage_limit is not None:
        promo_code.usage_limit = body.usage_limit
    if body.valid_from is not None:
        promo_code.valid_from = body.valid_from
    if body.valid_until is not None:
        promo_code.valid_until = body.valid_until
    if body.is_active is not None:
        promo_code.is_active = body.is_active

    await db.commit()
    await db.refresh(promo_code)
    return PromoCodeRead.model_validate(promo_code)
