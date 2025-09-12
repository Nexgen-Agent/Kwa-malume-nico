from pydantic import BaseSettings, Field, PostgresDsn
from typing import Optional
import secrets

class Settings(BaseSettings):
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    
    # Security
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Environment
    environment: str = "development"
    debug: bool = False
    
    # Rate limiting
    rate_limit_per_minute: int = 100
    rate_limit_per_hour: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
