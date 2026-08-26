from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.rbac import require_permission
from app.models.campaign import CAMPAIGN_WINDOW_KEY_VALUES, CampaignWindow
from app.schemas.campaign import CampaignWindowRead, CampaignWindowUpdate

router = APIRouter(prefix="/api/admin/campaign-windows", tags=["admin-campaign-windows"])


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

    window.start_at = new_start_at
    window.end_at = new_end_at
    if body.is_active is not None:
        window.is_active = body.is_active

    await db.commit()
    await db.refresh(window)
    return CampaignWindowRead.model_validate(window)
