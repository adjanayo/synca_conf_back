from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.rbac import get_current_admin
from app.models import AdminUser, Permission, Role, RolePermission
from app.schemas.auth import AdminLoginRequest, AdminMeOut, TokenPair
from app.services.auth_service import (
    AccountLockedError,
    InvalidCredentialsError,
    authenticate_admin,
    create_access_token,
    create_refresh_token,
)

router = APIRouter(prefix="/api/admin", tags=["auth"])


@router.post("/login", response_model=TokenPair)
@limiter.limit("5/minute")
async def login(
    request: Request,
    credentials: AdminLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenPair:
    client_ip = request.client.host if request.client else None
    try:
        admin = await authenticate_admin(db, credentials.email, credentials.password, client_ip)
    except (InvalidCredentialsError, AccountLockedError) as exc:
        logger.bind(channel="security").warning(
            f"Connexion admin échouée : {credentials.email} depuis {client_ip}"
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    logger.bind(channel="security").info(f"Connexion admin réussie : {admin.email}")
    subject = str(admin.id)
    return TokenPair(
        access_token=create_access_token(subject),
        refresh_token=create_refresh_token(subject),
    )


@router.get("/me", response_model=AdminMeOut)
async def get_me(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> AdminMeOut:
    role = await db.get(Role, admin.role_id)
    permission_codes = (
        (
            await db.execute(
                select(Permission.code)
                .join(RolePermission, RolePermission.permission_id == Permission.id)
                .where(RolePermission.role_id == admin.role_id)
            )
        )
        .scalars()
        .all()
    )
    return AdminMeOut(
        id=admin.id,
        email=admin.email,
        role=role.name if role else "",
        permission_codes=sorted(permission_codes),
    )
