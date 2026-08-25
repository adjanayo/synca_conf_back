import datetime

import pytest
from sqlalchemy import select

from app.models import Day, Session


@pytest.mark.asyncio
async def test_filter_sessions_by_day_and_category(db_session):
    day1 = Day(date=datetime.date(2027, 8, 18), label="Jour 1")
    day2 = Day(date=datetime.date(2027, 8, 19), label="Jour 2")
    db_session.add_all([day1, day2])
    await db_session.flush()

    db_session.add_all(
        [
            Session(
                day_id=day1.id,
                title="Keynote ouverture",
                category="keynote",
                start_time=datetime.time(9, 0),
                end_time=datetime.time(10, 0),
            ),
            Session(
                day_id=day1.id,
                title="Atelier IA",
                category="workshop",
                start_time=datetime.time(10, 30),
                end_time=datetime.time(12, 0),
            ),
            Session(
                day_id=day2.id,
                title="Panel Cybersec",
                category="panel",
                start_time=datetime.time(9, 0),
                end_time=datetime.time(10, 0),
            ),
        ]
    )
    await db_session.commit()

    result = await db_session.execute(
        select(Session).where(Session.day_id == day1.id, Session.category == "workshop")
    )
    sessions = result.scalars().all()
    assert [s.title for s in sessions] == ["Atelier IA"]
