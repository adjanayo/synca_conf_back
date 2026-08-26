import datetime
import io
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from PIL import Image
from sqlalchemy import select

from app.core.database import get_db
from app.main import app
from app.models import CampaignWindow, PartnerLevel


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()


async def open_call_for_partner(db_session) -> None:
    now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    window = (
        await db_session.execute(
            select(CampaignWindow).where(CampaignWindow.key == "call_for_partner")
        )
    ).scalar_one()
    window.start_at = now - datetime.timedelta(days=1)
    window.end_at = now + datetime.timedelta(days=1)
    window.is_active = True
    await db_session.commit()


def make_png_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10), color="green").save(buffer, format="PNG")
    return buffer.getvalue()


def form_fields(level_id: int, **overrides) -> dict:
    fields = {
        "organization_name": "ACME",
        "sector": "Tech/ESN",
        "country": "Sénégal",
        "city": "Dakar",
        "contact_name": "Jean Dupont",
        "contact_position": "CEO",
        "contact_email": "jean@acme.com",
        "contact_phone": "+221773333333",
        "level_id": str(level_id),
        "objectives": ["Visibilité"],
        "gdpr_consent": "true",
    }
    fields.update(overrides)
    return fields


@pytest.mark.asyncio
async def test_partner_apply_closed_window_forbidden(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post("/api/partners/apply", data=form_fields(1))

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_partner_apply_success_without_logo(db_session, client):
    await open_call_for_partner(db_session)
    level = PartnerLevel(name="Gold", price=500000)
    db_session.add(level)
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post("/api/partners/apply", data=form_fields(level.id))

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["logo_url"] is None
    assert body["objectives"] == "Visibilité"


@pytest.mark.asyncio
async def test_partner_apply_success_with_logo(db_session, client, monkeypatch):
    await open_call_for_partner(db_session)
    level = PartnerLevel(name="Silver", price=200000)
    db_session.add(level)
    await db_session.commit()
    monkeypatch.setattr("app.services.storage._client", lambda: MagicMock())

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/partners/apply",
            data=form_fields(level.id, contact_email="autre@acme.com"),
            files={"logo": ("logo-prive.png", make_png_bytes(), "image/png")},
        )

    assert response.status_code == 201
    assert "logo-prive" not in response.json()["logo_url"]


@pytest.mark.asyncio
async def test_partner_apply_invalid_level_400(db_session, client):
    await open_call_for_partner(db_session)

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post("/api/partners/apply", data=form_fields(999999))

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_partner_apply_fake_logo_rejected_400(db_session, client):
    await open_call_for_partner(db_session)
    level = PartnerLevel(name="Bronze", price=50000)
    db_session.add(level)
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/partners/apply",
            data=form_fields(level.id, contact_email="fake@acme.com"),
            files={"logo": ("logo.png", b"not-a-real-image", "image/png")},
        )

    assert response.status_code == 400
