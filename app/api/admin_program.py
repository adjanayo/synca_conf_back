from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.rbac import require_permission
from app.models.applications import Speaker
from app.models.referentials import Day
from app.models.sessions import SESSION_CATEGORY_VALUES, Session
from app.schemas.referentials import DayCreate, DayRead, DayUpdate
from app.schemas.sessions import SessionCreate, SessionRead, SessionUpdate

admin_days_router = APIRouter(prefix="/api/admin/days", tags=["admin-days"])
admin_sessions_router = APIRouter(prefix="/api/admin/sessions", tags=["admin-sessions"])


# --- Days -------------------------------------------------------------


@admin_days_router.get("", response_model=list[DayRead])
@limiter.limit("30/minute")
async def list_days_admin(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("sessions.manage")),
) -> list[DayRead]:
    days = (await db.execute(select(Day).order_by(Day.date))).scalars().all()
    return [DayRead.model_validate(day) for day in days]


@admin_days_router.post("", response_model=DayRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_day(
    request: Request,
    body: DayCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("sessions.manage")),
) -> DayRead:
    existing = (
        await db.execute(select(Day).where(Day.date == body.date))
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un jour existe déjà pour cette date.",
        )

    day = Day(date=body.date, label=body.label)
    db.add(day)
    await db.commit()
    await db.refresh(day)
    return DayRead.model_validate(day)


@admin_days_router.patch("/{day_id}", response_model=DayRead)
@limiter.limit("30/minute")
async def update_day(
    request: Request,
    day_id: int,
    body: DayUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("sessions.manage")),
) -> DayRead:
    day = await db.get(Day, day_id)
    if day is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jour introuvable.")

    if body.date is not None and body.date != day.date:
        existing = (
            await db.execute(select(Day).where(Day.date == body.date))
        ).scalar_one_or_none()
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un jour existe déjà pour cette date.",
            )
        day.date = body.date

    if body.label is not None:
        day.label = body.label

    await db.commit()
    await db.refresh(day)
    return DayRead.model_validate(day)


@admin_days_router.delete("/{day_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
async def delete_day(
    request: Request,
    day_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("sessions.manage")),
) -> None:
    day = await db.get(Day, day_id)
    if day is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jour introuvable.")

    has_sessions = (
        await db.execute(select(Session.id).where(Session.day_id == day_id).limit(1))
    ).scalar_one_or_none()
    if has_sessions is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de supprimer un jour ayant des sessions rattachées.",
        )

    await db.delete(day)
    await db.commit()


# --- Sessions -----------------------------------------------------------


@admin_sessions_router.get("", response_model=list[SessionRead])
@limiter.limit("30/minute")
async def list_sessions_admin(
    request: Request,
    day_id: int | None = None,
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("sessions.manage")),
) -> list[SessionRead]:
    query = select(Session)
    if day_id is not None:
        query = query.where(Session.day_id == day_id)
    if category is not None:
        query = query.where(Session.category == category)
    query = query.order_by(Session.start_time)

    sessions = (await db.execute(query)).scalars().all()
    return [SessionRead.model_validate(session) for session in sessions]


@admin_sessions_router.post("", response_model=SessionRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_session(
    request: Request,
    body: SessionCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("sessions.manage")),
) -> SessionRead:
    if body.category not in SESSION_CATEGORY_VALUES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Catégorie de session invalide.",
        )
    if body.end_time <= body.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_time doit être postérieur à start_time.",
        )

    day = await db.get(Day, body.day_id)
    if day is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jour introuvable.")

    if body.speaker_id is not None:
        speaker = await db.get(Speaker, body.speaker_id)
        if speaker is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Intervenant introuvable."
            )

    session = Session(
        day_id=body.day_id,
        title=body.title,
        description=body.description,
        category=body.category,
        start_time=body.start_time,
        end_time=body.end_time,
        room=body.room,
        speaker_id=body.speaker_id,
        is_public=body.is_public,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return SessionRead.model_validate(session)


@admin_sessions_router.patch("/{session_id}", response_model=SessionRead)
@limiter.limit("30/minute")
async def update_session(
    request: Request,
    session_id: int,
    body: SessionUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("sessions.manage")),
) -> SessionRead:
    session = await db.get(Session, session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session introuvable.")

    if body.category is not None and body.category not in SESSION_CATEGORY_VALUES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Catégorie de session invalide.",
        )

    new_start_time = body.start_time if body.start_time is not None else session.start_time
    new_end_time = body.end_time if body.end_time is not None else session.end_time
    if new_end_time <= new_start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_time doit être postérieur à start_time.",
        )

    if body.day_id is not None and body.day_id != session.day_id:
        day = await db.get(Day, body.day_id)
        if day is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jour introuvable.")
        session.day_id = body.day_id

    if body.speaker_id is not None and body.speaker_id != session.speaker_id:
        speaker = await db.get(Speaker, body.speaker_id)
        if speaker is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Intervenant introuvable."
            )
        session.speaker_id = body.speaker_id

    if body.title is not None:
        session.title = body.title
    if body.description is not None:
        session.description = body.description
    if body.category is not None:
        session.category = body.category
    session.start_time = new_start_time
    session.end_time = new_end_time
    if body.room is not None:
        session.room = body.room
    if body.is_public is not None:
        session.is_public = body.is_public

    await db.commit()
    await db.refresh(session)
    return SessionRead.model_validate(session)


@admin_sessions_router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
async def delete_session(
    request: Request,
    session_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("sessions.manage")),
) -> None:
    session = await db.get(Session, session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session introuvable.")

    await db.delete(session)
    await db.commit()
