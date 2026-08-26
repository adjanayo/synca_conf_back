import csv
import io
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
    return admin


async def make_payment(db_session, status: str) -> Payment:
    unique = uuid.uuid4().hex[:8]
    user = User(
        first_name="Awa",
        last_name="Diop",
        email=f"export-{unique}@example.com",
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
async def test_export_registrations_csv(db_session, client):
    admin = await make_admin_with_permission(db_session, "export-admin", "export.data")
    payment = await make_payment(db_session, "completed")
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(
            "/api/admin/export/registrations", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment" in response.headers["content-disposition"]

    reader = csv.reader(io.StringIO(response.text))
    rows = list(reader)
    assert rows[0] == [
        "payment_id",
        "user_name",
        "user_email",
        "pass_type_name",
        "amount_paid",
        "status",
        "ticket_number",
        "created_at",
    ]
    assert any(row[0] == str(payment.id) for row in rows[1:])


@pytest.mark.asyncio
async def test_export_registrations_forbidden_without_permission(db_session, client):
    admin = await make_admin_with_permission(db_session, "no-export-data", None)
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(
            "/api/admin/export/registrations", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_export_payments_csv(db_session, client):
    admin = await make_admin_with_permission(db_session, "export-admin2", "export.data")
    payment = await make_payment(db_session, "completed")
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(
            "/api/admin/export/payments", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200
    reader = csv.reader(io.StringIO(response.text))
    rows = list(reader)
    assert rows[0][0] == "payment_id"
    assert any(row[0] == str(payment.id) for row in rows[1:])


@pytest.mark.asyncio
async def test_export_payments_forbidden_without_permission(db_session, client):
    admin = await make_admin_with_permission(db_session, "no-export-data2", None)
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(
            "/api/admin/export/payments", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 403
