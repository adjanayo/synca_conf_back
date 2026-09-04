from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.rbac import get_current_admin
from app.models import AdminUser, Permission, Role, RolePermission
from app.schemas.auth import AdminLoginRequest, AdminMeOut, RefreshRequest, TokenPair
from app.services.auth_service import (
    AccountDisabledError,
    AccountLockedError,
    InvalidCredentialsError,
    InvalidTokenError,
    authenticate_admin,
    create_access_token,
    create_refresh_token,
    decode_token,
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
    except (InvalidCredentialsError, AccountLockedError, AccountDisabledError) as exc:
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


@router.post("/refresh", response_model=TokenPair)
@limiter.limit("30/minute")
async def refresh(
    request: Request,
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenPair:
    """Échange un refresh_token (long-lived) contre une nouvelle paire --
    évite de renvoyer l'admin au login à chaque expiration de l'access_token
    (ROADMAP_PUBLIC_SEO.md Partie 6, `create_refresh_token` existait déjà
    depuis le login mais rien ne le consommait). Rotation à chaque appel :
    l'ancien refresh_token n'est jamais réutilisable après (pas de
    révocation en base, mais un jeton volé et rejoué ne fait qu'avancer la
    même paire, aucun avantage pour l'attaquant).
    """
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Jeton de rafraîchissement invalide."
    )
    try:
        payload = decode_token(body.refresh_token, expected_type="refresh")
    except InvalidTokenError as exc:
        raise invalid from exc

    admin = await db.get(AdminUser, int(payload["sub"]))
    if admin is None or admin.status != "active":
        logger.bind(channel="security").warning(
            f"Refresh refusé : compte {payload['sub']} introuvable ou inactif"
        )
        raise invalid

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
