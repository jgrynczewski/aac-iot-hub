"""Application configuration using pydantic-settings."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API settings
    api_port: int = 8765
    api_host: str = "0.0.0.0"

    # Logging
    log_level: str = "info"

    # Discovery
    discovery_timeout: int = 5  # seconds for SSDP discovery

    class Config:
        env_prefix = "AAC_"  # All env vars start with AAC_
        case_sensitive = False


# Global settings instance
settings = Settings()