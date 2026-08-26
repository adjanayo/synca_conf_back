from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.promo import PromoValidateRequest, PromoValidateResponse
from app.services.promo_service import get_valid_promo_code

router = APIRouter(prefix="/api", tags=["payments"])


@router.post("/promo/validate", response_model=PromoValidateResponse)
async def validate_promo(
    body: PromoValidateRequest, db: AsyncSession = Depends(get_db)
) -> PromoValidateResponse:
    promo = await get_valid_promo_code(db, body.code)
    if promo is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce code promo n'est pas valide.",
        )

    return PromoValidateResponse(
        code=promo.code, discount_pct=promo.discount_pct, discount_fixed=promo.discount_fixed
    )
