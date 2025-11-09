"""Application configuration using Pydantic Settings."""
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid",
    )

    # Application
    app_name: str = Field(default="wwiii-apic", description="Application name")
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Environment",
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Log level",
    )

    # Database
    database_url: str = Field(
        ...,
        description="PostgreSQL database URL (postgresql+asyncpg://...)",
    )
    db_pool_size: int = Field(default=10, ge=1, description="Database pool size")
    db_max_overflow: int = Field(
        default=20,
        ge=0,
        description="Database max overflow",
    )

    # API
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")
    api_title: str = Field(default="WWIII API", description="API title")
    api_version: str = Field(default="0.1.0", description="API version")

    # Security (no defaults for secrets)
    secret_key: str | None = Field(default=None, description="Secret key")
    jwt_secret_key: str | None = Field(default=None, description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: int = Field(
        default=30,
        ge=1,
        description="JWT access token expiration in minutes",
    )

    # Observability
    otel_exporter_otlp_endpoint: str | None = Field(
        default=None,
        description="OpenTelemetry OTLP endpoint",
    )
    otel_service_name: str = Field(
        default="wwiii-apic",
        description="OpenTelemetry service name",
    )
    otel_resource_attributes: str = Field(
        default="service.name=wwiii-apic,service.version=0.1.0",
        description="OpenTelemetry resource attributes",
    )

    # Prometheus
    prometheus_enabled: bool = Field(
        default=True,
        description="Enable Prometheus metrics",
    )
    metrics_port: int = Field(default=9090, ge=1024, le=65535, description="Metrics port")

    # CORS
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="CORS origins (comma-separated)",
    )

    # Rate Limiting
    rate_limit_enabled: bool = Field(
        default=True,
        description="Enable rate limiting",
    )
    rate_limit_per_minute: int = Field(
        default=60,
        ge=1,
        description="Rate limit per minute",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

