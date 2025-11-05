"""
Backup & Restore Schemas
========================

Pydantic models for backup and restore endpoints.
"""

from pydantic import BaseModel
from typing import Optional


class BackupRequest(BaseModel):
    """Request model for creating a backup"""
    include_data: bool = True
    include_schema: bool = True
    description: Optional[str] = None


class BackupCreateRequest(BaseModel):
    """Request model for creating a backup (alias for BackupRequest)"""
    include_data: bool = True
    include_schema: bool = True
    description: Optional[str] = None
    schedule: Optional[str] = None


class BackupScheduleRequest(BaseModel):
    """Request model for scheduling backups"""
    cron_expression: str
    include_data: bool = True
    include_schema: bool = True
    description: Optional[str] = None


class RestoreRequest(BaseModel):
    """Request model for restoring from backup"""
    backup_file: str
    restore_data: bool = True
    restore_schema: bool = True


class BackupRestoreRequest(BaseModel):
    """Request model for restoring from backup (alias for RestoreRequest)"""
    backup_file: str
    restore_data: bool = True
    restore_schema: bool = True
