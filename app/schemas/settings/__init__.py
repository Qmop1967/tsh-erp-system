"""
Settings Schemas
================

Pydantic models for settings endpoints.
"""

from .system import TranslationUpdate
from .backup import (
    BackupRequest,
    BackupCreateRequest,
    BackupScheduleRequest,
    RestoreRequest,
    BackupRestoreRequest,
)
from .security import (
    GrantPermissionRequest,
    RevokePermissionRequest,
    SystemHealthResponse,
)
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
    # System
    "TranslationUpdate",
    # Backup
    "BackupRequest",
    "BackupCreateRequest",
    "BackupScheduleRequest",
    "RestoreRequest",
    "BackupRestoreRequest",
    # Security
    "GrantPermissionRequest",
    "RevokePermissionRequest",
    "SystemHealthResponse",
    # Zoho
    "ZohoIntegrationConfig",
    "ZohoModuleStatus",
    "ZohoFieldMapping",
    "ZohoSyncMapping",
    "ZohoSyncLog",
    "ZohoDataAnalysis",
    "ZohoSyncControl",
]
