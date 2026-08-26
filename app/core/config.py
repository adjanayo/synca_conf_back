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

    jwt_secret_key: str = "change-me-in-production-min-32-bytes-long"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

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
