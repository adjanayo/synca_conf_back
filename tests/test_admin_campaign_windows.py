import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.database import get_db
from app.main import app
from app.models import AdminUser, CampaignWindow, Permission, Role, RolePermission
from app.services.auth_service import create_access_token


async def make_admin_with_permission(db_session, role_name: str, code: str | None) -> AdminUser:
    role = (
        await db_session.execute(select(Role).where(Role.name == role_name))
    ).scalar_one_or_none()
    if role is None:
        role = Role(name=role_name)
        db_session.add(role)
        await db_session.flush()

    if code is not None:
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
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == permission.id,
                )
            )
        ).scalar_one_or_none()
        if existing is None:
            db_session.add(RolePermission(role_id=role.id, permission_id=permission.id))
            await db_session.commit()

    admin = AdminUser(email=f"{role_name}-{code}@synca.conf", password_hash="hash", role_id=role.id)
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
async def test_list_campaign_windows_admin(db_session, client):
    admin = await make_admin_with_permission(
        db_session, "cw-manager", "campaign_windows.manage"
    )
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(
            "/api/admin/campaign-windows", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200
    assert len(response.json()) == 6


@pytest.mark.asyncio
async def test_list_campaign_windows_forbidden_without_permission(db_session, client):
    admin = await make_admin_with_permission(db_session, "no-cw-manage", None)
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(
            "/api/admin/campaign-windows", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_campaign_window_dates_and_is_active(db_session, client):
    admin = await make_admin_with_permission(
        db_session, "cw-manager2", "campaign_windows.manage"
    )
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.patch(
            "/api/admin/campaign-windows/ticketing",
            json={
                "start_at": "2027-01-01T00:00:00",
                "end_at": "2027-01-31T23:59:59",
                "is_active": False,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["is_active"] is False
    assert body["start_at"].startswith("2027-01-01")
    assert body["end_at"].startswith("2027-01-31")


@pytest.mark.asyncio
async def test_update_campaign_window_rejects_end_before_start(db_session, client):
    admin = await make_admin_with_permission(
        db_session, "cw-manager3", "campaign_windows.manage"
    )
    token = create_access_token(subject=str(admin.id))

    original = (
        await db_session.execute(
            select(CampaignWindow).where(CampaignWindow.key == "ticketing")
        )
    ).scalar_one()
    original_start_at = original.start_at

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.patch(
            "/api/admin/campaign-windows/ticketing",
            json={"start_at": "2099-02-01T00:00:00", "end_at": "2099-01-01T00:00:00"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 400

    await db_session.refresh(original)
    assert original.start_at == original_start_at


@pytest.mark.asyncio
async def test_update_campaign_window_unknown_key_404(db_session, client):
    admin = await make_admin_with_permission(
        db_session, "cw-manager4", "campaign_windows.manage"
    )
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.patch(
            "/api/admin/campaign-windows/not-a-real-key",
            json={"is_active": False},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_campaign_window_forbidden_without_permission(db_session, client):
    admin = await make_admin_with_permission(db_session, "no-cw-manage2", None)
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.patch(
            "/api/admin/campaign-windows/ticketing",
            json={"is_active": False},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 403
