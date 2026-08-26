import httpx
from fastapi import HTTPException, status

from app.core.config import get_settings

GOOGLE_SITEVERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


async def verify_recaptcha(token: str) -> None:
    """Verify a reCAPTCHA v3 token, raising 400 on failure.

    Skipped entirely when RECAPTCHA_SECRET_KEY isn't set -- local dev/CI
    have no real Google credentials, and 4.9's own tests cover both the
    skip path and (via a mocked client) the real verification logic.
    """
    settings = get_settings()
    if not settings.recaptcha_secret_key:
        return

    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(
            GOOGLE_SITEVERIFY_URL,
            data={"secret": settings.recaptcha_secret_key, "response": token},
        )
    data = response.json()

    if not data.get("success") or data.get("score", 0) < settings.recaptcha_min_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vérification reCAPTCHA échouée.",
        )
