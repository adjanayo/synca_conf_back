import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.database import get_db
from app.main import app
from app.models import AdminUser, PassType, Payment, Permission, Role, RolePermission, User
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
    # status/created_at are server_default-only -- unloaded on the Python
    # object after commit. Refresh now so a later sync attribute access
    # (e.g. Pydantic model_validate) doesn't trigger a lazy load outside the
    # async/greenlet context.
    await db_session.refresh(admin)
    return admin


async def make_payment(db_session, status: str) -> Payment:
    unique = uuid.uuid4().hex[:8]
    user = User(
        first_name="Awa",
        last_name="Diop",
        email=f"reg-{unique}@example.com",
        phone_whatsapp="+221771234567",
        country="Sénégal",
        city="Dakar",
        gdpr_consent=True,
        newsletter_consent=False,
    )
    pass_type = PassType(name=f"Standard-{unique}", price=15000, is_active=True)
    db_session.add_all([user, pass_type])
    await db_session.flush()

    payment = Payment(
        user_id=user.id,
        pass_type_id=pass_type.id,
        amount_original=15000,
        amount_paid=15000,
        payment_method="wave",
        status=status,
    )
    db_session.add(payment)
    await db_session.commit()
    return payment


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_registrations_returns_all_by_default(db_session, client):
    admin = await make_admin_with_permission(db_session, "reg-viewer", "payments.view")
    await make_payment(db_session, "completed")
    await make_payment(db_session, "pending")
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(
            "/api/admin/registrations", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200
    assert len(response.json()) >= 2


@pytest.mark.asyncio
async def test_list_registrations_filters_by_status(db_session, client):
    admin = await make_admin_with_permission(db_session, "reg-viewer2", "payments.view")
    completed = await make_payment(db_session, "completed")
    await make_payment(db_session, "pending")
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(
            "/api/admin/registrations?payment_status=completed",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    body = response.json()
    assert all(row["status"] == "completed" for row in body)
    assert any(row["payment_id"] == completed.id for row in body)


@pytest.mark.asyncio
async def test_list_registrations_respects_pagination_limit(db_session, client):
    admin = await make_admin_with_permission(db_session, "reg-viewer3", "payments.view")
    for _ in range(3):
        await make_payment(db_session, "completed")
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(
            "/api/admin/registrations?limit=1", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_list_registrations_forbidden_without_permission(db_session, client):
    admin = await make_admin_with_permission(db_session, "no-payments-view-reg", None)
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(
            "/api/admin/registrations", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 403
