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
    # Participant OTP login (app/api/participant_auth.py) -- deliberately
    # longer-lived than the admin access token: a one-shot event site where
    # re-entering an email + OTP code every 15 minutes would be poor UX for
    # someone checking their ticket days apart.
    participant_token_expire_hours: int = 24

    # Same reasoning as JWT_SECRET_KEY: no default, so a deployment that
    # forgets to set FERNET_KEY fails to start rather than silently
    # encrypting PII (7.8) with a key baked into the repo. Generate with
    # `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`.
    fernet_key: str

    # Initial superadmin bootstrap (app/cli/create_admin.py). No defaults on
    # purpose -- same rationale as JWT_SECRET_KEY/FERNET_KEY: a hardcoded
    # fallback would let any deployment forget to set these and silently get a
    # known admin credential. Dev/CI set ADMIN_EMAIL/ADMIN_PASSWORD in .env;
    # production must set real credentials.
    admin_email: str = ""
    admin_password: str = ""

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

    # app/core/logging_config.py (8.1): directory for the 3 rotating loguru
    # sinks (security/payment/app). Relative path is fine -- mounted as a
    # Docker volume in production, not baked into the image.
    log_dir: str = "logs"

    # app/services/ticket_pdf.py: printed on every ticket. Placeholder until
    # the real venue is confirmed -- set EVENT_VENUE in .env, no redeploy
    # needed since it's read at request time via get_settings().
    event_venue: str = "Lieu à confirmer"

    # Rappels waitlist récurrents (app/services/waitlist_reminder.py) : pas de
    # cron dans le projet -- une boucle asyncio en tâche de fond (démarrée
    # dans app/main.py) se réveille toutes les `check` minutes et relance un
    # email aux inscrits non enregistrés dont le dernier email date de plus de
    # `interval` jours, tant que la fenêtre `ticketing` reste ouverte.
    waitlist_reminder_interval_days: int = 3
    waitlist_reminder_check_interval_minutes: int = 60

    # Comma-separated in .env, e.g. "http://localhost:3000,http://localhost:5173".
    # Wildcard-free by design (see security-hardening: CORS restricted to the
    # real frontend domain, not "*") -- dev defaults cover the two most common
    # local dev-server ports, plus :4666 used by the front's prerender step
    # (scripts/prerender.mjs, `vite preview` -- ROADMAP_PUBLIC_SEO.md S1.6).
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:4666"

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
