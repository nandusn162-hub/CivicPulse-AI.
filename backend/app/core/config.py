import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Optional, List

class Settings(BaseSettings):
    # General app settings
    APP_NAME: str = "CivicPulse AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    # CORS origins (comma‑separated in .env)
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Database URLs
    DATABASE_URL: str = "sqlite+aiosqlite:///./civicpulse.db"
    DATABASE_URL_SYNC: str = "sqlite:///./civicpulse.db"

    @model_validator(mode="after")
    def normalize_database_urls(self) -> "Settings":
        """Normalize database URLs so async and sync engines use the correct drivers."""
        # 1. Normalize async DATABASE_URL:
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("sqlite:///") and not url.startswith("sqlite+"):
            url = url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
        self.DATABASE_URL = url

        # 2. Normalize sync DATABASE_URL_SYNC:
        sync_url = self.DATABASE_URL_SYNC
        if sync_url.startswith("postgres://"):
            sync_url = sync_url.replace("postgres://", "postgresql://", 1)
        elif sync_url.startswith("postgresql+asyncpg://"):
            sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql://", 1)
        elif sync_url.startswith("sqlite+aiosqlite:///"):
            sync_url = sync_url.replace("sqlite+aiosqlite:///", "sqlite:///", 1)
        self.DATABASE_URL_SYNC = sync_url

        return self

    # Security / JWT
    SECRET_KEY: str = "change-me-to-a-32-byte-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Gemini AI (optional)
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_VISION_MODEL: str = "gemini-2.0-flash"

    # File storage configuration
    STORAGE_PROVIDER: str = "local"  # or "supabase"
    STORAGE_LOCAL_PATH: str = "./uploads"
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_BUCKET: str = "civicpulse-evidence"

    # Weather API (optional)
    WEATHER_API_KEY: Optional[str] = None
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5"

    # Rate limiting / upload limits
    RATE_LIMIT_PER_MINUTE: int = 60
    UPLOAD_MAX_SIZE_MB: int = 10

    # Demo mode flag – when true the Gemini client returns demo data
    DEMO_MODE: bool = True
    DEMO_CITY: str = "Whitefield Demo City"

    # Super admin credentials for seed data
    SUPER_ADMIN_EMAIL: str = "admin@civicpulse.ai"
    SUPER_ADMIN_PASSWORD: str = "CivicAdmin123!"

    class Config:
        env_file = ".env"
        case_sensitive = True
        env_prefix = ""
        # allow reading from .env.example when .env missing (useful for dev)
        env_file_encoding = "utf-8"

settings = Settings()
