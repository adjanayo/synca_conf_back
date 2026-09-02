from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.schemas.auth import OtpRequestIn, OtpVerifyIn, ParticipantTokenOut
from app.services.auth_service import create_participant_token
from app.services.otp_service import InvalidOtpError, request_otp, verify_otp

router = APIRouter(prefix="/api/auth/otp", tags=["participant-auth"])


@router.post("/request", status_code=status.HTTP_200_OK)
@limiter.limit("3/15minute")
async def request_login_code(
    request: Request,
    payload: OtpRequestIn,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    await request_otp(db, payload.email)
    # Generic response regardless of account existence (anti-enumeration,
    # same posture as security-hardening's "customer access codes" rule).
    return {
        "detail": "Si un compte existe pour cet email, un code de connexion vient d'être envoyé."
    }


@router.post("/verify", response_model=ParticipantTokenOut)
@limiter.limit("10/15minute")
async def verify_login_code(
    request: Request,
    payload: OtpVerifyIn,
    db: AsyncSession = Depends(get_db),
) -> ParticipantTokenOut:
    try:
        user = await verify_otp(db, payload.email, payload.code)
    except InvalidOtpError as exc:
        logger.bind(channel="security").warning(f"Connexion OTP échouée : {payload.email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    logger.bind(channel="security").info(f"Connexion OTP réussie : {user.email}")
    return ParticipantTokenOut(access_token=create_participant_token(str(user.id)))
