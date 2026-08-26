import datetime

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.deps.campaign_windows import require_open_campaign
from app.models import CampaignWindow


async def set_window(db_session, key: str, start_at, end_at, is_active: bool) -> None:
    # campaign_windows is seeded (1.8) with one row per valid key already,
    # so tests update the existing row rather than inserting a duplicate.
    window = (
        await db_session.execute(select(CampaignWindow).where(CampaignWindow.key == key))
    ).scalar_one()
    window.start_at = start_at
    window.end_at = end_at
    window.is_active = is_active
    await db_session.commit()


@pytest.mark.asyncio
async def test_open_window_allows(db_session):
    now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    await set_window(
        db_session,
        "call_for_speaker",
        now - datetime.timedelta(days=1),
        now + datetime.timedelta(days=1),
        True,
    )

    checker = require_open_campaign("call_for_speaker")
    await checker(db=db_session)  # should not raise


@pytest.mark.asyncio
async def test_window_not_yet_started_forbidden(db_session):
    now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    await set_window(
        db_session,
        "call_for_partner",
        now + datetime.timedelta(days=1),
        now + datetime.timedelta(days=2),
        True,
    )

    checker = require_open_campaign("call_for_partner")
    with pytest.raises(HTTPException) as exc_info:
        await checker(db=db_session)
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_window_already_closed_forbidden(db_session):
    now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    await set_window(
        db_session,
        "call_for_ambassador",
        now - datetime.timedelta(days=2),
        now - datetime.timedelta(days=1),
        True,
    )

    checker = require_open_campaign("call_for_ambassador")
    with pytest.raises(HTTPException) as exc_info:
        await checker(db=db_session)
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_window_deactivated_forbidden_even_within_dates(db_session):
    now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    await set_window(
        db_session,
        "call_for_exhibitor",
        now - datetime.timedelta(days=1),
        now + datetime.timedelta(days=1),
        False,
    )

    checker = require_open_campaign("call_for_exhibitor")
    with pytest.raises(HTTPException) as exc_info:
        await checker(db=db_session)
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_missing_window_forbidden(db_session):
    await db_session.execute(
        CampaignWindow.__table__.delete().where(CampaignWindow.key == "ticketing")
    )
    await db_session.commit()

    checker = require_open_campaign("ticketing")
    with pytest.raises(HTTPException) as exc_info:
        await checker(db=db_session)
    assert exc_info.value.status_code == 403
