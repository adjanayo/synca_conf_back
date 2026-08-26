from datetime import UTC, datetime

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import CampaignWindow


def require_open_campaign(key: str):
    async def _check(db: AsyncSession = Depends(get_db)) -> None:
        window = (
            await db.execute(select(CampaignWindow).where(CampaignWindow.key == key))
        ).scalar_one_or_none()

        now = datetime.now(UTC)
        is_open = (
            window is not None
            and window.is_active
            and window.start_at.replace(tzinfo=UTC) <= now <= window.end_at.replace(tzinfo=UTC)
        )
        if not is_open:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cette candidature n'est pas ouverte actuellement.",
            )

    return _check
