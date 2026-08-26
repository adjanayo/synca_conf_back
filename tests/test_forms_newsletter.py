import pytest
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
async def test_newsletter_subscribe_success(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post("/api/newsletter", json={"email": "newsletter@example.com"})

    assert response.status_code == 201
    assert response.json()["email"] == "newsletter@example.com"


@pytest.mark.asyncio
async def test_newsletter_duplicate_email_conflict(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        first = await http.post("/api/newsletter", json={"email": "dup@example.com"})
        second = await http.post("/api/newsletter", json={"email": "dup@example.com"})

    assert first.status_code == 201
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_newsletter_invalid_email_422(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post("/api/newsletter", json={"email": "not-an-email"})

    assert response.status_code == 422
