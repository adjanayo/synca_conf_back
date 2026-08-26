import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.main import app
from app.models import PassType, Payment, Ticket, User


async def make_user(
    db_session, access_token: str = "test-token-abc", email: str = "me@example.com"
) -> User:
    user = User(
        first_name="Awa",
        last_name="Diop",
        email=email,
        phone_whatsapp="+221771234567",
        country="Sénégal",
        city="Dakar",
        gdpr_consent=True,
        newsletter_consent=True,
        access_token=access_token,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_me_returns_own_data(db_session, client):
    await make_user(db_session)

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(
            "/api/user/me", headers={"Authorization": "Bearer test-token-abc"}
        )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "me@example.com"
    assert "access_token" not in body


@pytest.mark.asyncio
async def test_get_me_rejects_invalid_token(db_session, client):
    await make_user(db_session)

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(
            "/api/user/me", headers={"Authorization": "Bearer wrong-token"}
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_requires_authorization_header(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get("/api/user/me")

    assert response.status_code == 401


async def make_ticket_for(db_session, user: User, ticket_number: str) -> Ticket:
    pass_type = PassType(name=f"Standard-{ticket_number}", price=15000, is_active=True)
    db_session.add(pass_type)
    await db_session.flush()

    payment = Payment(
        user_id=user.id,
        pass_type_id=pass_type.id,
        amount_original=15000,
        amount_paid=15000,
        payment_method="wave",
        status="completed",
    )
    db_session.add(payment)
    await db_session.flush()

    ticket = Ticket(
        user_id=user.id,
        payment_id=payment.id,
        pass_type_id=pass_type.id,
        ticket_number=ticket_number,
        qr_code_hash=f"hash-{ticket_number}",
        pdf_url=f"https://cdn.example.com/{ticket_number}.pdf",
    )
    db_session.add(ticket)
    await db_session.commit()
    return ticket


@pytest.mark.asyncio
async def test_get_my_tickets_returns_only_own_tickets(db_session, client):
    owner = await make_user(db_session, access_token="owner-token")
    other = await make_user(db_session, access_token="other-token", email="other@example.com")
    await make_ticket_for(db_session, owner, "SYNCA-000001")
    await make_ticket_for(db_session, other, "SYNCA-000002")

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(
            "/api/user/me/tickets", headers={"Authorization": "Bearer owner-token"}
        )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["ticket_number"] == "SYNCA-000001"
    assert body[0]["pdf_url"] == "https://cdn.example.com/SYNCA-000001.pdf"


@pytest.mark.asyncio
async def test_get_my_tickets_rejects_invalid_token(db_session, client):
    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.get(
            "/api/user/me/tickets", headers={"Authorization": "Bearer wrong-token"}
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_me_anonymizes_and_revokes_token(db_session, client):
    user = await make_user(db_session)

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.delete(
            "/api/user/me", headers={"Authorization": "Bearer test-token-abc"}
        )

    assert response.status_code == 200

    await db_session.refresh(user)
    assert user.first_name == "Anonymisé"
    assert user.email == f"anonymized-{user.id}@deleted.synca.conf"
    assert user.access_token is None


@pytest.mark.asyncio
async def test_delete_me_token_cannot_be_reused(db_session, client):
    await make_user(db_session)

    async with AsyncClient(transport=client, base_url="http://test") as http:
        first = await http.delete(
            "/api/user/me", headers={"Authorization": "Bearer test-token-abc"}
        )
        second = await http.delete(
            "/api/user/me", headers={"Authorization": "Bearer test-token-abc"}
        )

    assert first.status_code == 200
    assert second.status_code == 401
