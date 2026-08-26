from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import User
from app.schemas.users import UserRead

router = APIRouter(prefix="/api/user", tags=["user-me"])

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_participant(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Jeton d'accès invalide.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise invalid

    user = (
        await db.execute(select(User).where(User.access_token == credentials.credentials))
    ).scalar_one_or_none()
    if user is None:
        raise invalid
    return user


@router.get("/me", response_model=UserRead)
async def get_me(user: User = Depends(get_current_participant)) -> UserRead:
    return UserRead.model_validate(user)


@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_me(
    user: User = Depends(get_current_participant), db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    """Right to erasure (RGPD) via anonymization, not a physical delete --
    tickets/payments keep their user_id for financial/audit records, but the
    personal fields on the user row itself are scrubbed. access_token is
    revoked so this can't be called twice.
    """
    user.first_name = "Anonymisé"
    user.last_name = "Anonymisé"
    user.email = f"anonymized-{user.id}@deleted.synca.conf"
    user.gender = None
    user.phone_whatsapp = "0000000000"
    user.linkedin_url = None
    user.portfolio_url = None
    user.special_needs = None
    user.heard_from = None
    user.newsletter_consent = False
    user.access_token = None

    await db.commit()
    return {"detail": "Compte anonymisé avec succès."}
