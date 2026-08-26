from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "SYNCA CONF 2027 API"
    environment: str = "local"  # local | staging | production

    db_host: str = "db"
    db_port: int = 3306
    mysql_user: str = "syncaconf"
    mysql_password: str = "change-me-app"
    mysql_database: str = "syncaconf"

    # No default on purpose (security review finding): a hardcoded fallback
    # here would be the actual production signing key for any deployment
    # that forgets to set JWT_SECRET_KEY, since nothing else would catch it
    # (the string is 32+ bytes, so PyJWT's InsecureKeyLengthWarning would
    # never fire either). Missing the env var now fails startup loudly.
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Empty by default -- app/services/recaptcha.py treats an empty key as
    # "not configured" and skips verification (local dev/CI has no real
    # Google reCAPTCHA credentials). Production must set a real key.
    recaptcha_secret_key: str = ""
    recaptcha_min_score: float = 0.5

    # Backblaze B2 (S3-compatible) -- see app/services/storage.py. Empty
    # defaults are fine for local dev/CI, which never call upload_file for
    # real; production must set all three.
    b2_endpoint_url: str = ""
    b2_key_id: str = ""
    b2_application_key: str = ""
    b2_bucket_name: str = ""
    b2_public_url: str = ""

    # Resend (app/services/email_service.py) -- empty key means dev mode:
    # emails are logged via loguru, never actually sent (planning_fastapi.md
    # §1: no SMTP test container).
    resend_api_key: str = ""
    resend_from_email: str = "no-reply@synca.conf"

    # Payment webhook signing secrets (app/services/webhook_verification.py).
    # Wave/Orange Money's exact signature scheme isn't published anywhere
    # this project has access to -- verify_hmac_signature() assumes the
    # common HMAC-SHA256-over-raw-body pattern; confirm against their real
    # docs before accepting live traffic.
    stripe_webhook_secret: str = ""
    wave_webhook_secret: str = ""
    orange_money_webhook_secret: str = ""

    # Comma-separated in .env, e.g. "http://localhost:3000,http://localhost:5173".
    # Wildcard-free by design (see security-hardening: CORS restricted to the
    # real frontend domain, not "*") -- dev defaults cover the two most common
    # local dev-server ports.
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def database_url(self) -> str:
        return (
            f"mysql+asyncmy://{self.mysql_user}:{self.mysql_password}"
            f"@{self.db_host}:{self.db_port}/{self.mysql_database}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
