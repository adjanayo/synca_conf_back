from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Waitlist
from app.schemas.payments import WaitlistRead
from app.schemas.waitlist import WaitlistCreate

router = APIRouter(prefix="/api", tags=["forms"])


@router.post("/waitlist", response_model=WaitlistRead, status_code=status.HTTP_201_CREATED)
async def join_waitlist(
    body: WaitlistCreate, db: AsyncSession = Depends(get_db)
) -> WaitlistRead:
    entry = Waitlist(email=body.email)
    db.add(entry)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cet email est déjà inscrit à la liste d'attente.",
        ) from exc

    await db.refresh(entry)
    return WaitlistRead.model_validate(entry)
