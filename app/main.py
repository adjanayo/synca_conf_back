from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.admin.setup import init_admin
from app.api.admin_applications import router as admin_applications_router
from app.api.admin_campaign_windows import router as admin_campaign_windows_router
from app.api.admin_contacts import router as admin_contacts_router
from app.api.admin_registrations import router as admin_registrations_router
from app.api.admin_stats import router as admin_stats_router
from app.api.auth import router as auth_router
from app.api.forms import router as forms_router
from app.api.payments import router as payments_router
from app.api.public import router as public_router
from app.api.rbac import router as rbac_router
from app.core.config import get_settings
from app.core.rate_limit import limiter

settings = get_settings()

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

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(auth_router)
app.include_router(rbac_router)
app.include_router(public_router)
app.include_router(forms_router)
app.include_router(payments_router)
app.include_router(admin_applications_router)
app.include_router(admin_campaign_windows_router)
app.include_router(admin_stats_router)
app.include_router(admin_registrations_router)
app.include_router(admin_contacts_router)

init_admin(app)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
