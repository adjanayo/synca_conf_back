from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.core.security import hash_password
from app.main import app
from app.models import OtpCode, User
from app.services import otp_service


async def make_verified_user(db_session, email: str = "otp@example.com") -> User:
    user = User(
        first_name="Awa",
        last_name="Diop",
        email=email,
        email_verified=True,
        phone_whatsapp="+221771234567",
        country="Sénégal",
        city="Dakar",
        gdpr_consent=True,
        newsletter_consent=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()


@pytest.fixture
def fixed_code(monkeypatch):
    monkeypatch.setattr(otp_service, "_generate_code", lambda: "123456")
    return "123456"


@pytest.mark.asyncio
async def test_request_otp_same_generic_response_known_and_unknown_email(
    db_session, client, fixed_code
):
    await make_verified_user(db_session, "known@example.com")

    async with AsyncClient(transport=client, base_url="http://test") as http:
        known = await http.post("/api/auth/otp/request", json={"email": "known@example.com"})
        unknown = await http.post("/api/auth/otp/request", json={"email": "ghost@example.com"})

    assert known.status_code == 200
    assert unknown.status_code == 200
    assert known.json() == unknown.json()


@pytest.mark.asyncio
async def test_request_otp_only_creates_row_for_known_verified_email(
    db_session, client, fixed_code
):
    await make_verified_user(db_session, "known@example.com")

    async with AsyncClient(transport=client, base_url="http://test") as http:
        await http.post("/api/auth/otp/request", json={"email": "known@example.com"})
        await http.post("/api/auth/otp/request", json={"email": "ghost@example.com"})

    rows = (await db_session.execute(OtpCode.__table__.select())).fetchall()
    assert len(rows) == 1


@pytest.mark.asyncio
async def test_verify_otp_success_grants_access_to_user_me(db_session, client, fixed_code):
    await make_verified_user(db_session, "known@example.com")

    async with AsyncClient(transport=client, base_url="http://test") as http:
        await http.post("/api/auth/otp/request", json={"email": "known@example.com"})
        verify = await http.post(
            "/api/auth/otp/verify", json={"email": "known@example.com", "code": "123456"}
        )
        assert verify.status_code == 200
        token = verify.json()["access_token"]

        me = await http.get("/api/user/me", headers={"Authorization": f"Bearer {token}"})

    assert me.status_code == 200
    assert me.json()["email"] == "known@example.com"


@pytest.mark.asyncio
async def test_verify_otp_wrong_code_returns_401(db_session, client, fixed_code):
    await make_verified_user(db_session, "known@example.com")

    async with AsyncClient(transport=client, base_url="http://test") as http:
        await http.post("/api/auth/otp/request", json={"email": "known@example.com"})
        response = await http.post(
            "/api/auth/otp/verify", json={"email": "known@example.com", "code": "000000"}
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_verify_otp_unknown_email_same_generic_401(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/auth/otp/verify", json={"email": "ghost@example.com", "code": "123456"}
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_verify_otp_expired_code_returns_401(db_session, client, fixed_code):
    user = await make_verified_user(db_session, "known@example.com")
    db_session.add(
        OtpCode(
            user_id=user.id,
            code_hash=hash_password("123456"),
            expires_at=datetime.now(UTC) - timedelta(minutes=1),
        )
    )
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/auth/otp/verify", json={"email": "known@example.com", "code": "123456"}
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_verify_otp_cannot_be_reused(db_session, client, fixed_code):
    await make_verified_user(db_session, "known@example.com")

    async with AsyncClient(transport=client, base_url="http://test") as http:
        await http.post("/api/auth/otp/request", json={"email": "known@example.com"})
        first = await http.post(
            "/api/auth/otp/verify", json={"email": "known@example.com", "code": "123456"}
        )
        second = await http.post(
            "/api/auth/otp/verify", json={"email": "known@example.com", "code": "123456"}
        )

    assert first.status_code == 200
    assert second.status_code == 401


@pytest.mark.asyncio
async def test_request_otp_rate_limited_after_three_per_15_minutes(
    db_session, client, fixed_code
):
    await make_verified_user(db_session, "known@example.com")

    async with AsyncClient(transport=client, base_url="http://test") as http:
        statuses = []
        for _ in range(4):
            response = await http.post(
                "/api/auth/otp/request", json={"email": "known@example.com"}
            )
            statuses.append(response.status_code)

    assert statuses[:3] == [200, 200, 200]
    assert statuses[3] == 429
