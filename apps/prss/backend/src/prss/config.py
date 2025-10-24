"""Configuration management for PRSS"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Database
    prss_db_url: str = "postgresql+psycopg://prss_user:prss_pass@localhost:5432/prss_db"

    # JWT
    prss_jwt_secret: str
    prss_jwt_algorithm: str = "HS256"
    prss_jwt_expire_minutes: int = 30

    # Integration APIs
    inventory_api_base: str
    sales_api_base: str
    accounting_api_base: str

    # Integration Auth
    inventory_api_token: str = ""
    sales_api_token: str = ""
    accounting_api_token: str = ""

    # Feature Flags
    instant_refund_threshold: float = 1500.0
    enable_auto_restock: bool = True
    enable_ai_inspection: bool = False

    # Application
    app_name: str = "TSH After-Sales Operations System"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"

    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8001"
    ]

    # File Upload
    max_photo_size: int = 5242880  # 5MB
    allowed_photo_types: List[str] = ["image/jpeg", "image/png", "image/webp"]

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Observability
    enable_request_id: bool = True
    enable_tracing: bool = True

    # API Settings
    api_v1_prefix: str = "/v1"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export settings instance
settings = get_settings()
