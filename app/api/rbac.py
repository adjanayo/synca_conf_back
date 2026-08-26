from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.rbac import require_permission
from app.models import AdminUser, Permission, Role, RolePermission
from app.schemas.rbac import RoleUpdate, RoleWithPermissionsRead

router = APIRouter(prefix="/api/admin", tags=["rbac"])


@router.patch("/roles/{role_id}", response_model=RoleWithPermissionsRead)
@limiter.limit("30/minute")
async def update_role_permissions(
    request: Request,
    role_id: int,
    body: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(require_permission("roles.manage")),
) -> RoleWithPermissionsRead:
    role = await db.get(Role, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rôle introuvable.")

    permissions = (
        (await db.execute(select(Permission).where(Permission.code.in_(body.permission_codes))))
        .scalars()
        .all()
    )
    found_codes = {p.code for p in permissions}
    unknown_codes = set(body.permission_codes) - found_codes
    if unknown_codes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Codes de permission inconnus : {', '.join(sorted(unknown_codes))}.",
        )

    existing = (
        (await db.execute(select(RolePermission).where(RolePermission.role_id == role_id)))
        .scalars()
        .all()
    )
    for row in existing:
        await db.delete(row)
    await db.flush()

    for permission in permissions:
        db.add(RolePermission(role_id=role_id, permission_id=permission.id))
    await db.commit()

    logger.bind(channel="security").info(
        f"Rôle {role.name} modifié par {admin.email} : permissions = {sorted(found_codes)}"
    )

    return RoleWithPermissionsRead(
        id=role.id, name=role.name, permission_codes=sorted(found_codes)
    )
