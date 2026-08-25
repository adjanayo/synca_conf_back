import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Day, FaqCategory, PartnerLevel, PassType


@pytest.mark.asyncio
async def test_day_unique_date(db_session):
    db_session.add(Day(date=datetime.date(2027, 8, 18), label="Jour 1"))
    await db_session.commit()

    db_session.add(Day(date=datetime.date(2027, 8, 18), label="Doublon"))
    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_pass_type_defaults(db_session):
    pass_type = PassType(name="Standard", price=15000)
    db_session.add(pass_type)
    await db_session.commit()

    assert pass_type.max_days == 3
    assert pass_type.is_active is True


@pytest.mark.asyncio
async def test_partner_level_and_faq_category(db_session):
    db_session.add(PartnerLevel(name="Gold", price=500000))
    db_session.add(FaqCategory(name="Billetterie"))
    await db_session.commit()
