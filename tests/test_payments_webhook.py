import hashlib
import hmac
import time
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select

from app.core.database import get_db
from app.main import app
from app.models import PassType, Payment, Ticket, User

WAVE_SECRET = "wave-test-secret"
STRIPE_SECRET = "stripe-test-secret"


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield ASGITransport(app=app)
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def _webhook_secrets():
    with patch("app.api.payments.get_settings") as mock_settings:
        mock_settings.return_value.wave_webhook_secret = WAVE_SECRET
        mock_settings.return_value.stripe_webhook_secret = STRIPE_SECRET
        mock_settings.return_value.orange_money_webhook_secret = "orange-test-secret"
        yield


async def make_pending_payment(db_session) -> Payment:
    user = User(
        first_name="Awa",
        last_name="Diop",
        email="webhook@example.com",
        phone_whatsapp="+221771234567",
        country="Sénégal",
        city="Dakar",
        gdpr_consent=True,
        newsletter_consent=False,
    )
    pass_type = PassType(name="Standard", price=15000, is_active=True)
    db_session.add_all([user, pass_type])
    await db_session.flush()

    payment = Payment(
        user_id=user.id,
        pass_type_id=pass_type.id,
        amount_original=15000,
        amount_paid=15000,
        payment_method="wave",
    )
    db_session.add(payment)
    await db_session.commit()
    return payment


def wave_signature(body: bytes) -> str:
    return hmac.new(WAVE_SECRET.encode(), body, hashlib.sha256).hexdigest()


def stripe_signature(body: bytes) -> str:
    timestamp = str(int(time.time()))
    signed_payload = f"{timestamp}.".encode() + body
    sig = hmac.new(STRIPE_SECRET.encode(), signed_payload, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={sig}"


@pytest.mark.asyncio
async def test_webhook_invalid_signature_401(db_session, client):
    payment = await make_pending_payment(db_session)
    body = (
        f'{{"payment_id": {payment.id}, "transaction_ref": "ref1", "status": "completed"}}'
    ).encode()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/payments/webhook/wave",
            content=body,
            headers={"X-Webhook-Signature": "totally-wrong"},
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_webhook_completes_payment_and_creates_ticket(db_session, client):
    payment = await make_pending_payment(db_session)
    body = (
        f'{{"payment_id": {payment.id}, "transaction_ref": "ref-success", "status": "completed"}}'
    ).encode()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/payments/webhook/wave",
            content=body,
            headers={"X-Webhook-Signature": wave_signature(body)},
        )

    assert response.status_code == 200

    await db_session.refresh(payment)
    assert payment.status == "completed"
    assert payment.transaction_ref == "ref-success"

    ticket = (
        await db_session.execute(select(Ticket).where(Ticket.payment_id == payment.id))
    ).scalar_one()
    assert ticket.ticket_number == f"SYNCA-{payment.id:06d}"


@pytest.mark.asyncio
async def test_webhook_replay_is_idempotent(db_session, client):
    payment = await make_pending_payment(db_session)
    body = (
        f'{{"payment_id": {payment.id}, "transaction_ref": "ref-replay", "status": "completed"}}'
    ).encode()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        first = await http.post(
            "/api/payments/webhook/wave",
            content=body,
            headers={"X-Webhook-Signature": wave_signature(body)},
        )
        second = await http.post(
            "/api/payments/webhook/wave",
            content=body,
            headers={"X-Webhook-Signature": wave_signature(body)},
        )

    assert first.status_code == 200
    assert second.status_code == 200

    ticket_count = (
        await db_session.execute(
            select(func.count(Ticket.id)).where(Ticket.payment_id == payment.id)
        )
    ).scalar_one()
    assert ticket_count == 1


@pytest.mark.asyncio
async def test_webhook_failed_status_marks_payment_failed(db_session, client):
    payment = await make_pending_payment(db_session)
    body = (
        f'{{"payment_id": {payment.id}, "transaction_ref": "ref-fail", "status": "failed"}}'
    ).encode()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/payments/webhook/wave",
            content=body,
            headers={"X-Webhook-Signature": wave_signature(body)},
        )

    assert response.status_code == 200
    await db_session.refresh(payment)
    assert payment.status == "failed"


@pytest.mark.asyncio
async def test_webhook_unknown_payment_404(db_session, client):
    body = b'{"payment_id": 999999, "transaction_ref": "ref", "status": "completed"}'

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/payments/webhook/wave",
            content=body,
            headers={"X-Webhook-Signature": wave_signature(body)},
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_webhook_stripe_valid_signature_accepted(db_session, client):
    payment = await make_pending_payment(db_session)
    body = (
        f'{{"payment_id": {payment.id}, "transaction_ref": "ref-stripe", "status": "completed"}}'
    ).encode()

    async with AsyncClient(transport=client, base_url="http://test") as http:
        response = await http.post(
            "/api/payments/webhook/stripe",
            content=body,
            headers={"Stripe-Signature": stripe_signature(body)},
        )

    assert response.status_code == 200
