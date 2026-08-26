import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.database import get_db
from app.main import app
from app.models import AdminUser, Role
from app.services.auth_service import create_access_token


async def make_admin_with_role(db_session, role_name: str) -> AdminUser:
    role = (
        await db_session.execute(select(Role).where(Role.name == role_name))
    ).scalar_one_or_none()
    if role is None:
        role = Role(name=role_name)
        db_session.add(role)
        await db_session.flush()

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
async def test_superadmin_can_update_role_permissions(db_session, client):
    superadmin = await make_admin_with_role(db_session, "superadmin")
    target_role = Role(name="editor_target")
    db_session.add(target_role)
    await db_session.commit()

    token = create_access_token(subject=str(superadmin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.patch(
            f"/api/admin/roles/{target_role.id}",
            json={"permission_codes": ["speakers.approve", "partners.manage"]},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "editor_target"
    assert sorted(body["permission_codes"]) == ["partners.manage", "speakers.approve"]


@pytest.mark.asyncio
async def test_non_superadmin_forbidden(db_session, client):
    admin = await make_admin_with_role(db_session, "admin_no_roles_manage")
    target_role = Role(name="another_target")
    db_session.add(target_role)
    await db_session.commit()

    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.patch(
            f"/api/admin/roles/{target_role.id}",
            json={"permission_codes": ["speakers.approve"]},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_unauthenticated_rejected(db_session, client):
    target_role = Role(name="no_auth_target")
    db_session.add(target_role)
    await db_session.commit()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.patch(
            f"/api/admin/roles/{target_role.id}",
            json={"permission_codes": []},
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_unknown_permission_code_rejected(db_session, client):
    superadmin = await make_admin_with_role(db_session, "superadmin")
    target_role = Role(name="yet_another_target")
    db_session.add(target_role)
    await db_session.commit()

    token = create_access_token(subject=str(superadmin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.patch(
            f"/api/admin/roles/{target_role.id}",
            json={"permission_codes": ["does.not.exist"]},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 400
