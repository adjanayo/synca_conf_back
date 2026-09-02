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
from app.api.admin_export import router as admin_export_router
from app.api.admin_registrations import router as admin_registrations_router
from app.api.admin_stats import router as admin_stats_router
from app.api.auth import router as auth_router
from app.api.forms import router as forms_router
from app.api.participant_auth import router as participant_auth_router
from app.api.payments import router as payments_router
from app.api.public import router as public_router
from app.api.rbac import router as rbac_router
from app.api.user_me import router as user_me_router
from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.core.rate_limit import limiter
from app.core.security_headers import SecurityHeadersMiddleware

settings = get_settings()
configure_logging()

docs_enabled = settings.environment != "production"

app = FastAPI(
    title=settings.app_name,
    docs_url="/docs" if docs_enabled else None,
    redoc_url="/redoc" if docs_enabled else None,
    openapi_url="/openapi.json" if docs_enabled else None,
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
app.include_router(user_me_router)

init_admin(app)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
