"""
Configuration management using pydantic-settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Anthropic API
    anthropic_api_key: str
    default_model: str = "claude-sonnet-4-20250514"
    router_model: str = "claude-3-5-haiku-20241022"

    # Service configuration
    service_host: str = "0.0.0.0"
    service_port: int = 8000
    log_level: str = "INFO"

    # Integration URLs
    workspace_api_url: str = "http://localhost:8001"
    session_orchestrator_url: str = "http://localhost:8002"

    # Feature flags
    enable_self_critique: bool = False
    max_tokens_per_request: int = 8000
    enable_usage_tracking: bool = True

    # Timeouts
    agent_timeout_seconds: int = 120
    tool_timeout_seconds: int = 30


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
