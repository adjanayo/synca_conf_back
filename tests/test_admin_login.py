import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.security import hash_password
from app.main import app
from app.models import AdminUser, Role
from app.services.auth_service import (
    AccountLockedError,
    InvalidCredentialsError,
    authenticate_admin,
)

PASSWORD = "correct horse battery staple"


async def make_admin(db_session, email: str) -> AdminUser:
    role = (
        await db_session.execute(select(Role).where(Role.name == "superadmin"))
    ).scalar_one_or_none()
    if role is None:
        role = Role(name="superadmin")
        db_session.add(role)
        await db_session.flush()

    admin = AdminUser(email=email, password_hash=hash_password(PASSWORD), role_id=role.id)
    db_session.add(admin)
    await db_session.commit()
    return admin


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    limiter.reset()
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()
    limiter.reset()


@pytest.mark.asyncio
async def test_login_success_returns_token_pair(db_session, client):
    await make_admin(db_session, "success@synca.conf")

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/admin/login", json={"email": "success@synca.conf", "password": PASSWORD}
        )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]


@pytest.mark.asyncio
async def test_login_wrong_password_generic_401(db_session, client):
    await make_admin(db_session, "wrongpass@synca.conf")

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/admin/login", json={"email": "wrongpass@synca.conf", "password": "nope"}
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Email ou mot de passe incorrect."


@pytest.mark.asyncio
async def test_unknown_email_same_generic_401(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/admin/login", json={"email": "ghost@synca.conf", "password": "whatever"}
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Email ou mot de passe incorrect."


@pytest.mark.asyncio
async def test_rate_limit_blocks_sixth_request_per_minute(db_session, client):
    await make_admin(db_session, "ratelimited@synca.conf")

    async with AsyncClient(transport=client, base_url="http://test") as http:
        statuses = []
        for _ in range(6):
            response = await http.post(
                "/api/admin/login",
                json={"email": "ratelimited@synca.conf", "password": "wrong"},
            )
            statuses.append(response.status_code)

    assert statuses[:5] == [401] * 5
    assert statuses[5] == 429


@pytest.mark.asyncio
async def test_account_locks_after_five_failed_attempts(db_session):
    admin = await make_admin(db_session, "lockout@synca.conf")

    for _ in range(5):
        with pytest.raises(InvalidCredentialsError):
            await authenticate_admin(db_session, admin.email, "wrong")

    with pytest.raises(AccountLockedError):
        await authenticate_admin(db_session, admin.email, PASSWORD)
