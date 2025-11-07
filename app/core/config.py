"""
TDS Core - Configuration Management
Handles all application settings using Pydantic Settings
"""
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ========================================================================
    # APPLICATION
    # ========================================================================
    app_name: str = "TDS_Core"
    app_version: str = "1.0.0"
    environment: str = Field(default="production", pattern="^(development|staging|production)$")
    debug: bool = False
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")

    # API Server
    api_host: str = "0.0.0.0"
    api_port: int = Field(default=8001, ge=1024, le=65535)
    api_workers: int = Field(default=4, ge=1, le=32)
    api_reload: bool = False

    # ========================================================================
    # DATABASE
    # ========================================================================
    database_host: str = "localhost"
    database_port: int = Field(default=5432, ge=1024, le=65535)
    database_name: str = "tsh_erp"
    database_user: str = "postgres"
    database_password: str = ""  # Will use DATABASE_URL from .env if empty

    # Connection Pool
    database_pool_size: int = Field(default=20, ge=5, le=100)
    database_max_overflow: int = Field(default=10, ge=0, le=50)
    database_pool_timeout: int = Field(default=30, ge=10, le=300)

    # Full URL (computed)
    database_url: Optional[str] = None

    @property
    def get_database_url(self) -> str:
        """Generate database URL from components"""
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+asyncpg://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    @property
    def get_sync_database_url(self) -> str:
        """Generate synchronous database URL (for Alembic migrations)"""
        return (
            f"postgresql://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    # ========================================================================
    # SECURITY
    # ========================================================================
    secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = Field(default=60, ge=5, le=1440)
    jwt_refresh_token_expire_days: int = Field(default=7, ge=1, le=30)

    # API Keys
    webhook_api_key: Optional[str] = None
    zoho_webhook_secret: Optional[str] = None

    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "https://erp.tsh.sale",
        "https://tsh.sale"
    ]
    cors_allow_credentials: bool = True

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ========================================================================
    # ZOHO INTEGRATION
    # ========================================================================
    zoho_client_id: Optional[str] = None
    zoho_client_secret: Optional[str] = None
    zoho_refresh_token: Optional[str] = None
    zoho_access_token: Optional[str] = None
    zoho_organization_id: Optional[str] = None
    zoho_region: str = Field(default="US", pattern="^(US|EU|IN)$")

    @property
    def zoho_api_base(self) -> str:
        """Get Zoho API base URL based on region"""
        region_urls = {
            "US": "https://www.zohoapis.com",
            "EU": "https://www.zohoapis.eu",
            "IN": "https://www.zohoapis.in"
        }
        return region_urls.get(self.zoho_region, region_urls["US"])

    # ========================================================================
    # TDS CORE CONFIGURATION
    # ========================================================================
    # Sync Settings
    tds_max_retry_attempts: int = Field(default=3, ge=1, le=10)
    tds_retry_backoff_base_ms: int = Field(default=1000, ge=100, le=10000)
    tds_retry_backoff_max_ms: int = Field(default=60000, ge=1000, le=300000)
    tds_batch_size: int = Field(default=100, ge=10, le=1000)
    tds_lock_timeout_seconds: int = Field(default=300, ge=30, le=3600)
    tds_queue_poll_interval_ms: int = Field(default=1000, ge=100, le=10000)

    # Alert Settings
    tds_alert_failure_rate_threshold: float = Field(default=0.05, ge=0.0, le=1.0)
    tds_alert_queue_backlog_threshold: int = Field(default=1000, ge=100, le=100000)
    tds_alert_sync_lag_threshold_minutes: int = Field(default=15, ge=1, le=1440)

    # Cleanup Settings
    tds_inbox_retention_days: int = Field(default=7, ge=1, le=90)
    tds_logs_retention_days: int = Field(default=90, ge=7, le=365)
    tds_metrics_retention_days: int = Field(default=30, ge=7, le=365)

    # ========================================================================
    # NOTIFICATIONS
    # ========================================================================
    # Email (SMTP)
    smtp_enabled: bool = False
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = Field(default=587, ge=1, le=65535)
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from: str = "noreply@tsh.sale"
    smtp_tls: bool = True

    # Slack
    slack_enabled: bool = False
    slack_webhook_url: Optional[str] = None

    # Telegram
    telegram_enabled: bool = False
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None

    # ========================================================================
    # REDIS (Optional)
    # ========================================================================
    redis_enabled: bool = False
    redis_host: str = "localhost"
    redis_port: int = Field(default=6379, ge=1, le=65535)
    redis_db: int = Field(default=0, ge=0, le=15)
    redis_password: Optional[str] = None
    redis_url: Optional[str] = None

    @property
    def get_redis_url(self) -> str:
        """Generate Redis URL"""
        if self.redis_url:
            return self.redis_url
        password_part = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{password_part}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # Convenience property for cache module
    @property
    def REDIS_URL(self) -> str:
        """Alias for get_redis_url for cache module compatibility"""
        return self.get_redis_url

    @property
    def REDIS_ENABLED(self) -> bool:
        """Alias for redis_enabled for cache module compatibility"""
        return self.redis_enabled

    # ========================================================================
    # MONITORING
    # ========================================================================
    prometheus_enabled: bool = True
    prometheus_port: int = Field(default=9090, ge=1024, le=65535)

    # Sentry
    sentry_enabled: bool = False
    sentry_dsn: Optional[str] = None

    # ========================================================================
    # LOGGING
    # ========================================================================
    log_format: str = Field(default="json", pattern="^(json|text)$")
    log_file: str = "/var/log/tds_core/api.log"
    log_max_bytes: int = Field(default=10485760, ge=1048576, le=104857600)  # 1MB to 100MB
    log_backup_count: int = Field(default=5, ge=1, le=30)

    # ========================================================================
    # RATE LIMITING
    # ========================================================================
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = Field(default=60, ge=10, le=1000)
    rate_limit_per_hour: int = Field(default=1000, ge=100, le=100000)

    # ========================================================================
    # DEVELOPMENT
    # ========================================================================
    dev_reload: bool = False

    # API Documentation
    docs_enabled: bool = True
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"

    # ========================================================================
    # TESTING
    # ========================================================================
    test_database_url: Optional[str] = None

    # ========================================================================
    # COMPUTED PROPERTIES
    # ========================================================================
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == "production"

    @property
    def is_testing(self) -> bool:
        """Check if running in test mode"""
        return self.test_database_url is not None


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment (useful for testing)"""
    global _settings
    _settings = Settings()
    return _settings


# Convenience access
settings = get_settings()


# ============================================================================
# CONFIGURATION SUMMARY
# ============================================================================
def print_config_summary():
    """Print non-sensitive configuration for debugging"""
    s = settings
    print("=" * 80)
    print("TDS CORE - CONFIGURATION SUMMARY")
    print("=" * 80)
    print(f"Environment: {s.environment}")
    print(f"Debug Mode: {s.debug}")
    print(f"Log Level: {s.log_level}")
    print(f"API Host: {s.api_host}:{s.api_port}")
    print(f"Workers: {s.api_workers}")
    print(f"Database: {s.database_name} @ {s.database_host}:{s.database_port}")
    print(f"Pool Size: {s.database_pool_size} (max overflow: {s.database_max_overflow})")
    print(f"Zoho Region: {s.zoho_region}")
    print(f"Zoho API Base: {s.zoho_api_base}")
    print(f"Max Retry Attempts: {s.tds_max_retry_attempts}")
    print(f"Batch Size: {s.tds_batch_size}")
    print(f"Queue Poll Interval: {s.tds_queue_poll_interval_ms}ms")
    print(f"Notifications: SMTP={s.smtp_enabled}, Slack={s.slack_enabled}, Telegram={s.telegram_enabled}")
    print(f"Redis: {s.redis_enabled}")
    print(f"Prometheus: {s.prometheus_enabled}")
    print(f"Sentry: {s.sentry_enabled}")
    print(f"Rate Limiting: {s.rate_limit_enabled}")
    print(f"API Docs: {s.docs_enabled}")
    print("=" * 80)


if __name__ == "__main__":
    # Test configuration loading
    print_config_summary()
