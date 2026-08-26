from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.deps.pagination import Pagination, pagination_params
from app.models import Day, Session
from app.schemas import DayRead, SessionRead

router = APIRouter(prefix="/api", tags=["public"])


@router.get("/days", response_model=list[DayRead])
async def list_days(db: AsyncSession = Depends(get_db)) -> list[DayRead]:
    days = (await db.execute(select(Day).order_by(Day.date))).scalars().all()
    return [DayRead.model_validate(day) for day in days]


@router.get("/sessions", response_model=list[SessionRead])
async def list_sessions(
    day: int | None = None,
    category: str | None = None,
    pagination: Pagination = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> list[SessionRead]:
    query = select(Session).where(Session.is_public.is_(True))
    if day is not None:
        query = query.where(Session.day_id == day)
    if category is not None:
        query = query.where(Session.category == category)
    query = query.order_by(Session.day_id, Session.start_time).limit(pagination.limit).offset(
        pagination.offset
    )

    sessions = (await db.execute(query)).scalars().all()
    return [SessionRead.model_validate(session) for session in sessions]
