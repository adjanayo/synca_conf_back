import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.database import get_db
from app.main import app
from app.models import AdminUser, ContactMessage, Role
from app.services.auth_service import create_access_token


async def make_admin(db_session, role_name: str) -> AdminUser:
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
async def test_any_authenticated_admin_can_list_contacts(db_session, client):
    admin = await make_admin(db_session, "support")
    db_session.add(ContactMessage(name="Awa", email="awa@example.com", message="Bonjour"))
    await db_session.commit()
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(
            "/api/admin/contacts", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_list_contacts_filters_by_is_read(db_session, client):
    admin = await make_admin(db_session, "support2")
    db_session.add_all(
        [
            ContactMessage(name="Awa", email="awa@example.com", message="Non lu", is_read=False),
            ContactMessage(name="Awa", email="awa@example.com", message="Lu", is_read=True),
        ]
    )
    await db_session.commit()
    token = create_access_token(subject=str(admin.id))

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(
            "/api/admin/contacts?is_read=false", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200
    body = response.json()
    assert all(row["is_read"] is False for row in body)


@pytest.mark.asyncio
async def test_list_contacts_requires_authentication(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get("/api/admin/contacts")

    assert response.status_code == 401
