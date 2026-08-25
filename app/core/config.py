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

    @property
    def database_url(self) -> str:
        return (
            f"mysql+asyncmy://{self.mysql_user}:{self.mysql_password}"
            f"@{self.db_host}:{self.db_port}/{self.mysql_database}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
