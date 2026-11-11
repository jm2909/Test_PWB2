"""Typed application settings (environment-driven)."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

NON_PRODUCTION_ENVIRONMENTS = {"development", "local", "test", "testing"}
_DEV_SECRET = "dev-only-insecure-secret-do-not-use-in-production"  # noqa: S105


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    environment: str = "development"
    debug: bool = False
    database_url: str = "sqlite:///./app.db"
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    session_ttl_minutes: int = Field(480, ge=1)
    session_inactivity_minutes: int = Field(30, ge=1)
    cors_origins: str = "http://localhost:5173"
    data_rights_fulfillment_days: int = Field(30, ge=1)
    freshness_stale_after_hours: int = Field(24, ge=1)
    wearable_providers: str = "fitband,pulsewear"
    login_rate_limit: str = "10/minute"
    rate_limit_enabled: bool = True
    trust_forwarded_for: bool = False
    audit_retention_days: int = Field(365, ge=1)
    seed_on_startup: bool = False
    bcrypt_rounds: int = Field(12, ge=12, le=16)
    otel_exporter_otlp_endpoint: str = ""

    @property
    def is_production_like(self) -> bool:
        return self.environment.strip().lower() not in NON_PRODUCTION_ENVIRONMENTS

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def wearable_provider_list(self) -> list[str]:
        return [p.strip().lower() for p in self.wearable_providers.split(",") if p.strip()]

    @property
    def docs_enabled(self) -> bool:
        return self.debug or not self.is_production_like

    @model_validator(mode="after")
    def _validate_environment(self) -> Settings:
        if self.is_production_like:
            if len(self.jwt_secret_key) < 32:
                raise ValueError(
                    "JWT_SECRET_KEY must be set (>= 32 characters) when ENVIRONMENT is "
                    f"'{self.environment}'. Generate one with: "
                    'python -c "import secrets;print(secrets.token_urlsafe(48))"'
                )
            if "*" in self.cors_origins_list:
                raise ValueError("CORS_ORIGINS must list explicit origins in production")
        elif not self.jwt_secret_key:
            self.jwt_secret_key = _DEV_SECRET
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
