import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.main import app
from app.models import AdminUser, Permission, Role, RolePermission
from app.services.auth_service import create_access_token


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
async def test_public_form_endpoint_limited_to_3_per_minute(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        statuses = []
        for i in range(4):
            response = await http.post(
                "/api/waitlist", json={"email": f"rl-{i}@example.com"}
            )
            statuses.append(response.status_code)

    assert statuses[:3] == [201, 201, 201]
    assert statuses[3] == 429


@pytest.mark.asyncio
async def test_admin_endpoint_limited_to_30_per_minute(db_session, client):
    role = (
        await db_session.execute(select(Role).where(Role.name == "superadmin"))
    ).scalar_one_or_none()
    if role is None:
        role = Role(name="superadmin")
        db_session.add(role)
        await db_session.flush()

    permission = (
        await db_session.execute(
            select(Permission).where(Permission.code == "campaign_windows.manage")
        )
    ).scalar_one_or_none()
    if permission is None:
        permission = Permission(code="campaign_windows.manage")
        db_session.add(permission)
        await db_session.flush()

    existing = (
        await db_session.execute(
            select(RolePermission).where(
                RolePermission.role_id == role.id, RolePermission.permission_id == permission.id
            )
        )
    ).scalar_one_or_none()
    if existing is None:
        db_session.add(RolePermission(role_id=role.id, permission_id=permission.id))

    admin = AdminUser(email="rl-admin@synca.conf", password_hash="hash", role_id=role.id)
    db_session.add(admin)
    await db_session.commit()

    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        statuses = []
        for _ in range(31):
            response = await http.get(
                "/api/admin/campaign-windows", headers={"Authorization": f"Bearer {token}"}
            )
            statuses.append(response.status_code)

    assert statuses[:30] == [200] * 30
    assert statuses[30] == 429


@pytest.mark.asyncio
async def test_default_global_limit_is_60_per_minute(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        statuses = []
        for _ in range(61):
            response = await http.get("/api/campaign-windows")
            statuses.append(response.status_code)

    assert statuses[:60] == [200] * 60
    assert statuses[60] == 429
