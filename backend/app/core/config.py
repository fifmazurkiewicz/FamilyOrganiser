from functools import cached_property
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / ".env", BASE_DIR.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "FamilyOrganiser"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+asyncpg://localhost:5432/familyorg"

    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "changeme-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    CORS_ORIGINS_STR: str = "http://localhost:3000,http://localhost:80"

    ADMIN_EMAIL: str = "admin@admin.com"
    ADMIN_PASSWORD: str = "changeme"

    MAX_FAMILY_GROUP_MEMBERS: int = 20
    APPROVAL_REQUEST_EXPIRE_DAYS: int = 7
    MAX_SECURITY_QUESTION_ATTEMPTS: int = 5
    EXCHANGE_RATE_FETCH_HOUR: int = 6

    @cached_property
    def CORS_ORIGINS(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS_STR.split(",") if o.strip()]


settings = Settings()
