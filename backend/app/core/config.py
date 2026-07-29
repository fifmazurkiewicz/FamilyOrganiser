from functools import cached_property
from pathlib import Path
from typing import List
import ssl
import uuid

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def is_supabase_database_url(url: str) -> bool:
    return "supabase.com" in url or "supabase.co" in url


def normalize_database_url(url: str) -> str:
    """Supabase kopiuje postgresql:// — SQLAlchemy async wymaga postgresql+asyncpg://."""
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgresql://")
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgres://")
    return url


def postgres_connect_args(database_url: str) -> dict:
    """asyncpg + Supabase wymaga SSL; SQLite ma własne connect_args."""
    if "sqlite" in database_url:
        return {"check_same_thread": False}
    if "postgresql" in database_url or "postgres" in database_url:
        if is_supabase_database_url(database_url):
            # Pooler Supabase: TLS wymagany; transaction pooler (6543) + prepared statements.
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            return {
                "ssl": ctx,
                "statement_cache_size": 0,
                "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4()}__",
            }
        return {"ssl": True}
    return {}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / ".env", BASE_DIR.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "FamilyOrganiser"
    DEBUG: bool = False

    DATABASE_URL: str = "sqlite+aiosqlite:///./familyorg.db"

    # Legacy app JWT (local tests / AUTH_MODE=legacy)
    SECRET_KEY: str = "changeme-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Supabase Auth (production)
    SUPABASE_URL: str = ""
    SUPABASE_JWT_SECRET: str = ""
    SUPABASE_JWT_AUDIENCE: str = "authenticated"

    CORS_ORIGINS_STR: str = "http://localhost:3000,http://localhost:3001,http://localhost:80"

    ADMIN_EMAIL: str = "admin@admin.com"
    ADMIN_PASSWORD: str = "changeme"

    MAX_FAMILY_GROUP_MEMBERS: int = 20
    APPROVAL_REQUEST_EXPIRE_DAYS: int = 7
    MAX_SECURITY_QUESTION_ATTEMPTS: int = 5
    EXCHANGE_RATE_FETCH_HOUR: int = 6

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _normalize_database_url(cls, value: str) -> str:
        if isinstance(value, str):
            return normalize_database_url(value)
        return value

    @cached_property
    def CORS_ORIGINS(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS_STR.split(",") if o.strip()]

    @property
    def supabase_auth_enabled(self) -> bool:
        return bool(self.SUPABASE_URL.strip() or self.SUPABASE_JWT_SECRET.strip())

    @property
    def supabase_issuer(self) -> str:
        base = self.SUPABASE_URL.rstrip("/")
        return f"{base}/auth/v1" if base else ""

    @property
    def supabase_jwks_url(self) -> str:
        base = self.SUPABASE_URL.rstrip("/")
        return f"{base}/auth/v1/.well-known/jwks.json" if base else ""


settings = Settings()
