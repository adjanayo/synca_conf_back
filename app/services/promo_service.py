import datetime
import re
import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Ambassador, PromoCode

AMBASSADOR_PROMO_DISCOUNT_PCT = 10
_NON_ALNUM = re.compile(r"[^A-Z0-9]")


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


async def generate_ambassador_promo_code(db: AsyncSession, ambassador: Ambassador) -> PromoCode:
    """Create and attach a promo code to a newly-accepted ambassador.

    No usage_limit -- an ambassador's code is meant to be shared widely, not
    capped like a one-off discount (schema.md §"un code promo peut être créé
    ... ou généré automatiquement pour un ambassadeur accepté").
    """
    last_name_slug = _NON_ALNUM.sub("", ambassador.last_name.upper())[:12] or "AMB"

    for _ in range(5):
        code = f"AMB-{last_name_slug}-{secrets.token_hex(2).upper()}"
        collision = (
            await db.execute(select(PromoCode).where(PromoCode.code == code))
        ).scalar_one_or_none()
        if collision is None:
            break
    else:
        raise RuntimeError("Impossible de générer un code promo unique.")

    promo = PromoCode(code=code, discount_pct=AMBASSADOR_PROMO_DISCOUNT_PCT, is_active=True)
    db.add(promo)
    await db.flush()

    ambassador.promo_code_id = promo.id
    return promo
