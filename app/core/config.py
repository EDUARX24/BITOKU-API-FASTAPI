from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración central de la aplicación."""

    PROJECT_NAME: str = "Bitoku API"
    API_V1_STR: str = "/api"
    DATABASE_URL: str
    TURSO_AUTH_TOKEN: str | None = None
    SECRET_KEY: str = "change-me-in-env"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ENV: str = "dev"
    APP_VERSION: str = "1.0.0"
    BACKEND_CORS_ORIGINS: list[str] = Field(default_factory=list)
    ENABLE_DOCS: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def is_dev(self) -> bool:
        return self.ENV.lower() == "dev"

    @property
    def local_dev_cors_regex(self) -> str | None:
        if not self.is_dev:
            return None
        return r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()