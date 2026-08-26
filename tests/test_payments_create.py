import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.main import app
from app.models import PassType, PromoCode, User


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()


async def make_user(db_session, email: str = "payeur@example.com") -> User:
    user = User(
        first_name="Awa",
        last_name="Diop",
        email=email,
        phone_whatsapp="+221771234567",
        country="Sénégal",
        city="Dakar",
        gdpr_consent=True,
        newsletter_consent=False,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.mark.asyncio
async def test_create_payment_success_no_promo(db_session, client):
    user = await make_user(db_session)
    pass_type = PassType(name="Standard", price=15000, is_active=True)
    db_session.add(pass_type)
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/payments",
            json={
                "user_id": user.id,
                "pass_type_id": pass_type.id,
                "payment_method": "wave",
            },
        )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["amount_original"] == 15000
    assert body["amount_paid"] == 15000
    assert body["promo_code_id"] is None


@pytest.mark.asyncio
async def test_create_payment_applies_percent_discount(db_session, client):
    user = await make_user(db_session, "promo10@example.com")
    pass_type = PassType(name="Standard", price=15000, is_active=True)
    promo = PromoCode(code="PROMO10", discount_pct=10, is_active=True)
    db_session.add_all([pass_type, promo])
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/payments",
            json={
                "user_id": user.id,
                "pass_type_id": pass_type.id,
                "payment_method": "wave",
                "promo_code": "PROMO10",
            },
        )

    assert response.status_code == 201
    body = response.json()
    assert body["amount_original"] == 15000
    assert body["amount_paid"] == 13500
    assert body["promo_code_id"] == promo.id


@pytest.mark.asyncio
async def test_create_payment_applies_fixed_discount(db_session, client):
    user = await make_user(db_session, "fixed@example.com")
    pass_type = PassType(name="Standard", price=15000, is_active=True)
    promo = PromoCode(code="FIXED5000", discount_pct=0, discount_fixed=5000, is_active=True)
    db_session.add_all([pass_type, promo])
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/payments",
            json={
                "user_id": user.id,
                "pass_type_id": pass_type.id,
                "payment_method": "wave",
                "promo_code": "FIXED5000",
            },
        )

    assert response.status_code == 201
    assert response.json()["amount_paid"] == 10000


@pytest.mark.asyncio
async def test_create_payment_invalid_user_400(db_session, client):
    pass_type = PassType(name="Standard", price=15000, is_active=True)
    db_session.add(pass_type)
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/payments",
            json={"user_id": 999999, "pass_type_id": pass_type.id, "payment_method": "wave"},
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_payment_invalid_promo_400(db_session, client):
    user = await make_user(db_session, "badpromo@example.com")
    pass_type = PassType(name="Standard", price=15000, is_active=True)
    db_session.add(pass_type)
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/payments",
            json={
                "user_id": user.id,
                "pass_type_id": pass_type.id,
                "payment_method": "wave",
                "promo_code": "GHOST",
            },
        )

    assert response.status_code == 400
