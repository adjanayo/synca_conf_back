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
async def test_list_campaign_windows_returns_seeded_windows(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get("/api/campaign-windows")

    assert response.status_code == 200
    keys = {w["key"] for w in response.json()}
    assert keys == {
        "call_for_speaker",
        "ticketing",
        "call_for_partner",
        "call_for_ambassador",
        "call_for_exhibitor",
        "event",
        "hackathon_universitaire",
        "call_for_community_certified",
    }
