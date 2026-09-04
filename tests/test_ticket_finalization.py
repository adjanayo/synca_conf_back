from contextlib import asynccontextmanager

import pytest

from app.models import PassType, Payment, Ticket, User
from app.models.referentials import EventSettings
from app.services import ticket_finalization


async def make_ticket(db_session) -> Ticket:
    # Force deterministic EventSettings for this test's SAVEPOINT-isolated
    # session (rolled back at teardown, doesn't touch the real seeded row) --
    # a row may already exist for real (id=1), so update it rather than
    # skipping when present.
    settings = await db_session.get(EventSettings, 1)
    if settings is None:
        db_session.add(
            EventSettings(id=1, name="Synca Conf", venue="Dakar, Sénégal", year=2027)
        )
    else:
        settings.name = "Synca Conf"
        settings.venue = "Dakar, Sénégal"
        settings.year = 2027

    user = User(
        first_name="Awa",
        last_name="Diop",
        email="finalize@example.com",
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
        status="completed",
    )
    db_session.add(payment)
    await db_session.flush()

    ticket = Ticket(
        user_id=user.id,
        payment_id=payment.id,
        pass_type_id=pass_type.id,
        ticket_number="SYNCA-000001",
        qr_code_hash="hash123",
    )
    db_session.add(ticket)
    await db_session.commit()
    await db_session.refresh(ticket)
    return ticket


@pytest.fixture(autouse=True)
def _use_test_session(monkeypatch, db_session):
    # finalize_ticket opens its own AsyncSessionLocal() connection, which
    # can't see rows created inside this test's SAVEPOINT-isolated
    # db_session. Reuse the same session here so the test can observe the
    # actual finalization logic, not just a no-op on invisible data.
    @asynccontextmanager
    async def _fake_session_local():
        yield db_session

    monkeypatch.setattr(ticket_finalization, "AsyncSessionLocal", _fake_session_local)


@pytest.mark.asyncio
async def test_finalize_ticket_sets_pdf_url_and_sends_email(db_session, monkeypatch):
    ticket = await make_ticket(db_session)

    async def fake_generate_and_upload(
        ticket_number, qr_code_hash, attendee_name, pass_type_name, event_name, venue
    ):
        assert ticket_number == "SYNCA-000001"
        assert qr_code_hash == "hash123"
        assert attendee_name == "Awa Diop"
        assert pass_type_name == "Standard"
        assert event_name == "Synca Conf 2027"
        assert venue == "Dakar, Sénégal"
        return "https://cdn.example.com/SYNCA-000001.pdf"

    sent_emails = []

    async def fake_send_email(to, subject, body):
        sent_emails.append((to, subject, body))

    monkeypatch.setattr(
        ticket_finalization, "generate_and_upload_ticket_pdf", fake_generate_and_upload
    )
    monkeypatch.setattr(ticket_finalization, "send_email", fake_send_email)

    await ticket_finalization.finalize_ticket(ticket.id)

    await db_session.refresh(ticket)
    assert ticket.pdf_url == "https://cdn.example.com/SYNCA-000001.pdf"
    assert len(sent_emails) == 1
    assert sent_emails[0][0] == "finalize@example.com"
    assert "SYNCA-000001" in sent_emails[0][2]


@pytest.mark.asyncio
async def test_finalize_ticket_is_idempotent_when_already_finalized(db_session, monkeypatch):
    ticket = await make_ticket(db_session)
    ticket.pdf_url = "https://cdn.example.com/already-there.pdf"
    await db_session.commit()

    calls = {"generate": 0, "email": 0}

    async def fake_generate_and_upload(*args, **kwargs):
        calls["generate"] += 1
        return "should-not-be-used.pdf"

    async def fake_send_email(*args, **kwargs):
        calls["email"] += 1

    monkeypatch.setattr(
        ticket_finalization, "generate_and_upload_ticket_pdf", fake_generate_and_upload
    )
    monkeypatch.setattr(ticket_finalization, "send_email", fake_send_email)

    await ticket_finalization.finalize_ticket(ticket.id)

    assert calls == {"generate": 0, "email": 0}


@pytest.mark.asyncio
async def test_finalize_ticket_noops_on_missing_ticket(db_session, monkeypatch):
    calls = {"generate": 0}

    async def fake_generate_and_upload(*args, **kwargs):
        calls["generate"] += 1
        return "unused.pdf"

    monkeypatch.setattr(
        ticket_finalization, "generate_and_upload_ticket_pdf", fake_generate_and_upload
    )

    await ticket_finalization.finalize_ticket(999999)

    assert calls["generate"] == 0
