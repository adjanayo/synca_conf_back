import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.deps.rbac import get_current_admin, require_permission
from app.models import AdminUser, Permission, Role, RolePermission
from app.services.auth_service import create_access_token


async def make_admin_with_role(db_session, role_name: str) -> AdminUser:
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
    # status/created_at are server_default-only -- unloaded on the Python
    # object after commit. Refresh now so a later sync attribute access
    # (e.g. Pydantic model_validate) doesn't trigger a lazy load outside the
    # async/greenlet context.
    await db_session.refresh(admin)
    return admin


@pytest.mark.asyncio
async def test_get_current_admin_valid_token(db_session):
    admin = await make_admin_with_role(db_session, "editor")
    token = create_access_token(subject=str(admin.id))

    resolved = await get_current_admin(token=token, db=db_session)
    assert resolved.id == admin.id


@pytest.mark.asyncio
async def test_get_current_admin_missing_token_raises_401(db_session):
    with pytest.raises(HTTPException) as exc_info:
        await get_current_admin(token=None, db=db_session)
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_admin_invalid_token_raises_401(db_session):
    with pytest.raises(HTTPException) as exc_info:
        await get_current_admin(token="not-a-real-token", db=db_session)
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_require_permission_granted(db_session):
    admin = await make_admin_with_role(db_session, "support_with_perm")
    permission = Permission(code="widgets.view")
    db_session.add(permission)
    await db_session.flush()
    db_session.add(RolePermission(role_id=admin.role_id, permission_id=permission.id))
    await db_session.commit()

    checker = require_permission("widgets.view")
    resolved = await checker(admin=admin, db=db_session)
    assert resolved.id == admin.id


@pytest.mark.asyncio
async def test_require_permission_denied_returns_403(db_session):
    admin = await make_admin_with_role(db_session, "support_no_perm")

    checker = require_permission("widgets.delete")
    with pytest.raises(HTTPException) as exc_info:
        await checker(admin=admin, db=db_session)
    assert exc_info.value.status_code == 403
