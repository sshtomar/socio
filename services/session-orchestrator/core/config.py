"""
Configuration management for the session orchestrator service.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings sourced from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # HTTP service configuration
    service_host: str = "0.0.0.0"
    service_port: int = 8002
    debug: bool = False

    # Modal integration
    modal_app_name: str = "socio-marimo"
    modal_launch_function: str = "run_marimo_session"
    modal_timeout_seconds: int = 7200
    modal_volume_notebooks: str = "marimo-notebooks"
    modal_volume_cache: str = "marimo-uv-cache"
    modal_token_length: int = 24

    # Storage configuration
    workspace_storage_root: str = "./data/workspaces"
    autosave_enabled: bool = True
    autosave_interval_seconds: int = 60

    # Optional R2/S3 configuration
    r2_enabled: bool = False
    r2_bucket: Optional[str] = None
    r2_endpoint_url: Optional[str] = None
    r2_access_key_id: Optional[str] = None
    r2_secret_access_key: Optional[str] = None

    # Observability
    enable_logfire: bool = False
    log_level: str = "INFO"


@lru_cache()
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()
