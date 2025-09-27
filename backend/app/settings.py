from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional


class Settings(BaseSettings):
    # ----------------------------
    # Database
    # ----------------------------
    database_url: str = Field(..., env="DATABASE_URL")

    # ----------------------------
    # Security & Authentication
    # ----------------------------
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # ----------------------------
    # Application
    # ----------------------------
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")
    port: int = Field(4000, env="PORT")

    # ----------------------------
    # CORS
    # ----------------------------
    cors_origins: List[str] = Field(..., env="CORS_ORIGINS")

    @validator("cors_origins", pre=True)
    def split_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ----------------------------
    # Rate Limiting
    # ----------------------------
    rate_limit_per_minute: int = Field(100, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(1000, env="RATE_LIMIT_PER_HOUR")

    # ----------------------------
    # Database Pooling (PostgreSQL production)
    # ----------------------------
    db_pool_size: int = Field(20, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(10, env="DB_MAX_OVERFLOW")
    db_pool_recycle: int = Field(3600, env="DB_POOL_RECYCLE")
    db_ssl: bool = Field(False, env="DB_SSL")

    @validator("db_ssl", pre=True)
    def parse_bool(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)

    # ----------------------------
    # Email Service (optional)
    # ----------------------------
    smtp_server: Optional[str] = Field(None, env="SMTP_SERVER")
    smtp_port: Optional[int] = Field(None, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(None, env="SMTP_PASSWORD")
    notification_email: Optional[str] = Field(None, env="NOTIFICATION_EMAIL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# ✅ global settings instance
settings = Settings()