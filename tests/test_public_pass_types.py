import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.main import app
from app.models import PassType


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_pass_types_excludes_inactive(db_session, client):
    db_session.add_all(
        [
            PassType(name="Standard", price=15000, is_active=True),
            PassType(name="VIP", price=50000, is_active=True),
            PassType(name="Retiré", price=5000, is_active=False),
        ]
    )
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get("/api/pass-types")

    assert response.status_code == 200
    names = [p["name"] for p in response.json()]
    assert names == ["Standard", "VIP"]


@pytest.mark.asyncio
async def test_list_pass_types_empty(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get("/api/pass-types")

    assert response.status_code == 200
    assert response.json() == []
