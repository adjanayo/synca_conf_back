import pytest
from sqlalchemy.exc import IntegrityError

from app.models import User, UserProfile


def make_user(**overrides) -> User:
    defaults = dict(
        first_name="Awa",
        last_name="Diop",
        email="awa.diop@example.com",
        phone_whatsapp="+221771234567",
        country="Sénégal",
        city="Dakar",
        gdpr_consent=True,
        newsletter_consent=False,
    )
    defaults.update(overrides)
    return User(**defaults)


@pytest.mark.asyncio
async def test_user_email_unique(db_session):
    db_session.add(make_user())
    await db_session.commit()

    db_session.add(make_user(email="awa.diop@example.com", first_name="Doublon"))
    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_user_profile_unique_pair(db_session):
    user = make_user(email="fatou@example.com")
    db_session.add(user)
    await db_session.flush()

    db_session.add(UserProfile(user_id=user.id, profile="Étudiant"))
    await db_session.commit()

    db_session.add(UserProfile(user_id=user.id, profile="Étudiant"))
    with pytest.raises(IntegrityError):
        await db_session.commit()
