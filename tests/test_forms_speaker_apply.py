import datetime
import io
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from PIL import Image
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


async def open_call_for_speaker(db_session) -> None:
    now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    window = (
        await db_session.execute(
            select(CampaignWindow).where(CampaignWindow.key == "call_for_speaker")
        )
    ).scalar_one()
    window.start_at = now - datetime.timedelta(days=1)
    window.end_at = now + datetime.timedelta(days=1)
    window.is_active = True
    await db_session.commit()


def make_png_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10), color="blue").save(buffer, format="PNG")
    return buffer.getvalue()


def form_fields(**overrides) -> dict:
    fields = {
        "first_name": "Moussa",
        "last_name": "Ba",
        "title_role": "CTO",
        "country": "Sénégal",
        "email": "moussa@example.com",
        "phone_whatsapp": "+221700000000",
        "intervention_format": "Keynote",
        "intervention_title": "L'IA en Afrique",
        "theme": "IA",
        "summary": "Résumé de l'intervention.",
        "motivation": "Envie de partager.",
        "gdpr_consent": "true",
    }
    fields.update(overrides)
    return fields


@pytest.mark.asyncio
async def test_speaker_apply_closed_window_forbidden(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/speakers/apply",
            data=form_fields(),
            files={"photo": ("photo.png", make_png_bytes(), "image/png")},
        )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_speaker_apply_success(db_session, client, monkeypatch):
    await open_call_for_speaker(db_session)
    mock_client = MagicMock()
    monkeypatch.setattr("app.services.storage._client", lambda: mock_client)

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/speakers/apply",
            data=form_fields(),
            files={"photo": ("photo-secrete.png", make_png_bytes(), "image/png")},
        )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["is_public"] is False
    assert "photo-secrete" not in body["photo_url"]


@pytest.mark.asyncio
async def test_speaker_apply_rejects_fake_image(db_session, client):
    await open_call_for_speaker(db_session)

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/speakers/apply",
            data=form_fields(email="autre@example.com"),
            files={"photo": ("photo.png", b"not-a-real-image", "image/png")},
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_speaker_apply_missing_gdpr_consent_422(db_session, client):
    await open_call_for_speaker(db_session)

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/speakers/apply",
            data=form_fields(gdpr_consent="false", email="autre2@example.com"),
            files={"photo": ("photo.png", make_png_bytes(), "image/png")},
        )

    assert response.status_code == 422
