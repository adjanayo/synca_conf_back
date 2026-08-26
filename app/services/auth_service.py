from datetime import UTC, datetime, timedelta
from typing import Literal

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import hash_password, verify_password
from app.models import AdminUser

settings = get_settings()

LOCKOUT_THRESHOLD = 5
LOCKOUT_BASE_MINUTES = 15
LOCKOUT_MAX_MINUTES = 240

# A real Argon2 hash of an unguessable value, computed once at import time,
# used as the comparison target when the email doesn't exist -- keeps the
# unknown-email path exercising the same hashing work as a real check.
_DUMMY_PASSWORD_HASH = hash_password("no-such-account-dummy-hash-comparison-target")


class InvalidTokenError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class AccountLockedError(Exception):
    pass


async def authenticate_admin(db: AsyncSession, email: str, password: str) -> AdminUser:
    """Verify admin credentials, enforcing the account-lockout policy.

    Always takes the same code path (hash a dummy value) when the email
    doesn't exist, so response timing doesn't reveal account existence.
    """
    admin = (
        await db.execute(select(AdminUser).where(AdminUser.email == email))
    ).scalar_one_or_none()

    now = datetime.now(UTC)
    if admin and admin.locked_until and admin.locked_until.replace(tzinfo=UTC) > now:
        raise AccountLockedError("Compte temporairement verrouillé, réessayez plus tard.")

    password_hash = admin.password_hash if admin else _DUMMY_PASSWORD_HASH
    is_valid = verify_password(password, password_hash)

    if not admin or not is_valid:
        if admin:
            admin.failed_login_attempts += 1
            if admin.failed_login_attempts >= LOCKOUT_THRESHOLD:
                minutes = min(
                    LOCKOUT_BASE_MINUTES * 2 ** (admin.failed_login_attempts - LOCKOUT_THRESHOLD),
                    LOCKOUT_MAX_MINUTES,
                )
                admin.locked_until = now + timedelta(minutes=minutes)
            await db.commit()
        raise InvalidCredentialsError("Email ou mot de passe incorrect.")

    admin.failed_login_attempts = 0
    admin.locked_until = None
    admin.last_login = now
    await db.commit()
    await db.refresh(admin)
    return admin


def _create_token(
    subject: str, expires_delta: timedelta, token_type: Literal["access", "refresh"]
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str) -> str:
    return _create_token(
        subject, timedelta(minutes=settings.access_token_expire_minutes), "access"
    )


def create_refresh_token(subject: str) -> str:
    return _create_token(subject, timedelta(days=settings.refresh_token_expire_days), "refresh")


def decode_token(token: str, expected_type: Literal["access", "refresh"]) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.InvalidTokenError as exc:
        raise InvalidTokenError(str(exc)) from exc

    if payload.get("type") != expected_type:
        raise InvalidTokenError(f"expected a {expected_type} token")

    return payload
