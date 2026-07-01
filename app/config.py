"""Configuration module for EventWatch AI application."""

from pydantic_settings import BaseSettings
from typing import Optional
import logging


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "EventWatch AI"
    app_version: str = "2.0.0"
    debug: bool = False

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/eventwatch"
    database_echo: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Webhook
    webhook_url: Optional[str] = None
    webhook_timeout: int = 10

    # Anomaly Detection
    isolation_forest_contamination: float = 0.05
    anomaly_threshold: float = 0.7

    # Alert Settings
    alert_batch_size: int = 100
    alert_retention_days: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
