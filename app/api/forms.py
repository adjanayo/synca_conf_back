import datetime

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.multipart import parse_multipart_form
from app.deps.campaign_windows import require_open_campaign
from app.models import (
    Ambassador,
    ContactMessage,
    Exhibitor,
    NewsletterSubscriber,
    Partner,
    PartnerLevel,
    PassType,
    PromoCode,
    Speaker,
    User,
    UserProfile,
    Waitlist,
)
from app.schemas.ambassador_apply import AmbassadorApplyCreate
from app.schemas.applications import AmbassadorRead, ExhibitorRead, PartnerRead, SpeakerRead
from app.schemas.contact import ContactCreate
from app.schemas.content import ContactMessageRead
from app.schemas.exhibitor_apply import ExhibitorApplyCreate
from app.schemas.newsletter import NewsletterCreate, NewsletterSubscriberRead
from app.schemas.partner_apply import PartnerApplyCreate
from app.schemas.payments import WaitlistRead
from app.schemas.register import RegisterCreate
from app.schemas.speaker_apply import SpeakerApplyCreate
from app.schemas.users import UserRead
from app.schemas.waitlist import WaitlistCreate
from app.services.email_service import send_email
from app.services.recaptcha import verify_recaptcha
from app.services.storage import UploadRejectedError, upload_file

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
async def register(
    body: RegisterCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)
) -> UserRead:
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

    background_tasks.add_task(
        send_email,
        to=user.email,
        subject="Confirmation d'inscription — SYNCA CONF 2027",
        body=f"Bonjour {user.first_name}, votre inscription à SYNCA CONF 2027 est confirmée.",
    )
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


