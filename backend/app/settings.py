from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import Field

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 4000

    CORS_ORIGINS: list[str] = []

    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000

    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 3600
    DB_SSL: bool = False

    SMTP_SERVER: str | None = None
    SMTP_PORT: str | int | None = None
    SMTP_USERNAME: Optional[str] = Field(None, env="SMTP_USERNAME")
    SMTP_PASSWORD: str | None = None
    NOTIFICATION_EMAIL: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()