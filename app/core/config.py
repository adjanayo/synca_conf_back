from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "SYNCA CONF 2027 API"
    environment: str = "local"  # local | staging | production


@lru_cache
def get_settings() -> Settings:
    return Settings()
