"""
TSH NeuroLink - Configuration Management
Handles all application settings from environment variables
"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application Info
    app_name: str = "TSH NeuroLink"
    app_version: str = "1.0.0"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")

    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8002, env="PORT")
    workers: int = Field(default=4, env="WORKERS")

    # Database Configuration (TSH ERP PostgreSQL)
    database_url: str = Field(
        default="postgresql+asyncpg://khaleel:khaleel@localhost:5432/tsh_erp",
        env="DATABASE_URL"
    )
    db_pool_size: int = Field(default=20, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=10, env="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")

    # Redis Configuration (Event Bus)
    redis_url: str = Field(
        default="redis://localhost:6379/2",  # DB 2 for NeuroLink
        env="REDIS_URL"
    )
    redis_channel_prefix: str = Field(default="neurolink:", env="REDIS_CHANNEL_PREFIX")

    # Authentication (Integrate with TSH ERP)
    jwt_secret_key: str = Field(
        default="your-secret-key-change-in-production",
        env="JWT_SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_minutes: int = Field(default=30, env="JWT_EXPIRATION_MINUTES")

    # TSH ERP API Integration
    tsh_erp_api_url: str = Field(
        default="https://api.tsh.sale/erp",
        env="TSH_ERP_API_URL"
    )
    tsh_erp_api_key: Optional[str] = Field(default=None, env="TSH_ERP_API_KEY")

    # WebSocket Configuration
    ws_heartbeat_interval: int = Field(default=30, env="WS_HEARTBEAT_INTERVAL")
    ws_max_connections: int = Field(default=1000, env="WS_MAX_CONNECTIONS")

    # Event Processing
    event_batch_size: int = Field(default=100, env="EVENT_BATCH_SIZE")
    event_poll_interval_ms: int = Field(default=1000, env="EVENT_POLL_INTERVAL_MS")
    event_retry_max_attempts: int = Field(default=3, env="EVENT_RETRY_MAX_ATTEMPTS")
    event_retention_days: int = Field(default=90, env="EVENT_RETENTION_DAYS")

    # Notification Settings
    notification_batch_size: int = Field(default=50, env="NOTIFICATION_BATCH_SIZE")
    notification_rate_limit_per_user_hour: int = Field(
        default=100,
        env="NOTIFICATION_RATE_LIMIT_PER_USER_HOUR"
    )

    # Email Configuration (for email notifications)
    smtp_enabled: bool = Field(default=False, env="SMTP_ENABLED")
    smtp_host: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, env="SMTP_USER")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    smtp_from_email: str = Field(
        default="notifications@tsh.sale",
        env="SMTP_FROM_EMAIL"
    )

    # SMS Configuration (for SMS notifications)
    sms_enabled: bool = Field(default=False, env="SMS_ENABLED")
    sms_provider: str = Field(default="twilio", env="SMS_PROVIDER")  # twilio, nexmo, etc.
    sms_account_sid: Optional[str] = Field(default=None, env="SMS_ACCOUNT_SID")
    sms_auth_token: Optional[str] = Field(default=None, env="SMS_AUTH_TOKEN")
    sms_from_number: Optional[str] = Field(default=None, env="SMS_FROM_NUMBER")

    # Telegram Configuration
    telegram_enabled: bool = Field(default=False, env="TELEGRAM_ENABLED")
    telegram_bot_token: Optional[str] = Field(default=None, env="TELEGRAM_BOT_TOKEN")

    # Monitoring & Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")  # json or text
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")

    # CORS Configuration
    cors_origins: list[str] = Field(
        default=[
            "http://localhost:3000",
            "https://erp.tsh.sale",
            "https://shop.tsh.sale"
        ],
        env="CORS_ORIGINS"
    )

    # Rule Engine
    rule_engine_enabled: bool = Field(default=True, env="RULE_ENGINE_ENABLED")
    rule_evaluation_timeout_seconds: int = Field(
        default=5,
        env="RULE_EVALUATION_TIMEOUT_SECONDS"
    )

    # Performance
    enable_query_logging: bool = Field(default=False, env="ENABLE_QUERY_LOGGING")
    slow_query_threshold_ms: int = Field(default=1000, env="SLOW_QUERY_THRESHOLD_MS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Dependency for FastAPI routes to inject settings"""
    return settings
