import pytest
from sqlalchemy import text

from app.models import User


async def make_user(db_session) -> User:
    user = User(
        first_name="Awa",
        last_name="Diop",
        email="crypto@example.com",
        phone_whatsapp="+221771234567",
        country="Sénégal",
        city="Dakar",
        special_needs="Fauteuil roulant",
        gdpr_consent=True,
        newsletter_consent=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_orm_read_returns_plaintext(db_session):
    user = await make_user(db_session)

    assert user.phone_whatsapp == "+221771234567"
    assert user.special_needs == "Fauteuil roulant"


@pytest.mark.asyncio
async def test_raw_db_row_is_not_plaintext(db_session):
    user = await make_user(db_session)

    row = (
        await db_session.execute(
            text("SELECT phone_whatsapp, special_needs FROM users WHERE id = :id"),
            {"id": user.id},
        )
    ).one()

    assert row.phone_whatsapp != "+221771234567"
    assert "+221771234567" not in row.phone_whatsapp
    assert row.special_needs != "Fauteuil roulant"
    assert "Fauteuil roulant" not in row.special_needs


@pytest.mark.asyncio
async def test_null_special_needs_stays_null(db_session):
    user = User(
        first_name="Moussa",
        last_name="Ba",
        email="crypto-null@example.com",
        phone_whatsapp="+221770000000",
        country="Sénégal",
        city="Dakar",
        gdpr_consent=True,
        newsletter_consent=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.special_needs is None
