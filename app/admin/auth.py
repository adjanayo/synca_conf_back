from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from starlette.requests import Request

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.models import AdminUser, Permission, RolePermission
from app.services.auth_service import (
    AccountLockedError,
    InvalidCredentialsError,
    InvalidTokenError,
    authenticate_admin,
    create_access_token,
    decode_token,
)


class AdminAuth(AuthenticationBackend):
    """SQLAdmin login backed by the same admin_users/Argon2id/lockout path
    as POST /api/admin/login (2.3) -- no separate credential store for the
    backoffice. The session cookie only carries the JWT access token;
    authenticate() re-derives the caller's permission codes from the DB on
    every request so a role change takes effect immediately, and stashes
    them in the session for each ModelView's is_accessible() to read.
    """

    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = str(form.get("username", ""))
        password = str(form.get("password", ""))
        ip_address = request.client.host if request.client else None

        async with AsyncSessionLocal() as db:
            try:
                admin = await authenticate_admin(db, email, password, ip_address)
            except (InvalidCredentialsError, AccountLockedError):
                return False

        request.session["token"] = create_access_token(str(admin.id))
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False

        try:
            payload = decode_token(token, expected_type="access")
        except InvalidTokenError:
            return False

        async with AsyncSessionLocal() as db:
            admin = await db.get(AdminUser, int(payload["sub"]))
            if admin is None:
                return False

            codes = (
                await db.execute(
                    select(Permission.code)
                    .join(RolePermission, RolePermission.permission_id == Permission.id)
                    .where(RolePermission.role_id == admin.role_id)
                )
            ).scalars().all()

        request.session["permissions"] = list(codes)
        return True


def build_admin_auth() -> AdminAuth:
    # Reuses JWT_SECRET_KEY rather than a second secret: SQLAdmin's session
    # cookie only ever holds a token already governed by that key, so a
    # separate secret would add rotation surface without adding security.
    return AdminAuth(secret_key=get_settings().jwt_secret_key)
