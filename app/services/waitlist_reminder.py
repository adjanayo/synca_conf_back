"""Rappels récurrents waitlist (voir DEVLOG.md front, phase J3 suite).

Pas de cron dans le projet : cette fonction est appelée périodiquement par la
boucle asyncio démarrée dans app/main.py, pas par une tâche planifiée
externe. Elle relance un email aux inscrits non enregistrés dont le dernier
email date de plus de `waitlist_reminder_interval_days`, tant que la fenêtre
`ticketing` reste ouverte -- silencieuse (no-op) sinon.
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import Waitlist
from app.models.campaign import CampaignWindow
from app.services.email_service import send_email
from app.services.email_templates import waitlist_reminder_email

settings = get_settings()


async def _ticketing_window_open(db: AsyncSession, now: datetime) -> bool:
    window = (
        await db.execute(select(CampaignWindow).where(CampaignWindow.key == "ticketing"))
    ).scalar_one_or_none()
    if window is None:
        return False
    return (
        window.is_active
        and window.start_at.replace(tzinfo=UTC) <= now <= window.end_at.replace(tzinfo=UTC)
    )


async def send_waitlist_reminders(db: AsyncSession) -> int:
    now = datetime.now(UTC)
    if not await _ticketing_window_open(db, now):
        return 0

    threshold = now - timedelta(days=settings.waitlist_reminder_interval_days)
    entries = (
        await db.execute(
            select(Waitlist).where(
                Waitlist.registered.is_(False),
                Waitlist.notified.is_(True),
            )
        )
    ).scalars().all()

    due = [
        entry
        for entry in entries
        if entry.last_notified_at is None
        or entry.last_notified_at.replace(tzinfo=UTC) <= threshold
    ]
    if not due:
        return 0

    body = waitlist_reminder_email()
    for entry in due:
        await send_email(
            to=entry.email,
            subject="La billetterie SYNCA CONF 2027 est toujours ouverte",
            body=body,
        )
        entry.last_notified_at = now
    await db.commit()
    return len(due)
