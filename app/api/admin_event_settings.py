from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.deps.rbac import require_permission
from app.models.referentials import EventSettings
from app.schemas.referentials import EventSettingsRead, EventSettingsUpdate

router = APIRouter(prefix="/api/admin/event-settings", tags=["admin-event-settings"])

# La ligne singleton est toujours seedée par la migration (id=1) : le 404 ici
# n'est qu'un filet de sécurité si jamais elle a été supprimée manuellement.
_SINGLETON_ID = 1


@router.get("", response_model=EventSettingsRead)
@limiter.limit("30/minute")
async def get_event_settings(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("event_settings.manage")),
) -> EventSettingsRead:
    settings = await db.get(EventSettings, _SINGLETON_ID)
    if settings is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paramètres de l'événement introuvables.",
        )
    return EventSettingsRead.model_validate(settings)


@router.patch("", response_model=EventSettingsRead)
@limiter.limit("30/minute")
async def update_event_settings(
    request: Request,
    body: EventSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_permission("event_settings.manage")),
) -> EventSettingsRead:
    settings = await db.get(EventSettings, _SINGLETON_ID)
    if settings is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paramètres de l'événement introuvables.",
        )

    if body.name is not None:
        settings.name = body.name
    if body.venue is not None:
        settings.venue = body.venue
    # `year` est nullable par design (contrairement à name/venue) -- on
    # distingue "champ absent" de "champ explicitement remis à null" pour
    # permettre à l'admin d'effacer l'année, pas seulement de la fixer.
    if "year" in body.model_fields_set:
        settings.year = body.year

    await db.commit()
    await db.refresh(settings)
    return EventSettingsRead.model_validate(settings)
