import datetime

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.main import app
from app.models import Day, Session


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_days_ordered(db_session, client):
    db_session.add_all(
        [
            Day(date=datetime.date(2027, 8, 19), label="Jour 2"),
            Day(date=datetime.date(2027, 8, 18), label="Jour 1"),
        ]
    )
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get("/api/days")

    assert response.status_code == 200
    labels = [d["label"] for d in response.json()]
    assert labels == ["Jour 1", "Jour 2"]


@pytest.mark.asyncio
async def test_list_days_empty(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get("/api/days")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_sessions_filter_by_day_and_category_excludes_private(db_session, client):
    day = Day(date=datetime.date(2027, 8, 18), label="Jour 1")
    db_session.add(day)
    await db_session.flush()

    db_session.add_all(
        [
            Session(
                day_id=day.id, title="Public Workshop", category="workshop",
                start_time=datetime.time(9, 0), end_time=datetime.time(10, 0), is_public=True,
            ),
            Session(
                day_id=day.id, title="Private Workshop", category="workshop",
                start_time=datetime.time(11, 0), end_time=datetime.time(12, 0), is_public=False,
            ),
            Session(
                day_id=day.id, title="Public Keynote", category="keynote",
                start_time=datetime.time(13, 0), end_time=datetime.time(14, 0), is_public=True,
            ),
        ]
    )
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(f"/api/sessions?day={day.id}&category=workshop")

    assert response.status_code == 200
    titles = [s["title"] for s in response.json()]
    assert titles == ["Public Workshop"]


@pytest.mark.asyncio
async def test_sessions_empty_result(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get("/api/sessions?day=999999")

    assert response.status_code == 200
    assert response.json() == []
