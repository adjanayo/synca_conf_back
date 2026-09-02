import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models import OtpCode, User
from app.services.email_service import send_email
from app.services.email_templates import otp_login_email

OTP_LENGTH = 6
OTP_TTL_MINUTES = 10
OTP_MAX_ATTEMPTS = 5

# Same anti-enumeration posture as auth_service._DUMMY_PASSWORD_HASH: exercised
# on the "no such account" path in verify_otp so timing doesn't reveal
# whether an email has an account.
_DUMMY_OTP_HASH = hash_password("no-such-account-dummy-otp-comparison-target")


class InvalidOtpError(Exception):
    pass


def _generate_code() -> str:
    return "".join(secrets.choice("0123456789") for _ in range(OTP_LENGTH))


async def request_otp(db: AsyncSession, email: str) -> None:
    """Create + email a login code if the address matches a verified account.

    Silent no-op otherwise -- the router always answers with the same
    generic 200 regardless (security-hardening: customer access codes get
    the identical response whether or not the account exists).
    """
    user = (
        await db.execute(select(User).where(User.email == email, User.email_verified.is_(True)))
    ).scalar_one_or_none()
    if user is None:
        return

    code = _generate_code()
    db.add(
        OtpCode(
            user_id=user.id,
            code_hash=hash_password(code),
            expires_at=datetime.now(UTC) + timedelta(minutes=OTP_TTL_MINUTES),
        )
    )
    await db.commit()

    await send_email(
        user.email,
        "Votre code de connexion SYNCA CONF 2027",
        otp_login_email(user.first_name, code),
    )


async def verify_otp(db: AsyncSession, email: str, code: str) -> User:
    """Consume the most recent unexpired, unconsumed code for this email.

    Every failure path (unknown email, no active code, expired, too many
    attempts, wrong code) raises the same InvalidOtpError with the same
    generic message -- no signal to a caller distinguishing them.
    """
    invalid = InvalidOtpError("Code invalide ou expiré.")

    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if user is None:
        verify_password(code, _DUMMY_OTP_HASH)
        raise invalid

    otp = (
        await db.execute(
            select(OtpCode)
            .where(OtpCode.user_id == user.id, OtpCode.consumed_at.is_(None))
            .order_by(OtpCode.created_at.desc())
        )
    ).scalars().first()

    now = datetime.now(UTC)
    if otp is None or otp.expires_at.replace(tzinfo=UTC) < now:
        raise invalid

    if otp.attempts >= OTP_MAX_ATTEMPTS:
        otp.consumed_at = now
        await db.commit()
        raise invalid

    otp.attempts += 1
    if not verify_password(code, otp.code_hash):
        await db.commit()
        raise invalid

    otp.consumed_at = now
    await db.commit()
    return user
