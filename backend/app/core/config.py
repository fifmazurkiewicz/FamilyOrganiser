from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "FamilyOrganiser"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://familyorg:familyorg@localhost:5432/familyorg"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "changeme-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:80"]

    # Groups
    MAX_FAMILY_GROUP_MEMBERS: int = 20

    # Approval flow
    APPROVAL_REQUEST_EXPIRE_DAYS: int = 7

    # Security question
    MAX_SECURITY_QUESTION_ATTEMPTS: int = 5

    # Exchange rate schedule (hour in UTC)
    EXCHANGE_RATE_FETCH_HOUR: int = 6

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
