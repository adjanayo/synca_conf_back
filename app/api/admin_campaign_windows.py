from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.rbac import require_permission
from app.models import Waitlist
from app.models.campaign import CAMPAIGN_WINDOW_KEY_VALUES, CampaignWindow
from app.schemas.campaign import CampaignWindowRead, CampaignWindowUpdate
from app.services.email_service import send_email
from app.services.email_templates import waitlist_ticketing_open_email

router = APIRouter(prefix="/api/admin/campaign-windows", tags=["admin-campaign-windows"])


def _is_open(window: CampaignWindow, now: datetime) -> bool:
    return (
        window.is_active
        and window.start_at.replace(tzinfo=UTC) <= now <= window.end_at.replace(tzinfo=UTC)
    )


async def _notify_waitlist(db: AsyncSession) -> None:
    entries = (
        await db.execute(select(Waitlist).where(Waitlist.notified.is_(False)))
    ).scalars().all()
    if not entries:
        return
    body = waitlist_ticketing_open_email()
    for entry in entries:
        await send_email(
            to=entry.email,
            subject="La billetterie SYNCA CONF 2027 est ouverte !",
            body=body,
        )
        entry.notified = True
        entry.last_notified_at = datetime.now(UTC)
    await db.commit()


@router.get("", response_model=list[CampaignWindowRead])
@limiter.limit("30/minute")
async def list_campaign_windows_admin(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("campaign_windows.manage")),
) -> list[CampaignWindowRead]:
    windows = (
        await db.execute(select(CampaignWindow).order_by(CampaignWindow.start_at))
    ).scalars().all()
    return [CampaignWindowRead.model_validate(window) for window in windows]


@router.patch("/{key}", response_model=CampaignWindowRead)
@limiter.limit("30/minute")
async def update_campaign_window(
    request: Request,
    key: str,
    body: CampaignWindowUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("campaign_windows.manage")),
) -> CampaignWindowRead:
    if key not in CAMPAIGN_WINDOW_KEY_VALUES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Fenêtre de campagne inconnue."
        )

    window = (
        await db.execute(select(CampaignWindow).where(CampaignWindow.key == key))
    ).scalar_one_or_none()
    if window is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Fenêtre de campagne inconnue."
        )

    new_start_at = body.start_at if body.start_at is not None else window.start_at
    new_end_at = body.end_at if body.end_at is not None else window.end_at
    # Validated here rather than left to MySQL's CHECK constraint, which
    # surfaces as an opaque OperationalError (not IntegrityError) -- a clean
    # 400 is worth the extra check.
    if new_end_at <= new_start_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_at doit être postérieur à start_at.",
        )

    now = datetime.now(UTC)
    was_open = _is_open(window, now)

    window.start_at = new_start_at
    window.end_at = new_end_at
    if body.is_active is not None:
        window.is_active = body.is_active

    await db.commit()
    await db.refresh(window)

    # Ouverture billetterie -> notifier la liste d'attente (J3), en plus des
    # rappels récurrents pris en charge par la boucle asyncio de
    # app/services/waitlist_reminder.py une fois la fenêtre ouverte.
    if key == "ticketing" and not was_open and _is_open(window, now):
        background_tasks.add_task(_notify_waitlist, db)

    return CampaignWindowRead.model_validate(window)
