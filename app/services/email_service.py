import httpx
from loguru import logger

from app.core.config import get_settings

RESEND_API_URL = "https://api.resend.com/emails"


async def send_email(to: str, subject: str, body: str) -> None:
    """Send a transactional email, or log it in dev.

    Without RESEND_API_KEY configured (local dev, CI), the email is only
    logged via loguru -- no real send, no SMTP test container needed
    (planning_fastapi.md §1).
    """
    settings = get_settings()
    if not settings.resend_api_key:
        logger.info(f"[email:dev] to={to} subject={subject!r}\n{body}")
        return

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            RESEND_API_URL,
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            json={
                "from": settings.resend_from_email,
                "to": [to],
                "subject": subject,
                "html": body,
            },
        )
        response.raise_for_status()
