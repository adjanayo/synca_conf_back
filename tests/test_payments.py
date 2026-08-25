import pytest
from sqlalchemy.exc import IntegrityError

from app.models import PassType, Payment, PromoCode, Ticket, User, Waitlist


async def make_user_and_pass(db_session) -> tuple[User, PassType]:
    user = User(
        first_name="Awa",
        last_name="Diop",
        email="awa@example.com",
        phone_whatsapp="+221771234567",
        country="Sénégal",
        city="Dakar",
        gdpr_consent=True,
        newsletter_consent=False,
    )
    pass_type = PassType(name="Standard", price=15000)
    db_session.add_all([user, pass_type])
    await db_session.flush()
    return user, pass_type


@pytest.mark.asyncio
async def test_payment_requires_valid_fk(db_session):
    payment = Payment(
        user_id=999999,
        pass_type_id=999999,
        amount_original=15000,
        amount_paid=15000,
        payment_method="wave",
    )
    db_session.add(payment)
    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_payment_default_status_pending(db_session):
    user, pass_type = await make_user_and_pass(db_session)
    payment = Payment(
        user_id=user.id,
        pass_type_id=pass_type.id,
        amount_original=15000,
        amount_paid=15000,
        payment_method="wave",
    )
    db_session.add(payment)
    await db_session.commit()
    await db_session.refresh(payment)

    assert payment.status == "pending"


@pytest.mark.asyncio
async def test_ticket_one_per_payment(db_session):
    user, pass_type = await make_user_and_pass(db_session)
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

    db_session.add(
        Ticket(
            user_id=user.id,
            payment_id=payment.id,
            pass_type_id=pass_type.id,
            ticket_number="SYNCA-0001",
            qr_code_hash="hash-1",
        )
    )
    await db_session.commit()

    db_session.add(
        Ticket(
            user_id=user.id,
            payment_id=payment.id,
            pass_type_id=pass_type.id,
            ticket_number="SYNCA-0002",
            qr_code_hash="hash-2",
        )
    )
    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_promo_code_and_waitlist_unique(db_session):
    db_session.add(PromoCode(code="AMBASSADOR1", discount_pct=10))
    db_session.add(Waitlist(email="attente@example.com"))
    await db_session.commit()

    db_session.add(Waitlist(email="attente@example.com"))
    with pytest.raises(IntegrityError):
        await db_session.commit()
