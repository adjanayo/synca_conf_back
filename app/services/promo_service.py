import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PromoCode


async def get_valid_promo_code(db: AsyncSession, code: str) -> PromoCode | None:
    promo = (
        await db.execute(select(PromoCode).where(PromoCode.code == code))
    ).scalar_one_or_none()

    today = datetime.date.today()
    is_valid = (
        promo is not None
        and promo.is_active
        and (promo.valid_from is None or promo.valid_from <= today)
        and (promo.valid_until is None or promo.valid_until >= today)
        and (promo.usage_limit is None or promo.usage_count < promo.usage_limit)
    )
    return promo if is_valid else None


def compute_discounted_amount(original_amount: int, promo: PromoCode) -> int:
    if promo.discount_fixed is not None:
        return max(0, original_amount - promo.discount_fixed)
    return round(original_amount * (1 - promo.discount_pct / 100))
