import datetime

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError

from app.models import CampaignWindow


@pytest.mark.asyncio
async def test_five_campaign_windows_seeded(db_session):
    keys = (await db_session.execute(select(CampaignWindow.key))).scalars().all()
    assert set(keys) == {
        "call_for_speaker",
        "ticketing",
        "call_for_partner",
        "call_for_ambassador",
        "call_for_exhibitor",
    }
    count = (await db_session.execute(select(func.count(CampaignWindow.id)))).scalar_one()
    assert count == 5


@pytest.mark.asyncio
async def test_end_at_must_be_after_start_at(db_session):
    window = (
        await db_session.execute(
            select(CampaignWindow).where(CampaignWindow.key == "call_for_speaker")
        )
    ).scalar_one()
    window.end_at = window.start_at - datetime.timedelta(days=1)

    with pytest.raises(DBAPIError):
        await db_session.commit()
