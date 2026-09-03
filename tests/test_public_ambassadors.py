import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.main import app
from app.models import Ambassador


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()


def make_ambassador(**overrides) -> Ambassador:
    defaults = dict(
        first_name="A",
        last_name="Diop",
        age=22,
        country="SN",
        city="Dakar",
        email="a@example.com",
        phone_whatsapp="+221700000000",
        motivation="Motivation",
        mobilization_plan="Plan",
        preferred_channels="Instagram",
        gdpr_consent=True,
        is_public=True,
    )
    defaults.update(overrides)
    return Ambassador(**defaults)


@pytest.mark.asyncio
async def test_list_ambassadors_excludes_private_and_pii(db_session, client):
    db_session.add_all(
        [
            make_ambassador(last_name="Visible"),
            make_ambassador(email="b@example.com", last_name="Zzz", is_public=False),
        ]
    )
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get("/api/ambassadors")

    assert response.status_code == 200
    body = response.json()
    last_names = [a["last_name"] for a in body]
    assert last_names == ["Visible"]
    assert "email" not in body[0]
    assert "phone_whatsapp" not in body[0]


@pytest.mark.asyncio
async def test_get_ambassador_detail(db_session, client):
    ambassador = make_ambassador(last_name="Détail")
    db_session.add(ambassador)
    await db_session.commit()
    await db_session.refresh(ambassador)

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(f"/api/ambassadors/{ambassador.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["last_name"] == "Détail"
    assert "email" not in body
    assert "phone_whatsapp" not in body


@pytest.mark.asyncio
async def test_get_ambassador_detail_404_when_not_public(db_session, client):
    ambassador = make_ambassador(is_public=False)
    db_session.add(ambassador)
    await db_session.commit()
    await db_session.refresh(ambassador)

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(f"/api/ambassadors/{ambassador.id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_ambassador_detail_404_when_missing(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get("/api/ambassadors/999999")

    assert response.status_code == 404
