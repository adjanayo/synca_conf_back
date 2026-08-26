import pytest
from fastapi import HTTPException, status
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.main import app


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_contact_success_without_recaptcha_configured(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/contact",
            json={
                "name": "Awa",
                "email": "awa@example.com",
                "message": "Bonjour, question sur la billetterie.",
                "captcha": "any-token",
            },
        )

    assert response.status_code == 201
    body = response.json()
    assert body["message"] == "Bonjour, question sur la billetterie."
    assert body["is_read"] is False


@pytest.mark.asyncio
async def test_contact_missing_message_422(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/contact",
            json={"name": "Awa", "email": "awa@example.com", "captcha": "token"},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_contact_rejected_when_recaptcha_fails(db_session, client, monkeypatch):
    # verify_recaptcha's own httpx-mocking is covered by test_recaptcha.py;
    # here we only need the route to propagate a recaptcha rejection, so we
    # stub the function directly instead of mocking httpx.AsyncClient (which
    # would also intercept this test's own ASGI test client, since it's the
    # same class).
    async def fake_verify_recaptcha(token: str) -> None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="reCAPTCHA échec.")

    monkeypatch.setattr("app.api.forms.verify_recaptcha", fake_verify_recaptcha)

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/contact",
            json={
                "name": "Bot",
                "email": "bot@example.com",
                "message": "spam",
                "captcha": "bad-token",
            },
        )

    assert response.status_code == 400
