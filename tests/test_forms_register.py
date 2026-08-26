import datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.database import get_db
from app.main import app
from app.models import CampaignWindow, PassType, PromoCode, User


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()


async def open_ticketing(db_session) -> None:
    now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    window = (
        await db_session.execute(select(CampaignWindow).where(CampaignWindow.key == "ticketing"))
    ).scalar_one()
    window.start_at = now - datetime.timedelta(days=1)
    window.end_at = now + datetime.timedelta(days=1)
    window.is_active = True
    await db_session.commit()


def register_payload(**overrides) -> dict:
    payload = {
        "first_name": "Awa",
        "last_name": "Diop",
        "email": "awa@example.com",
        "phone_whatsapp": "+221771234567",
        "country": "Sénégal",
        "city": "Dakar",
        "profiles": ["Étudiant"],
        "pass_type_id": 1,
        "gdpr_consent": True,
    }
    payload.update(overrides)
    return payload


@pytest.mark.asyncio
async def test_register_closed_window_forbidden(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post("/api/register", json=register_payload())

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_register_success(db_session, client):
    await open_ticketing(db_session)
    pass_type = PassType(name="Standard", price=15000, is_active=True)
    db_session.add(pass_type)
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/register", json=register_payload(pass_type_id=pass_type.id)
        )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "awa@example.com"


@pytest.mark.asyncio
async def test_register_sends_confirmation_email(db_session, client, monkeypatch):
    await open_ticketing(db_session)
    pass_type = PassType(name="Standard", price=15000, is_active=True)
    db_session.add(pass_type)
    await db_session.commit()

    sent = {}

    async def fake_send_email(to: str, subject: str, body: str) -> None:
        sent["to"] = to
        sent["subject"] = subject

    monkeypatch.setattr("app.api.forms.send_email", fake_send_email)

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/register",
            json=register_payload(pass_type_id=pass_type.id, email="confirm@example.com"),
        )

    assert response.status_code == 201
    assert sent["to"] == "confirm@example.com"
    assert "Confirmation" in sent["subject"]


@pytest.mark.asyncio
async def test_register_missing_gdpr_consent_422(db_session, client):
    await open_ticketing(db_session)
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/register", json=register_payload(gdpr_consent=False)
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_pass_type_400(db_session, client):
    await open_ticketing(db_session)
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/register", json=register_payload(pass_type_id=999999)
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_register_inactive_pass_type_400(db_session, client):
    await open_ticketing(db_session)
    pass_type = PassType(name="Retiré", price=5000, is_active=False)
    db_session.add(pass_type)
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/register", json=register_payload(pass_type_id=pass_type.id)
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_register_invalid_promo_code_400(db_session, client):
    await open_ticketing(db_session)
    pass_type = PassType(name="Standard", price=15000, is_active=True)
    db_session.add(pass_type)
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/register",
            json=register_payload(pass_type_id=pass_type.id, promo_code="DOESNOTEXIST"),
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_register_valid_promo_code_accepted(db_session, client):
    await open_ticketing(db_session)
    pass_type = PassType(name="Standard", price=15000, is_active=True)
    promo = PromoCode(code="AMB1", discount_pct=10, is_active=True)
    db_session.add_all([pass_type, promo])
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/register",
            json=register_payload(pass_type_id=pass_type.id, promo_code="AMB1"),
        )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_register_duplicate_email_conflict(db_session, client):
    await open_ticketing(db_session)
    pass_type = PassType(name="Standard", price=15000, is_active=True)
    db_session.add_all(
        [
            pass_type,
            User(
                first_name="Existant",
                last_name="Déjà",
                email="awa@example.com",
                phone_whatsapp="+221700000000",
                country="Sénégal",
                city="Dakar",
                gdpr_consent=True,
                newsletter_consent=False,
            ),
        ]
    )
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/register", json=register_payload(pass_type_id=pass_type.id)
        )

    assert response.status_code == 409
