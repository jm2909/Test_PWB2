"""Typed application settings, read from the environment and an optional .env file."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

API_PREFIX = "/api/v1"


class DatabaseSettings(BaseSettings):
    """Only the DB URL, so migrations/seed run without app secrets."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    database_url: str = "sqlite:///./app.db"


class Settings(BaseSettings):
    """All runtime configuration. JWT_SECRET_KEY is required: startup fails without it."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    database_url: str = "sqlite:///./app.db"
    jwt_secret_key: str = Field(min_length=16)
    jwt_expire_minutes: int = Field(default=30, ge=1)
    session_inactivity_minutes: int = Field(default=30, ge=1)
    cors_origins: str = "http://localhost:5173"
    debug: bool = False
    seed_on_start: bool = False
    rate_limit_enabled: bool = True
    login_rate_limit: str = "10/minute"
    adapter_mode: str = "simulated"
    ai_provider_url: str = ""
    ai_provider_key: str = ""
    otel_exporter_otlp_endpoint: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip() and o.strip() != "*"]


@lru_cache
def get_settings() -> Settings:
    # Required values are supplied by the environment / .env file, not by constructor args.
    return Settings()  # type: ignore[call-arg]
