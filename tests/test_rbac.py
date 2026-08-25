import pytest
from sqlalchemy import func, select

from app.models import AdminUser, Permission, Role, RolePermission


@pytest.mark.asyncio
async def test_seeded_roles_and_permissions(db_session):
    role_names = (await db_session.execute(select(Role.name))).scalars().all()
    assert set(role_names) == {"superadmin", "admin", "editor", "support"}

    permission_count = (await db_session.execute(select(func.count(Permission.id)))).scalar_one()
    assert permission_count == 8

    superadmin_id = (
        await db_session.execute(select(Role.id).where(Role.name == "superadmin"))
    ).scalar_one()
    superadmin_permission_count = (
        await db_session.execute(
            select(func.count(RolePermission.id)).where(RolePermission.role_id == superadmin_id)
        )
    ).scalar_one()
    assert superadmin_permission_count == permission_count


@pytest.mark.asyncio
async def test_admin_user_requires_permission_only_superadmin(db_session):
    superadmin_id = (
        await db_session.execute(select(Role.id).where(Role.name == "superadmin"))
    ).scalar_one()

    admin_user = AdminUser(
        email="admin@synca.conf",
        password_hash="not-a-real-hash",
        role_id=superadmin_id,
    )
    db_session.add(admin_user)
    await db_session.commit()

    role_name = (
        await db_session.execute(
            select(Role.name).join(AdminUser, AdminUser.role_id == Role.id).where(
                AdminUser.id == admin_user.id
            )
        )
    ).scalar_one()
    assert role_name == "superadmin"
