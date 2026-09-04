import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.admin.setup import init_admin
from app.api.admin_applications import router as admin_applications_router
from app.api.admin_audit import router as admin_audit_router
from app.api.admin_campaign_windows import router as admin_campaign_windows_router
from app.api.admin_contacts import router as admin_contacts_router
from app.api.admin_event_settings import router as admin_event_settings_router
from app.api.admin_export import router as admin_export_router
from app.api.admin_faqs import admin_faq_categories_router, admin_faqs_router
from app.api.admin_hackathon import admin_hackathon_teams_router
from app.api.admin_participants import router as admin_participants_router
from app.api.admin_partner_levels import benefits_router as admin_partner_benefits_router
from app.api.admin_partner_levels import router as admin_partner_levels_router
from app.api.admin_pass_types import contents_router as admin_pass_contents_router
from app.api.admin_pass_types import router as admin_pass_types_router
from app.api.admin_program import admin_days_router, admin_sessions_router
from app.api.admin_promo_codes import router as admin_promo_codes_router
from app.api.admin_registrations import router as admin_registrations_router
from app.api.admin_stats import router as admin_stats_router
from app.api.admin_users import router as admin_users_router
from app.api.admin_waitlist import router as admin_waitlist_router
from app.api.auth import router as auth_router
from app.api.forms import router as forms_router
from app.api.participant_auth import router as participant_auth_router
from app.api.payments import router as payments_router
from app.api.public import router as public_router
from app.api.rbac import router as rbac_router
from app.api.user_me import router as user_me_router
from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.core.logging_config import configure_logging
from app.core.rate_limit import limiter
from app.core.security_headers import SecurityHeadersMiddleware
from app.services.waitlist_reminder import send_waitlist_reminders

settings = get_settings()
configure_logging()

docs_enabled = settings.environment != "production"


async def _waitlist_reminder_loop() -> None:
    """Pas de cron dans le projet : boucle asyncio en tâche de fond,
    voir app/services/waitlist_reminder.py."""
    interval_seconds = settings.waitlist_reminder_check_interval_minutes * 60
    while True:
        await asyncio.sleep(interval_seconds)
        try:
            async with AsyncSessionLocal() as db:
                sent = await send_waitlist_reminders(db)
            if sent:
                logger.info(f"Rappels waitlist envoyés : {sent}")
        except Exception:
            logger.exception("Échec de la boucle de rappels waitlist")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    task = asyncio.create_task(_waitlist_reminder_loop())
    yield
    task.cancel()


app = FastAPI(
    title=settings.app_name,
    docs_url="/docs" if docs_enabled else None,
    redoc_url="/redoc" if docs_enabled else None,
    openapi_url="/openapi.json" if docs_enabled else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
app.add_middleware(SecurityHeadersMiddleware, hsts_enabled=settings.environment == "production")

app.state.limiter = limiter


def _log_rate_limit_exceeded(request: Request, exc: RateLimitExceeded):
    client_ip = request.client.host if request.client else "?"
    logger.bind(channel="security").warning(
        f"Rate limit dépassé : {client_ip} sur {request.url.path}"
    )
    return _rate_limit_exceeded_handler(request, exc)


app.add_exception_handler(RateLimitExceeded, _log_rate_limit_exceeded)
app.add_middleware(SlowAPIMiddleware)

app.include_router(auth_router)
app.include_router(participant_auth_router)
app.include_router(rbac_router)
app.include_router(public_router)
app.include_router(forms_router)
app.include_router(payments_router)
app.include_router(admin_applications_router)
app.include_router(admin_campaign_windows_router)
app.include_router(admin_stats_router)
app.include_router(admin_registrations_router)
app.include_router(admin_contacts_router)
app.include_router(admin_export_router)
app.include_router(admin_audit_router)
app.include_router(admin_pass_types_router)
app.include_router(admin_pass_contents_router)
app.include_router(admin_partner_levels_router)
app.include_router(admin_partner_benefits_router)
app.include_router(admin_event_settings_router)
app.include_router(admin_days_router)
app.include_router(admin_sessions_router)
app.include_router(admin_faq_categories_router)
app.include_router(admin_faqs_router)
app.include_router(admin_hackathon_teams_router)
app.include_router(admin_participants_router)
app.include_router(admin_waitlist_router)
app.include_router(admin_promo_codes_router)
app.include_router(admin_users_router)
app.include_router(user_me_router)

init_admin(app)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
