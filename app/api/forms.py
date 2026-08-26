import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.deps.campaign_windows import require_open_campaign
from app.models import (
    ContactMessage,
    NewsletterSubscriber,
    PassType,
    PromoCode,
    User,
    UserProfile,
    Waitlist,
)
from app.schemas.contact import ContactCreate
from app.schemas.content import ContactMessageRead
from app.schemas.newsletter import NewsletterCreate, NewsletterSubscriberRead
from app.schemas.payments import WaitlistRead
from app.schemas.register import RegisterCreate
from app.schemas.users import UserRead
from app.schemas.waitlist import WaitlistCreate
from app.services.recaptcha import verify_recaptcha

router = APIRouter(prefix="/api", tags=["forms"])


async def _validate_promo_code(db: AsyncSession, code: str) -> None:
    promo = (
        await db.execute(select(PromoCode).where(PromoCode.code == code))
    ).scalar_one_or_none()

    today = datetime.date.today()
    is_valid = (
        promo is not None
        and promo.is_active
        and (promo.valid_from is None or promo.valid_from <= today)
        and (promo.valid_until is None or promo.valid_until >= today)
        and (promo.usage_limit is None or promo.usage_count < promo.usage_limit)
    )
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce code promo n'est pas valide.",
        )


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


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_open_campaign("ticketing"))],
)
async def register(body: RegisterCreate, db: AsyncSession = Depends(get_db)) -> UserRead:
    pass_type = await db.get(PassType, body.pass_type_id)
    if pass_type is None or not pass_type.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce type de billet n'est pas valide.",
        )

    if body.promo_code is not None:
        await _validate_promo_code(db, body.promo_code)

    user = User(
        first_name=body.first_name,
        last_name=body.last_name,
        gender=body.gender,
        email=body.email,
        phone_whatsapp=body.phone_whatsapp,
        country=body.country,
        city=body.city,
        sector=body.sector,
        experience_level=body.experience_level,
        linkedin_url=body.linkedin_url,
        portfolio_url=body.portfolio_url,
        special_needs=body.special_needs,
        heard_from=body.heard_from,
        gdpr_consent=body.gdpr_consent,
        newsletter_consent=body.newsletter_consent,
    )
    db.add(user)
    try:
        await db.flush()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cet email est déjà inscrit.",
        ) from exc

    for profile in set(body.profiles):
        db.add(UserProfile(user_id=user.id, profile=profile))
    await db.commit()
    await db.refresh(user)

    return UserRead.model_validate(user)


@router.post(
    "/contact", response_model=ContactMessageRead, status_code=status.HTTP_201_CREATED
)
async def contact(body: ContactCreate, db: AsyncSession = Depends(get_db)) -> ContactMessageRead:
    await verify_recaptcha(body.captcha)

    message = ContactMessage(
        name=body.name, email=body.email, subject=body.subject, message=body.message
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)

    return ContactMessageRead.model_validate(message)


@router.post(
    "/newsletter", response_model=NewsletterSubscriberRead, status_code=status.HTTP_201_CREATED
)
async def subscribe_newsletter(
    body: NewsletterCreate, db: AsyncSession = Depends(get_db)
) -> NewsletterSubscriberRead:
    subscriber = NewsletterSubscriber(email=body.email)
    db.add(subscriber)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cet email est déjà inscrit à la newsletter.",
        ) from exc

    await db.refresh(subscriber)
    return NewsletterSubscriberRead.model_validate(subscriber)
