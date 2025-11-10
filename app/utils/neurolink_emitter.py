"""
NeuroLink Event Emitter Utility
Allows TSH ERP modules to emit events to NeuroLink notification system
"""

import logging
import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)


class NeuroLinkEmitter:
    """
    Utility class for emitting events to NeuroLink

    Usage:
        emitter = NeuroLinkEmitter()
        await emitter.emit_price_list_update(
            price_list_name="Consumer Price List",
            products_updated=150,
            sync_duration=45.2
        )
    """

    def __init__(self):
        self.neurolink_url = getattr(settings, 'NEUROLINK_API_URL', 'http://localhost:8002')
        self.timeout = 10.0
        self.enabled = getattr(settings, 'NEUROLINK_ENABLED', True)

    async def emit_event(
        self,
        source_module: str,
        event_type: str,
        payload: Dict[str, Any],
        severity: str = "info",
        correlation_id: Optional[str] = None,
        branch_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> bool:
        """
        Emit an event to NeuroLink

        Args:
            source_module: Source module (e.g., 'tds', 'inventory', 'sales')
            event_type: Event type (e.g., 'price_list.updated', 'stock.low')
            payload: Event data
            severity: Severity level (info, warning, error, critical)
            correlation_id: Correlation ID for related events
            branch_id: Branch ID if applicable
            user_id: User ID who triggered the event

        Returns:
            bool: True if event was emitted successfully
        """
        if not self.enabled:
            logger.debug(f"NeuroLink disabled, skipping event: {event_type}")
            return False

        try:
            # Generate idempotency key to prevent duplicates
            idempotency_key = f"{source_module}_{event_type}_{datetime.utcnow().date()}"
            if payload.get('id'):
                idempotency_key += f"_{payload['id']}"

            event_data = {
                "source_module": source_module,
                "event_type": event_type,
                "severity": severity,
                "occurred_at": datetime.utcnow().isoformat(),
                "payload": payload,
                "producer_idempotency_key": idempotency_key,
                "correlation_id": correlation_id,
                "branch_id": branch_id,
                "user_id": user_id
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.neurolink_url}/v1/events",
                    json=event_data
                )

                if response.status_code in [200, 201]:
                    logger.info(
                        f"✅ Event emitted to NeuroLink: {source_module}.{event_type}"
                    )
                    return True
                elif response.status_code == 409:
                    # Duplicate event (idempotency)
                    logger.debug(
                        f"Duplicate event (idempotency): {source_module}.{event_type}"
                    )
                    return True
                else:
                    logger.warning(
                        f"Failed to emit event to NeuroLink: {response.status_code} - {response.text}"
                    )
                    return False

        except httpx.TimeoutException:
            logger.warning(f"NeuroLink timeout for event: {event_type}")
            return False
        except Exception as e:
            logger.error(f"Error emitting event to NeuroLink: {str(e)}", exc_info=True)
            return False

    # ========================================================================
    # TDS-Specific Event Emitters
    # ========================================================================

    async def emit_price_list_updated(
        self,
        price_list_name: str,
        products_updated: int,
        sync_duration: float,
        source: str = "zoho",
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Emit price list update event

        Args:
            price_list_name: Name of the price list (e.g., "Consumer Price List")
            products_updated: Number of products with price updates
            sync_duration: Sync duration in seconds
            source: Source of the update (default: "zoho")
            details: Additional details

        Returns:
            bool: Success status
        """
        payload = {
            "price_list_name": price_list_name,
            "products_updated": products_updated,
            "sync_duration_seconds": sync_duration,
            "source": source,
            "synced_at": datetime.utcnow().isoformat()
        }

        if details:
            payload.update(details)

        return await self.emit_event(
            source_module="tds",
            event_type="price_list.updated",
            payload=payload,
            severity="info"
        )

    async def emit_sync_completed(
        self,
        entity_type: str,
        total_processed: int,
        successful: int,
        failed: int,
        duration: float
    ) -> bool:
        """
        Emit sync completion event

        Args:
            entity_type: Type of entity synced (e.g., "products", "orders")
            total_processed: Total items processed
            successful: Successful items
            failed: Failed items
            duration: Sync duration in seconds

        Returns:
            bool: Success status
        """
        success_rate = (successful / total_processed * 100) if total_processed > 0 else 0

        # Determine severity based on success rate
        if success_rate >= 95:
            severity = "info"
        elif success_rate >= 80:
            severity = "warning"
        else:
            severity = "error"

        payload = {
            "entity_type": entity_type,
            "total_processed": total_processed,
            "successful": successful,
            "failed": failed,
            "success_rate": round(success_rate, 2),
            "duration_seconds": duration,
            "synced_at": datetime.utcnow().isoformat()
        }

        return await self.emit_event(
            source_module="tds",
            event_type="sync.completed",
            payload=payload,
            severity=severity
        )

    async def emit_sync_failed(
        self,
        entity_type: str,
        error_message: str,
        error_code: Optional[str] = None
    ) -> bool:
        """
        Emit sync failure event

        Args:
            entity_type: Type of entity that failed to sync
            error_message: Error message
            error_code: Error code if available

        Returns:
            bool: Success status
        """
        payload = {
            "entity_type": entity_type,
            "error_message": error_message,
            "error_code": error_code,
            "failed_at": datetime.utcnow().isoformat()
        }

        return await self.emit_event(
            source_module="tds",
            event_type="sync.failed",
            payload=payload,
            severity="error"
        )

    async def emit_stock_discrepancy(
        self,
        product_name: str,
        product_sku: str,
        zoho_stock: int,
        local_stock: int,
        discrepancy: int
    ) -> bool:
        """
        Emit stock discrepancy event

        Args:
            product_name: Product name
            product_sku: Product SKU
            zoho_stock: Stock in Zoho
            local_stock: Stock in local database
            discrepancy: Difference (zoho - local)

        Returns:
            bool: Success status
        """
        payload = {
            "product_name": product_name,
            "product_sku": product_sku,
            "zoho_stock": zoho_stock,
            "local_stock": local_stock,
            "discrepancy": discrepancy,
            "detected_at": datetime.utcnow().isoformat()
        }

        # Determine severity based on discrepancy
        severity = "critical" if abs(discrepancy) > 100 else "warning"

        return await self.emit_event(
            source_module="tds",
            event_type="stock.discrepancy",
            payload=payload,
            severity=severity
        )

    async def emit_image_sync_completed(
        self,
        products_processed: int,
        images_downloaded: int,
        images_failed: int,
        duration: float
    ) -> bool:
        """
        Emit image sync completion event

        Args:
            products_processed: Number of products processed
            images_downloaded: Successfully downloaded images
            images_failed: Failed downloads
            duration: Sync duration in seconds

        Returns:
            bool: Success status
        """
        payload = {
            "products_processed": products_processed,
            "images_downloaded": images_downloaded,
            "images_failed": images_failed,
            "success_rate": round((images_downloaded / (images_downloaded + images_failed) * 100), 2) if (images_downloaded + images_failed) > 0 else 0,
            "duration_seconds": duration,
            "synced_at": datetime.utcnow().isoformat()
        }

        return await self.emit_event(
            source_module="tds",
            event_type="image_sync.completed",
            payload=payload,
            severity="info"
        )


# Global instance
neurolink_emitter = NeuroLinkEmitter()
