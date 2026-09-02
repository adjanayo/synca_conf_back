from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.security import (
    WeakPasswordError,
    hash_password,
    validate_password_strength,
)
from app.deps.pagination import Pagination, pagination_params
from app.deps.rbac import require_permission
from app.models import AdminUser, Role
from app.schemas.admin_users import AdminUserCreate, AdminUserRead, AdminUserUpdate

router = APIRouter(prefix="/api/admin/users", tags=["admin-users"])


async def _to_read(db: AsyncSession, admin: AdminUser) -> AdminUserRead:
    role = await db.get(Role, admin.role_id)
    return AdminUserRead(
        id=admin.id,
        email=admin.email,
        role_id=admin.role_id,
        role_name=role.name if role else "",
        status=admin.status,
        last_login=admin.last_login,
        created_at=admin.created_at,
    )


@router.get("", response_model=list[AdminUserRead])
@limiter.limit("30/minute")
async def list_admin_users(
    request: Request,
    pagination: Pagination = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
    _admin: AdminUser = Depends(require_permission("admin_users.manage")),
) -> list[AdminUserRead]:
    admins = (
        (
            await db.execute(
                select(AdminUser)
                .order_by(AdminUser.created_at.desc())
                .limit(pagination.limit)
                .offset(pagination.offset)
            )
        )
        .scalars()
        .all()
    )
    return [await _to_read(db, a) for a in admins]


@router.post("", response_model=AdminUserRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_admin_user(
    request: Request,
    body: AdminUserCreate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(require_permission("admin_users.manage")),
) -> AdminUserRead:
    existing = (
        await db.execute(select(AdminUser).where(AdminUser.email == body.email))
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cet email est déjà utilisé."
        )

    role = await db.get(Role, body.role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rôle introuvable.")

    try:
        validate_password_strength(body.password)
    except WeakPasswordError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    new_admin = AdminUser(
        email=body.email,
        password_hash=hash_password(body.password),
        role_id=body.role_id,
        status="active",
    )
    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)

    logger.bind(channel="security").info(
        f"Compte admin {new_admin.email} créé par {admin.email}"
    )
    return await _to_read(db, new_admin)


@router.patch("/{user_id}", response_model=AdminUserRead)
@limiter.limit("30/minute")
async def update_admin_user(
    request: Request,
    user_id: int,
    body: AdminUserUpdate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(require_permission("admin_users.manage")),
) -> AdminUserRead:
    target = await db.get(AdminUser, user_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compte introuvable.")

    if body.status is not None and body.status != "active" and target.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas désactiver ou archiver votre propre compte.",
        )

    if body.email is not None and body.email != target.email:
        existing = (
            await db.execute(select(AdminUser).where(AdminUser.email == body.email))
        ).scalar_one_or_none()
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Cet email est déjà utilisé."
            )
        target.email = body.email

    if body.role_id is not None:
        role = await db.get(Role, body.role_id)
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Rôle introuvable."
            )
        target.role_id = body.role_id

    if body.status is not None:
        target.status = body.status

    if body.password is not None:
        try:
            validate_password_strength(body.password)
        except WeakPasswordError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        target.password_hash = hash_password(body.password)

    await db.commit()
    await db.refresh(target)

    logger.bind(channel="security").info(
        f"Compte admin {target.email} modifié par {admin.email} : "
        f"status={target.status}, role_id={target.role_id}"
    )
    return await _to_read(db, target)
