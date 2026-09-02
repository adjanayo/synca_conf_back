import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.database import get_db
from app.main import app
from app.models import AdminUser, Permission, Role, RolePermission
from app.services.auth_service import create_access_token


async def make_admin_with_permissions(
    db_session, role_name: str, permission_codes: list[str]
) -> AdminUser:
    role = (
        await db_session.execute(select(Role).where(Role.name == role_name))
    ).scalar_one_or_none()
    if role is None:
        role = Role(name=role_name)
        db_session.add(role)
        await db_session.flush()

    for code in permission_codes:
        permission = (
            await db_session.execute(select(Permission).where(Permission.code == code))
        ).scalar_one_or_none()
        if permission is None:
            permission = Permission(code=code)
            db_session.add(permission)
            await db_session.flush()
        db_session.add(RolePermission(role_id=role.id, permission_id=permission.id))

    admin = AdminUser(email=f"{role_name}@synca.conf", password_hash="hash", role_id=role.id)
    db_session.add(admin)
    await db_session.commit()
    return admin


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_me_returns_identity_role_and_permissions(db_session, client):
    admin = await make_admin_with_permissions(
        db_session, "editor_me", ["speakers.approve", "partners.manage"]
    )
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(
            "/api/admin/me", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == admin.id
    assert body["email"] == admin.email
    assert body["role"] == "editor_me"
    assert sorted(body["permission_codes"]) == ["partners.manage", "speakers.approve"]


@pytest.mark.asyncio
async def test_me_unauthenticated_rejected(client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get("/api/admin/me")

    assert response.status_code == 401
