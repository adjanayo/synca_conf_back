import datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.database import get_db
from app.main import app
from app.models import CampaignWindow


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()


async def open_call_for_exhibitor(db_session) -> None:
    now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    window = (
        await db_session.execute(
            select(CampaignWindow).where(CampaignWindow.key == "call_for_exhibitor")
        )
    ).scalar_one()
    window.start_at = now - datetime.timedelta(days=1)
    window.end_at = now + datetime.timedelta(days=1)
    window.is_active = True
    await db_session.commit()


def payload(**overrides) -> dict:
    data = {
        "organization_name": "Expo Corp",
        "sector": "Tech",
        "country": "Sénégal",
        "city": "Dakar",
        "contact_name": "Awa Fall",
        "contact_position": "Manager",
        "contact_email": "awa@expo.com",
        "contact_phone": "+221774444444",
        "stand_type": "Standard",
        "reps_count": 2,
        "products_services": "Logiciels B2B",
        "rules_accepted": True,
        "gdpr_consent": True,
    }
    data.update(overrides)
    return data


@pytest.mark.asyncio
async def test_exhibitor_apply_closed_window_forbidden(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post("/api/exhibitors/apply", json=payload())

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_exhibitor_apply_success(db_session, client):
    await open_call_for_exhibitor(db_session)

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/exhibitors/apply",
            json=payload(equipment_needs=["Électricité", "Wifi"]),
        )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["is_public"] is False
    assert body["equipment_needs"] == "Électricité, Wifi"


@pytest.mark.asyncio
async def test_exhibitor_apply_rules_not_accepted_422(db_session, client):
    await open_call_for_exhibitor(db_session)

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/exhibitors/apply",
            json=payload(rules_accepted=False, contact_email="autre@expo.com"),
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_exhibitor_apply_invalid_reps_count_422(db_session, client):
    await open_call_for_exhibitor(db_session)

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/exhibitors/apply",
            json=payload(reps_count=0, contact_email="zero@expo.com"),
        )

    assert response.status_code == 422
