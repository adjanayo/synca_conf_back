import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.main import app
from app.models import Exhibitor


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()


def make_exhibitor(**overrides) -> Exhibitor:
    defaults = dict(
        organization_name="Expo",
        sector="Tech",
        country="SN",
        city="Dakar",
        contact_name="A",
        contact_position="Manager",
        contact_email="a@expo.com",
        contact_phone="+221700000000",
        stand_type="Standard",
        reps_count=2,
        products_services="Logiciels",
        rules_accepted=True,
        gdpr_consent=True,
        is_public=True,
    )
    defaults.update(overrides)
    return Exhibitor(**defaults)


@pytest.mark.asyncio
async def test_exhibitors_excludes_private(db_session, client):
    db_session.add_all(
        [
            make_exhibitor(organization_name="Public Expo", contact_email="a@x.com"),
            make_exhibitor(
                organization_name="Private Expo", is_public=False, contact_email="b@x.com"
            ),
        ]
    )
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get("/api/exhibitors")

    assert response.status_code == 200
    names = [e["organization_name"] for e in response.json()]
    assert names == ["Public Expo"]


@pytest.mark.asyncio
async def test_exhibitors_empty_result(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get("/api/exhibitors")

    assert response.status_code == 200
    assert response.json() == []
