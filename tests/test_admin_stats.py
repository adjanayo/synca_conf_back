import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.database import get_db
from app.main import app
from app.models import (
    AdminUser,
    PassType,
    Payment,
    Permission,
    PromoCode,
    Role,
    RolePermission,
    Speaker,
    Ticket,
    User,
)
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


async def make_user_and_pass_type(db_session) -> tuple[User, PassType]:
    unique = uuid.uuid4().hex[:8]
    user = User(
        first_name="Awa",
        last_name="Diop",
        email=f"stats-{unique}@example.com",
        phone_whatsapp="+221771234567",
        country="Sénégal",
        city="Dakar",
        gdpr_consent=True,
        newsletter_consent=False,
    )
    pass_type = PassType(name=f"Standard-{unique}", price=15000, is_active=True)
    db_session.add_all([user, pass_type])
    await db_session.flush()
    return user, pass_type


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_stats_computed_from_payments_tickets_and_applications(db_session, client):
    admin = await make_admin_with_permission(db_session, "stats-viewer", "payments.view")

    promo = PromoCode(code="STATS10", discount_pct=10, is_active=True)
    db_session.add(promo)
    await db_session.flush()

    user1, pass_type1 = await make_user_and_pass_type(db_session)
    payment1 = Payment(
        user_id=user1.id,
        pass_type_id=pass_type1.id,
        promo_code_id=promo.id,
        amount_original=15000,
        amount_paid=13500,
        payment_method="wave",
        status="completed",
    )
    db_session.add(payment1)
    await db_session.flush()
    db_session.add(Ticket(user_id=user1.id, payment_id=payment1.id, pass_type_id=pass_type1.id,
                           ticket_number=f"SYNCA-{payment1.id:06d}", qr_code_hash="hash1"))

    user2, pass_type2 = await make_user_and_pass_type(db_session)
    payment2 = Payment(
        user_id=user2.id,
        pass_type_id=pass_type2.id,
        amount_original=15000,
        amount_paid=15000,
        payment_method="wave",
        status="completed",
    )
    db_session.add(payment2)
    await db_session.flush()
    db_session.add(Ticket(user_id=user2.id, payment_id=payment2.id, pass_type_id=pass_type2.id,
                           ticket_number=f"SYNCA-{payment2.id:06d}", qr_code_hash="hash2"))

    user3, pass_type3 = await make_user_and_pass_type(db_session)
    pending_payment = Payment(
        user_id=user3.id,
        pass_type_id=pass_type3.id,
        amount_original=15000,
        amount_paid=15000,
        payment_method="wave",
        status="pending",
    )
    db_session.add(pending_payment)

    db_session.add(
        Speaker(
            first_name="Awa",
            last_name="Diop",
            title_role="CTO",
            country="Sénégal",
            email="speaker-stats@example.com",
            phone_whatsapp="+221771234567",
            intervention_format="Keynote",
            intervention_title="IA en Afrique",
            theme="IA",
            summary="Résumé",
            motivation="Motivation",
            status="accepted",
        )
    )
    await db_session.commit()

    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(
            "/api/admin/stats", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200
    body = response.json()
    assert body["total_registrations"] >= 2
    assert body["completed_payments"] >= 2
    assert body["payments_with_promo"] >= 1
    assert body["total_revenue"] >= 13500 + 15000
    assert 0 < body["promo_conversion_rate"] <= 1
    assert body["applications_by_status"]["speakers"]["accepted"] >= 1


@pytest.mark.asyncio
async def test_stats_forbidden_without_permission(db_session, client):
    admin = await make_admin_with_permission(db_session, "no-payments-view", None)
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(
            "/api/admin/stats", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_stats_handles_no_completed_payments(db_session, client):
    admin = await make_admin_with_permission(db_session, "stats-viewer2", "payments.view")
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(
            "/api/admin/stats", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200
    body = response.json()
    assert body["promo_conversion_rate"] == 0.0
