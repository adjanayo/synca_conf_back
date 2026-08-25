from fastapi import FastAPI

from app.core.config import get_settings

settings = get_settings()

docs_enabled = settings.environment != "production"

app = FastAPI(
    title=settings.app_name,
    docs_url="/docs" if docs_enabled else None,
    redoc_url="/redoc" if docs_enabled else None,
    openapi_url="/openapi.json" if docs_enabled else None,
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
