"""
Zoho Integration Schemas
========================

Pydantic models for Zoho integration settings endpoints.
"""

from pydantic import BaseModel
from typing import Dict, Any, List, Optional


class ZohoIntegrationConfig(BaseModel):
    """Zoho integration configuration"""
    enabled: bool = False
    client_id: str = ""
    client_secret: str = ""
    refresh_token: str = ""
    organization_id: str = ""


class ZohoModuleStatus(BaseModel):
    """Status of a Zoho module"""
    name: str
    enabled: bool
    last_sync: Optional[str] = None


class ZohoFieldMapping(BaseModel):
    """Field mapping between Zoho and TSH ERP"""
    zoho_field: str
    tsh_field: str
    field_type: str  # text, number, date, boolean, image, etc.
    is_required: bool = False
    default_value: Optional[str] = None
    transformation_rule: Optional[str] = None  # e.g., "uppercase", "lowercase", "date_format"


class ZohoSyncMapping(BaseModel):
    """Sync mapping configuration for a Zoho entity"""
    entity_type: str  # "item", "customer", "vendor"
    enabled: bool = True
    sync_direction: str = "zoho_to_tsh"  # One direction: Zoho → TSH
    sync_mode: str = "real_time"  # real_time, scheduled, manual
    sync_frequency: Optional[int] = None  # Minutes (for scheduled sync)
    field_mappings: List[ZohoFieldMapping]
    sync_images: bool = True
    sync_attachments: bool = False
    conflict_resolution: str = "zoho_wins"  # zoho_wins, tsh_wins, manual
    auto_create: bool = True  # Auto create if not exists in TSH
    auto_update: bool = True  # Auto update if exists in TSH
    delete_sync: bool = False  # Sync deletions from Zoho
    last_sync: Optional[str] = None
    last_sync_status: Optional[str] = None
    total_synced: int = 0
    total_errors: int = 0


class ZohoSyncLog(BaseModel):
    """Log entry for sync operation"""
    sync_id: str
    entity_type: str
    entity_id: str
    zoho_id: str
    operation: str  # create, update, delete
    status: str  # success, error, skipped
    error_message: Optional[str] = None
    synced_fields: List[str]
    timestamp: str


class ZohoDataAnalysis(BaseModel):
    """Analysis of Zoho data"""
    entity_type: str
    total_records: int
    new_records: int  # Not in TSH
    updated_records: int  # Modified in Zoho
    matched_records: int  # Already synced
    error_records: int
    last_analyzed: str
    field_statistics: Dict[str, Any]


class ZohoSyncControl(BaseModel):
    """Real-time sync control settings"""
    webhook_enabled: bool = True
    webhook_url: str = ""
    webhook_secret: str = ""
    auto_sync_enabled: bool = True
    sync_interval_minutes: int = 15
    max_retries: int = 3
    retry_delay_seconds: int = 60
