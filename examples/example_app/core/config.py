"""
Application settings loaded from environment variables.

Uses pydantic-settings to validate and parse the .env file.
All configuration lives here so the rest of the app imports `settings`.
"""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Example App"
    app_version: str = "0.1.0"
    api_default_version: str = Field(
        default="v1",
        description="Default API version when API-Version header is omitted",
    )
    debug: bool = False
    environment: str = Field(default="development", description="development | staging | production")
    database_url: str = Field(description="Async Postgres connection string")
    db_pool_size: int = Field(default=5, ge=1, le=20)
    db_max_overflow: int = Field(default=10, ge=0, le=50)
    db_echo: bool = False

    cors_origins: list[str] = Field(default=["*"])

    log_level: str = Field(default="INFO", description="DEBUG | INFO | WARNING | ERROR | CRITICAL")

    @field_validator("database_url", mode="before")
    @classmethod
    def ensure_async_driver(cls, v: str) -> str:
        """Transparently swap the sync driver for asyncpg."""
        if v and "+asyncpg" not in v:
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton – import this everywhere."""
    return Settings()