@router.post(
    "/speakers/apply",
    response_model=SpeakerRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_open_campaign("call_for_speaker"))],
)
async def apply_as_speaker(
    request: Request,
    background_tasks: BackgroundTasks,
    photo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> SpeakerRead:
    body = await parse_multipart_form(request, SpeakerApplyCreate)
    content = await photo.read()
    try:
        photo_url = await upload_file(content, photo.filename or "photo", photo.content_type or "")
    except UploadRejectedError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    speaker = Speaker(
        first_name=body.first_name,
        last_name=body.last_name,
        title_role=body.title_role,
        company=body.company,
        country=body.country,
        email=body.email,
        phone_whatsapp=body.phone_whatsapp,
        linkedin_url=body.linkedin_url,
        website_url=body.website_url,
        photo_url=photo_url,
        intervention_format=body.intervention_format,
        intervention_title=body.intervention_title,
        theme=body.theme,
        summary=body.summary,
        audience_level=body.audience_level,
        language=body.language,
        past_experience=body.past_experience,
        video_link=body.video_link,
        availability=body.availability,
        departure_city=body.departure_city,
        needs_accommodation=body.needs_accommodation,
        motivation=body.motivation,
        video_consent=body.video_consent,
        gdpr_consent=body.gdpr_consent,
    )
    db.add(speaker)
    await db.commit()
    await db.refresh(speaker)

    background_tasks.add_task(
        send_email,
        to=speaker.email,
        subject="Candidature speaker reçue — SYNCA CONF 2027",
        body=f"Bonjour {speaker.first_name}, nous avons bien reçu votre candidature.",
    )
    return SpeakerRead.model_validate(speaker)


@router.post(
    "/ambassadors/apply",
    response_model=AmbassadorRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_open_campaign("call_for_ambassador"))],
)
async def apply_as_ambassador(
    body: AmbassadorApplyCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> AmbassadorRead:
    ambassador = Ambassador(
        first_name=body.first_name,
        last_name=body.last_name,
        age=body.age,
        country=body.country,
        city=body.city,
        email=body.email,
        phone_whatsapp=body.phone_whatsapp,
        current_profile=body.current_profile,
        institution_company=body.institution_company,
        linkedin_url=body.linkedin_url,
        social_handles=body.social_handles,
        followers_range=body.followers_range,
        motivation=body.motivation,
        mobilization_plan=body.mobilization_plan,
        estimated_reach=body.estimated_reach,
        previous_synca=body.previous_synca,
        preferred_channels=", ".join(body.preferred_channels),
        availability_pre=body.availability_pre,
        gdpr_consent=body.gdpr_consent,
    )
    db.add(ambassador)
    await db.commit()
    await db.refresh(ambassador)

    background_tasks.add_task(
        send_email,
        to=ambassador.email,
        subject="Candidature ambassadeur reçue — SYNCA CONF 2027",
        body=f"Bonjour {ambassador.first_name}, nous avons bien reçu votre candidature.",
    )
    return AmbassadorRead.model_validate(ambassador)


@router.post(
    "/partners/apply",
    response_model=PartnerRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_open_campaign("call_for_partner"))],
)
async def apply_as_partner(
    request: Request,
    background_tasks: BackgroundTasks,
    logo: UploadFile | None = File(default=None),
    db: AsyncSession = Depends(get_db),
) -> PartnerRead:
    body = await parse_multipart_form(request, PartnerApplyCreate)

    level = await db.get(PartnerLevel, body.level_id)
    if level is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce palier de partenariat n'est pas valide.",
        )

    logo_url = None
    if logo is not None and logo.filename:
        content = await logo.read()
        try:
            logo_url = await upload_file(content, logo.filename, logo.content_type or "")
        except UploadRejectedError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    partner = Partner(
        organization_name=body.organization_name,
        sector=body.sector,
        country=body.country,
        city=body.city,
        website_url=body.website_url,
        contact_name=body.contact_name,
        contact_position=body.contact_position,
        contact_email=body.contact_email,
        contact_phone=body.contact_phone,
        level_id=body.level_id,
        has_budget=body.has_budget,
        objectives=", ".join(body.objectives),
        previous_sponsor=body.previous_sponsor,
        message=body.message,
        heard_from=body.heard_from,
        gdpr_consent=body.gdpr_consent,
        logo_url=logo_url,
    )
    db.add(partner)
    await db.commit()
    await db.refresh(partner)

    background_tasks.add_task(
        send_email,
        to=partner.contact_email,
        subject="Candidature partenaire reçue — SYNCA CONF 2027",
        body=f"Bonjour {partner.contact_name}, nous avons bien reçu votre candidature.",
    )
    return PartnerRead.model_validate(partner)


@router.post(
    "/exhibitors/apply",
    response_model=ExhibitorRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_open_campaign("call_for_exhibitor"))],
)
async def apply_as_exhibitor(
    body: ExhibitorApplyCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> ExhibitorRead:
    exhibitor = Exhibitor(
        organization_name=body.organization_name,
        sector=body.sector,
        country=body.country,
        city=body.city,
        website_url=body.website_url,
        contact_name=body.contact_name,
        contact_position=body.contact_position,
        contact_email=body.contact_email,
        contact_phone=body.contact_phone,
        stand_type=body.stand_type,
        reps_count=body.reps_count,
        linked_partner_level=body.linked_partner_level,
        products_services=body.products_services,
        equipment_needs=", ".join(body.equipment_needs) if body.equipment_needs else None,
        side_activities=", ".join(body.side_activities) if body.side_activities else None,
        visuals_url=body.visuals_url,
        payment_method=body.payment_method,
        rules_accepted=body.rules_accepted,
        gdpr_consent=body.gdpr_consent,
    )
    db.add(exhibitor)
    await db.commit()
    await db.refresh(exhibitor)

    background_tasks.add_task(
        send_email,
        to=exhibitor.contact_email,
        subject="Candidature exposant reçue — SYNCA CONF 2027",
        body=f"Bonjour {exhibitor.contact_name}, nous avons bien reçu votre candidature.",
    )
    return ExhibitorRead.model_validate(exhibitor)
