import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.main import app
from app.models import Partner, PartnerLevel


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()


def make_partner(level_id: int, **overrides) -> Partner:
    defaults = dict(
        organization_name="ACME",
        sector="Tech/ESN",
        country="SN",
        city="Dakar",
        contact_name="Jean",
        contact_position="CEO",
        contact_email="j@acme.com",
        contact_phone="+221700000000",
        level_id=level_id,
        objectives="Visibilité",
        gdpr_consent=True,
        is_public=True,
    )
    defaults.update(overrides)
    return Partner(**defaults)


@pytest.mark.asyncio
async def test_partners_filter_by_level_excludes_private(db_session, client):
    gold = PartnerLevel(name="Gold", price=500000)
    silver = PartnerLevel(name="Silver", price=200000)
    db_session.add_all([gold, silver])
    await db_session.flush()

    db_session.add_all(
        [
            make_partner(gold.id, organization_name="Gold Public", contact_email="a@x.com"),
            make_partner(
                gold.id, organization_name="Gold Private", is_public=False,
                contact_email="b@x.com",
            ),
            make_partner(silver.id, organization_name="Silver Public", contact_email="c@x.com"),
        ]
    )
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(f"/api/partners?level={gold.id}")

    assert response.status_code == 200
    names = [p["organization_name"] for p in response.json()]
    assert names == ["Gold Public"]


@pytest.mark.asyncio
async def test_partners_empty_result(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get("/api/partners?level=999999")

    assert response.status_code == 200
    assert response.json() == []
