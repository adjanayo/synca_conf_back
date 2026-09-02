from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import AdminUser, Permission, RolePermission
from app.services.auth_service import InvalidTokenError, decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/login", auto_error=False)


async def get_current_admin(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> AdminUser:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides ou expirés.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        logger.bind(channel="security").warning("Accès admin refusé : aucun jeton fourni")
        raise credentials_error

    try:
        payload = decode_token(token, expected_type="access")
    except InvalidTokenError as exc:
        logger.bind(channel="security").warning("Accès admin refusé : jeton invalide ou expiré")
        raise credentials_error from exc

    admin = await db.get(AdminUser, int(payload["sub"]))
    if admin is None:
        logger.bind(channel="security").warning(
            f"Accès admin refusé : sujet de jeton inconnu ({payload['sub']})"
        )
        raise credentials_error
    if admin.status != "active":
        logger.bind(channel="security").warning(
            f"Accès admin refusé : compte {admin.email} {admin.status}"
        )
        raise credentials_error
    return admin


def require_permission(code: str):
    async def _check(
        admin: AdminUser = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db),
    ) -> AdminUser:
        has_permission = (
            await db.execute(
                select(RolePermission)
                .join(Permission, Permission.id == RolePermission.permission_id)
                .where(RolePermission.role_id == admin.role_id, Permission.code == code)
            )
        ).scalar_one_or_none()

        if has_permission is None:
            logger.bind(channel="security").warning(
                f"Accès admin refusé : {admin.email} sans permission {code}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission manquante : {code}.",
            )
        return admin

    return _check
