"""
Settings Schemas
================

Pydantic models for settings endpoints.
"""

from .system import TranslationUpdate
from .backup import BackupRequest, RestoreRequest
from .zoho import (
    ZohoIntegrationConfig,
    ZohoModuleStatus,
    ZohoFieldMapping,
    ZohoSyncMapping,
    ZohoSyncLog,
    ZohoDataAnalysis,
    ZohoSyncControl,
)

__all__ = [
    "TranslationUpdate",
    "BackupRequest",
    "RestoreRequest",
    "ZohoIntegrationConfig",
    "ZohoModuleStatus",
    "ZohoFieldMapping",
    "ZohoSyncMapping",
    "ZohoSyncLog",
    "ZohoDataAnalysis",
    "ZohoSyncControl",
]
