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


async def open_call_for_ambassador(db_session) -> None:
    now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    window = (
        await db_session.execute(
            select(CampaignWindow).where(CampaignWindow.key == "call_for_ambassador")
        )
    ).scalar_one()
    window.start_at = now - datetime.timedelta(days=1)
    window.end_at = now + datetime.timedelta(days=1)
    window.is_active = True
    await db_session.commit()


def payload(**overrides) -> dict:
    data = {
        "first_name": "Fatou",
        "last_name": "Sow",
        "age": 22,
        "country": "Sénégal",
        "city": "Dakar",
        "email": "fatou@example.com",
        "phone_whatsapp": "+221772222222",
        "social_handles": {"instagram": "@fatou"},
        "motivation": "Motivation.",
        "mobilization_plan": "Plan.",
        "preferred_channels": ["WhatsApp", "Instagram"],
        "gdpr_consent": True,
    }
    data.update(overrides)
    return data


@pytest.mark.asyncio
async def test_ambassador_apply_closed_window_forbidden(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post("/api/ambassadors/apply", json=payload())

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_ambassador_apply_success(db_session, client):
    await open_call_for_ambassador(db_session)

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post("/api/ambassadors/apply", json=payload())

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["preferred_channels"] == "WhatsApp, Instagram"
    assert body["social_handles"] == {"instagram": "@fatou"}


@pytest.mark.asyncio
async def test_ambassador_apply_under_age_422(db_session, client):
    await open_call_for_ambassador(db_session)

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/ambassadors/apply", json=payload(age=15, email="jeune@example.com")
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ambassador_apply_empty_channels_422(db_session, client):
    await open_call_for_ambassador(db_session)

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/ambassadors/apply",
            json=payload(preferred_channels=[], email="autre@example.com"),
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ambassador_apply_missing_gdpr_consent_422(db_session, client):
    await open_call_for_ambassador(db_session)

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/ambassadors/apply",
            json=payload(gdpr_consent=False, email="sanscgu@example.com"),
        )

    assert response.status_code == 422
