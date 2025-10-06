# app/config.py
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List, Optional


class Settings(BaseSettings):
    # -- App
    app_name: str = Field("Malume Nico API", env="APP_NAME")
    debug: bool = Field(True, env="DEBUG")
    environment: str = Field("development", env="ENVIRONMENT")
    port: int = Field(4000, env="PORT")

    # -- Security / JWT
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # -- Database
    database_url: str = Field("sqlite+aiosqlite:///./malume.db", env="DATABASE_URL")

    # -- CORS: accepts comma-separated string or JSON-like list
    cors_origins: List[str] = Field([], env="CORS_ORIGINS")

    # -- Rate limiting
    rate_limit_per_minute: int = Field(100, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(1000, env="RATE_LIMIT_PER_HOUR")

    # -- DB pooling (optional/postgres)
    db_pool_size: int = Field(20, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(10, env="DB_MAX_OVERFLOW")
    db_pool_recycle: int = Field(3600, env="DB_POOL_RECYCLE")
    db_ssl: bool = Field(False, env="DB_SSL")

    # -- SMTP (optional) — allow blank values safely
    smtp_server: Optional[str] = Field(None, env="SMTP_SERVER")
    smtp_port: Optional[int] = Field(None, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(None, env="SMTP_PASSWORD")
    notification_email: Optional[str] = Field(None, env="NOTIFICATION_EMAIL")

    # ------------------- Validators -------------------
    @field_validator("cors_origins", mode="before")
    def _parse_cors_origins(cls, v):
        # Accept a JSON-style list, a CSV string, or already-a-list
        if v is None:
            return []
        if isinstance(v, (list, tuple)):
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("[") and s.endswith("]"):
                # try to parse JSON-like list safely (no json import to avoid failure)
                inner = s[1:-1].strip()
                # split naive by comma — OK for simple lists like ["a","b"]
                parts = [p.strip().strip('"').strip("'") for p in inner.split(",") if p.strip()]
                return [p for p in parts if p]
            # fallback: comma-separated
            return [part.strip() for part in s.split(",") if part.strip()]
        return v

    @field_validator("debug", mode="before")
    def _parse_bool_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)

    @field_validator("db_ssl", mode="before")
    def _parse_bool_db_ssl(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)

    @field_validator("smtp_port", mode="before")
    def _smtp_port_to_int_or_none(cls, v):
        # Accept empty strings as None, or int strings
        if v is None or v == "":
            return None
        if isinstance(v, str) and v.isdigit():
            return int(v)
        if isinstance(v, (int, float)):
            return int(v)
        return None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # ignore any stray env fields you don't care about
        extra = "ignore"


# instantiate once and import from everywhere
settings = Settings()