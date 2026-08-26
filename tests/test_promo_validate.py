import datetime

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.main import app
from app.models import PromoCode


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_promo_validate_success(db_session, client):
    db_session.add(PromoCode(code="VALID10", discount_pct=10, is_active=True))
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post("/api/promo/validate", json={"code": "VALID10"})

    assert response.status_code == 200
    assert response.json() == {"code": "VALID10", "discount_pct": 10, "discount_fixed": None}


@pytest.mark.asyncio
async def test_promo_validate_unknown_code_400(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post("/api/promo/validate", json={"code": "GHOST"})

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_promo_validate_inactive_400(db_session, client):
    db_session.add(PromoCode(code="OFF", discount_pct=10, is_active=False))
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post("/api/promo/validate", json={"code": "OFF"})

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_promo_validate_expired_400(db_session, client):
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    db_session.add(
        PromoCode(code="EXPIRED", discount_pct=10, is_active=True, valid_until=yesterday)
    )
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post("/api/promo/validate", json={"code": "EXPIRED"})

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_promo_validate_exhausted_400(db_session, client):
    db_session.add(
        PromoCode(code="USEDUP", discount_pct=10, is_active=True, usage_limit=5, usage_count=5)
    )
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post("/api/promo/validate", json={"code": "USEDUP"})

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_promo_validate_fixed_discount(db_session, client):
    db_session.add(PromoCode(code="FIXED5000", discount_pct=0, discount_fixed=5000, is_active=True))
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post("/api/promo/validate", json={"code": "FIXED5000"})

    assert response.status_code == 200
    assert response.json()["discount_fixed"] == 5000
