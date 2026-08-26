from contextlib import asynccontextmanager

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.admin import auth as admin_auth
from app.core.database import engine, get_db
from app.core.security import hash_password
from app.main import app
from app.models import AdminUser, Permission, Role, RolePermission

PASSWORD = "correct horse battery staple"


async def make_admin(db_session, email: str, role_name: str) -> AdminUser:
    role = (
        await db_session.execute(select(Role).where(Role.name == role_name))
    ).scalar_one_or_none()
    if role is None:
        role = Role(name=role_name)
        db_session.add(role)
        await db_session.flush()

    admin = AdminUser(email=email, password_hash=hash_password(PASSWORD), role_id=role.id)
    db_session.add(admin)
    await db_session.commit()
    return admin


async def grant_permission(db_session, role_name: str, code: str) -> None:
    role = (
        await db_session.execute(select(Role).where(Role.name == role_name))
    ).scalar_one()
    permission = (
        await db_session.execute(select(Permission).where(Permission.code == code))
    ).scalar_one_or_none()
    if permission is None:
        permission = Permission(code=code)
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
        await db_session.commit()


@pytest.fixture(autouse=True)
async def _dispose_global_engine():
    # SQLAdmin's ModelView list/detail queries run through app.core.database's
    # module-level `engine`/pool, not through the get_db override -- its
    # pooled connections are bound to the event loop that created them.
    # pytest-asyncio spins up a fresh loop per test, so a connection kept
    # alive across tests raises "attached to a different loop". Disposing
    # after each test forces a clean connection on the next one.
    yield
    await engine.dispose()


@pytest.fixture
def client(db_session, monkeypatch):
    async def override_get_db():
        yield db_session

    # AdminAuth (app/admin/auth.py) opens its own AsyncSessionLocal(), a
    # different connection from this test's SAVEPOINT-isolated db_session --
    # same reasoning as finalize_ticket's tests. Reuse db_session so the
    # login/permission checks see the rows this test just created.
    @asynccontextmanager
    async def _fake_session_local():
        yield db_session

    monkeypatch.setattr(admin_auth, "AsyncSessionLocal", _fake_session_local)

    app.dependency_overrides[get_db] = override_get_db
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_login_success_grants_access_to_a_permitted_view(db_session, client):
    await make_admin(db_session, "superadmin-panel@synca.conf", "superadmin")
    await grant_permission(db_session, "superadmin", "speakers.approve")

    async with AsyncClient(transport=client, base_url="http://test") as http:
        login = await http.post(
            "/admin/login",
            data={"username": "superadmin-panel@synca.conf", "password": PASSWORD},
        )
        assert login.status_code in (302, 303)

        response = await http.get("/admin/speaker/list")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_login_wrong_password_is_rejected(db_session, client):
    await make_admin(db_session, "wrongpass-panel@synca.conf", "superadmin")

    async with AsyncClient(transport=client, base_url="http://test") as http:
        login = await http.post(
            "/admin/login",
            data={"username": "wrongpass-panel@synca.conf", "password": "nope"},
        )
        assert login.status_code == 400

        response = await http.get("/admin/speaker/list")

    # No session was ever established -- SQLAdmin redirects to /admin/login.
    assert response.status_code in (302, 303)


@pytest.mark.asyncio
async def test_role_without_permission_gets_403_on_gated_view(db_session, client):
    await make_admin(db_session, "support-panel@synca.conf", "support")

    async with AsyncClient(transport=client, base_url="http://test") as http:
        login = await http.post(
            "/admin/login",
            data={"username": "support-panel@synca.conf", "password": PASSWORD},
        )
        assert login.status_code in (302, 303)

        response = await http.get("/admin/speaker/list")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_any_authenticated_admin_can_read_contact_messages(db_session, client):
    await make_admin(db_session, "support-contact@synca.conf", "support")

    async with AsyncClient(transport=client, base_url="http://test") as http:
        login = await http.post(
            "/admin/login",
            data={"username": "support-contact@synca.conf", "password": PASSWORD},
        )
        assert login.status_code in (302, 303)

        response = await http.get("/admin/contact-message/list")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_unauthenticated_request_redirects_to_login(client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get("/admin/speaker/list")

    assert response.status_code in (302, 303)
