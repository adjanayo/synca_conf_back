import pytest
from sqlalchemy import select

from app.models import AuditLog
from app.services.auth_service import (
    AccountLockedError,
    InvalidCredentialsError,
    authenticate_admin,
)
from tests.test_admin_login import make_admin


@pytest.mark.asyncio
async def test_successful_login_writes_audit_entry(db_session):
    admin = await make_admin(db_session, "audit-success@synca.conf")

    await authenticate_admin(db_session, admin.email, "correct horse battery staple", "1.2.3.4")

    logs = (
        await db_session.execute(select(AuditLog).where(AuditLog.email == admin.email))
    ).scalars().all()
    assert len(logs) == 1
    assert logs[0].success is True
    assert logs[0].ip_address == "1.2.3.4"


@pytest.mark.asyncio
async def test_failed_login_writes_audit_entry(db_session):
    admin = await make_admin(db_session, "audit-fail@synca.conf")

    with pytest.raises(InvalidCredentialsError):
        await authenticate_admin(db_session, admin.email, "wrong", "5.6.7.8")

    logs = (
        await db_session.execute(select(AuditLog).where(AuditLog.email == admin.email))
    ).scalars().all()
    assert len(logs) == 1
    assert logs[0].success is False
    assert logs[0].ip_address == "5.6.7.8"


@pytest.mark.asyncio
async def test_locked_account_attempt_writes_audit_entry(db_session):
    admin = await make_admin(db_session, "audit-locked@synca.conf")

    for _ in range(5):
        with pytest.raises(InvalidCredentialsError):
            await authenticate_admin(db_session, admin.email, "wrong")

    with pytest.raises(AccountLockedError):
        await authenticate_admin(db_session, admin.email, "correct horse battery staple")

    logs = (
        await db_session.execute(select(AuditLog).where(AuditLog.email == admin.email))
    ).scalars().all()
    assert len(logs) == 6
    assert all(log.success is False for log in logs)
