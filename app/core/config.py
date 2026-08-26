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
