from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.schemas.auth import AdminLoginRequest, TokenPair
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
    try:
        admin = await authenticate_admin(db, credentials.email, credentials.password)
    except (InvalidCredentialsError, AccountLockedError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    subject = str(admin.id)
    return TokenPair(
        access_token=create_access_token(subject),
        refresh_token=create_refresh_token(subject),
    )
