"""
Base Integration Interface
==========================

Defines the standard interface that all external integrations must implement.
This ensures consistency across different integration types.

خدمة التكامل الأساسية - واجهة موحدة لجميع التكاملات الخارجية
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class IntegrationType(str, Enum):
    """نوع التكامل"""
    ZOHO = "zoho"
    CUSTOM = "custom"
    # Add more integration types as needed


class SyncMode(str, Enum):
    """وضع المزامنة"""
    FULL = "full"           # Full sync - import all data
    INCREMENTAL = "incremental"  # Only sync changes since last sync
    REALTIME = "realtime"   # Real-time webhook-based sync


class SyncStatus(str, Enum):
    """حالة المزامنة"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BaseIntegration(ABC):
    """
    Base class for all external system integrations
    الفئة الأساسية لجميع التكاملات مع الأنظمة الخارجية

    All integration implementations must inherit from this class
    and implement the required abstract methods.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize integration with configuration

        Args:
            config: Integration-specific configuration
        """
        self.config = config
        self.integration_type = self._get_integration_type()
        self.logger = logging.getLogger(f"{__name__}.{self.integration_type}")

    @abstractmethod
    def _get_integration_type(self) -> IntegrationType:
        """Return the integration type"""
        pass

    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Authenticate with the external system

        Returns:
            bool: True if authentication successful
        """
        pass

    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to the external system

        Returns:
            dict: Connection test results with status and details
        """
        pass

    @abstractmethod
    async def sync_entity(
        self,
        entity_type: str,
        entity_ids: Optional[List[str]] = None,
        mode: SyncMode = SyncMode.INCREMENTAL
    ) -> Dict[str, Any]:
        """
        Sync a specific entity type from external system

        Args:
            entity_type: Type of entity (e.g., 'products', 'customers')
            entity_ids: Optional list of specific entity IDs to sync
            mode: Sync mode (full, incremental, realtime)

        Returns:
            dict: Sync results with status and statistics
        """
        pass

    @abstractmethod
    async def handle_webhook(
        self,
        event_type: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle webhook event from external system

        Args:
            event_type: Type of webhook event
            payload: Webhook payload data

        Returns:
            dict: Processing results
        """
        pass

    @abstractmethod
    async def get_sync_status(self, sync_id: str) -> Dict[str, Any]:
        """
        Get status of a sync operation

        Args:
            sync_id: Unique sync operation ID

        Returns:
            dict: Sync status and progress information
        """
        pass

    # Common helper methods (implemented in base class)

    def log_operation(
        self,
        operation: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an integration operation

        Args:
            operation: Operation name
            status: Operation status
            details: Additional details
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "integration": self.integration_type,
            "operation": operation,
            "status": status,
            "details": details or {}
        }

        if status == "failed":
            self.logger.error(f"Operation failed: {log_entry}")
        else:
            self.logger.info(f"Operation logged: {log_entry}")

    async def validate_config(self) -> bool:
        """
        Validate integration configuration

        Returns:
            bool: True if configuration is valid
        """
        required_fields = self._get_required_config_fields()

        for field in required_fields:
            if field not in self.config or not self.config[field]:
                self.logger.error(f"Missing required config field: {field}")
                return False

        return True

    @abstractmethod
    def _get_required_config_fields(self) -> List[str]:
        """Return list of required configuration fields"""
        pass

    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get integration metrics

        Returns:
            dict: Metrics data (sync count, success rate, etc.)
        """
        return {
            "integration_type": self.integration_type,
            "status": "active",
            "metrics": {}
        }
