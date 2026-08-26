import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.database import get_db
from app.main import app
from app.models import (
    AdminUser,
    Ambassador,
    Exhibitor,
    Partner,
    PartnerLevel,
    Permission,
    Role,
    RolePermission,
    Speaker,
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


async def make_speaker(db_session) -> Speaker:
    speaker = Speaker(
        first_name="Awa",
        last_name="Diop",
        title_role="CTO",
        country="Sénégal",
        email="speaker@example.com",
        phone_whatsapp="+221771234567",
        intervention_format="Keynote",
        intervention_title="IA en Afrique",
        theme="IA",
        summary="Résumé",
        motivation="Motivation",
    )
    db_session.add(speaker)
    await db_session.commit()
    return speaker


async def make_ambassador(db_session) -> Ambassador:
    ambassador = Ambassador(
        first_name="Awa",
        last_name="Diop",
        age=25,
        country="Sénégal",
        city="Dakar",
        email="ambassador@example.com",
        phone_whatsapp="+221771234567",
        motivation="Motivation",
        mobilization_plan="Plan",
        preferred_channels="LinkedIn",
    )
    db_session.add(ambassador)
    await db_session.commit()
    return ambassador


async def make_partner(db_session) -> Partner:
    level = PartnerLevel(name="Gold", price=100000)
    db_session.add(level)
    await db_session.flush()

    partner = Partner(
        organization_name="Acme",
        sector="Tech/ESN",
        country="Sénégal",
        city="Dakar",
        contact_name="Awa Diop",
        contact_position="CEO",
        contact_email="partner@example.com",
        contact_phone="+221771234567",
        level_id=level.id,
        objectives="Objectifs",
    )
    db_session.add(partner)
    await db_session.commit()
    return partner


async def make_exhibitor(db_session) -> Exhibitor:
    exhibitor = Exhibitor(
        organization_name="Acme",
        sector="Tech",
        country="Sénégal",
        city="Dakar",
        contact_name="Awa Diop",
        contact_position="CEO",
        contact_email="exhibitor@example.com",
        contact_phone="+221771234567",
        stand_type="Standard",
        reps_count=2,
        products_services="Produits",
    )
    db_session.add(exhibitor)
    await db_session.commit()
    return exhibitor


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_speaker_accepted_publishes_it(db_session, client):
    admin = await make_admin_with_permission(db_session, "speaker-approver", "speakers.approve")
    speaker = await make_speaker(db_session)
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.patch(
            f"/api/admin/speakers/{speaker.id}",
            json={"status": "accepted"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "accepted"
    assert body["is_public"] is True


@pytest.mark.asyncio
async def test_speaker_rejected_stays_unpublished(db_session, client):
    admin = await make_admin_with_permission(db_session, "speaker-approver2", "speakers.approve")
    speaker = await make_speaker(db_session)
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.patch(
            f"/api/admin/speakers/{speaker.id}",
            json={"status": "rejected"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejected"
    assert body["is_public"] is False


@pytest.mark.asyncio
async def test_speaker_update_forbidden_without_permission(db_session, client):
    admin = await make_admin_with_permission(db_session, "no-speakers-approve", None)
    speaker = await make_speaker(db_session)
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.patch(
            f"/api/admin/speakers/{speaker.id}",
            json={"status": "accepted"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_speaker_update_404_for_unknown_id(db_session, client):
    admin = await make_admin_with_permission(db_session, "speaker-approver3", "speakers.approve")
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.patch(
            "/api/admin/speakers/999999",
            json={"status": "accepted"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_speaker_update_rejects_invalid_status(db_session, client):
    admin = await make_admin_with_permission(db_session, "speaker-approver4", "speakers.approve")
    speaker = await make_speaker(db_session)
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.patch(
            f"/api/admin/speakers/{speaker.id}",
            json={"status": "not-a-real-status"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ambassador_accepted(db_session, client):
    admin = await make_admin_with_permission(
        db_session, "ambassador-approver", "ambassadors.approve"
    )
    ambassador = await make_ambassador(db_session)
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.patch(
            f"/api/admin/ambassadors/{ambassador.id}",
            json={"status": "accepted"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


@pytest.mark.asyncio
async def test_ambassador_update_forbidden_without_permission(db_session, client):
    admin = await make_admin_with_permission(db_session, "no-ambassadors-approve", None)
    ambassador = await make_ambassador(db_session)
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.patch(
            f"/api/admin/ambassadors/{ambassador.id}",
            json={"status": "accepted"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_partner_confirmed_publishes_it(db_session, client):
    admin = await make_admin_with_permission(db_session, "partner-manager", "partners.manage")
    partner = await make_partner(db_session)
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.patch(
            f"/api/admin/partners/{partner.id}",
            json={"status": "confirmed"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "confirmed"
    assert body["is_public"] is True


@pytest.mark.asyncio
async def test_partner_negotiating_stays_unpublished(db_session, client):
    admin = await make_admin_with_permission(db_session, "partner-manager2", "partners.manage")
    partner = await make_partner(db_session)
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.patch(
            f"/api/admin/partners/{partner.id}",
            json={"status": "negotiating"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "negotiating"
    assert body["is_public"] is False


@pytest.mark.asyncio
async def test_partner_update_forbidden_without_permission(db_session, client):
    admin = await make_admin_with_permission(db_session, "no-partners-manage", None)
    partner = await make_partner(db_session)
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.patch(
            f"/api/admin/partners/{partner.id}",
            json={"status": "confirmed"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_exhibitor_confirmed_publishes_it(db_session, client):
    admin = await make_admin_with_permission(db_session, "exhibitor-manager", "exhibitors.manage")
    exhibitor = await make_exhibitor(db_session)
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.patch(
            f"/api/admin/exhibitors/{exhibitor.id}",
            json={"status": "confirmed"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "confirmed"
    assert body["is_public"] is True


@pytest.mark.asyncio
async def test_exhibitor_update_forbidden_without_permission(db_session, client):
    admin = await make_admin_with_permission(db_session, "no-exhibitors-manage", None)
    exhibitor = await make_exhibitor(db_session)
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.patch(
            f"/api/admin/exhibitors/{exhibitor.id}",
            json={"status": "confirmed"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 403
