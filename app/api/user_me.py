from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.models import Ticket, User
from app.schemas.tickets import TicketRead
from app.schemas.users import UserRead
from app.services.auth_service import InvalidTokenError, decode_token

router = APIRouter(prefix="/api/user", tags=["user-me"])

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_participant(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Accepts either credential: the legacy one-time `access_token` handed
    out at registration (still valid, never re-issued), or the JWT from the
    OTP login flow (app/api/participant_auth.py). JWT is tried first since
    it's cheap to reject on a decode failure before falling back to a DB hit.
    """
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Jeton d'accès invalide.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        logger.bind(channel="security").warning("Accès /api/user/me refusé : aucun jeton fourni")
        raise invalid

    token = credentials.credentials

    try:
        payload = decode_token(token, expected_type="participant_access")
    except InvalidTokenError:
        payload = None

    if payload is not None:
        user = await db.get(User, int(payload["sub"]))
        if user is None:
            logger.bind(channel="security").warning(
                "Accès /api/user/me refusé : sujet de jeton OTP inconnu"
            )
            raise invalid
        return user

    user = (
        await db.execute(select(User).where(User.access_token == token))
    ).scalar_one_or_none()
    if user is None:
        logger.bind(channel="security").warning("Accès /api/user/me refusé : jeton inconnu")
        raise invalid
    return user


@router.get("/me", response_model=UserRead)
@limiter.limit("60/minute")
async def get_me(
    request: Request, user: User = Depends(get_current_participant)
) -> UserRead:
    return UserRead.model_validate(user)


@router.get("/me/tickets", response_model=list[TicketRead])
@limiter.limit("60/minute")
async def get_my_tickets(
    request: Request,
    user: User = Depends(get_current_participant),
    db: AsyncSession = Depends(get_db),
) -> list[TicketRead]:
    """TODO.md: ticket download from the web page.

    Scoped to `Ticket.user_id == user.id` -- no `{ticket_id}` path param
    anywhere, so there's nothing here for another user's bearer token to
    substitute in and no IDOR surface. `pdf_url` itself points at a
    UUID-keyed B2 object (app/services/storage.py::_generate_key), so the
    email delivery path (4.12/5.7) isn't guessable either.
    """
    tickets = (
        await db.execute(select(Ticket).where(Ticket.user_id == user.id))
    ).scalars().all()
    return [TicketRead.model_validate(t) for t in tickets]


@router.delete("/me", status_code=status.HTTP_200_OK)
@limiter.limit("60/minute")
async def delete_me(
    request: Request,
    user: User = Depends(get_current_participant),
    db: AsyncSession = Depends(get_db),
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
