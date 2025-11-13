"""
TDS Webhook API Router
======================

RESTful API endpoints for receiving Zoho webhooks through TDS.
All Zoho webhook operations are centralized here per architecture.

Author: TSH ERP Team
Date: November 9, 2025
"""
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, Header, HTTPException, status, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.db.database import get_async_db
from app.core.config import settings
from app.services.zoho_processor import ProcessorService

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ZohoWebhookRequest(BaseModel):
    """Generic Zoho webhook request payload"""
    model_config = {"extra": "allow"}  # Allow extra fields from Zoho
    
    event_type: Optional[str] = None
    entity_id: Optional[str] = None  # Made optional - extract from nested data
    entity_type: Optional[str] = None
    organization_id: Optional[str] = None  # Made optional - extract from nested data
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    item: Optional[Dict[str, Any]] = None  # For Zoho Items
    invoice: Optional[Dict[str, Any]] = None  # For Zoho Invoices
    contact: Optional[Dict[str, Any]] = None  # For Zoho Contacts
    salesorder: Optional[Dict[str, Any]] = None  # For Zoho Sales Orders


class SimpleWebhook(BaseModel):
    """Simple webhook model for ProcessorService"""
    entity_type: str
    entity_id: str
    event_type: str = "update"
    data: Dict[str, Any] = Field(default_factory=dict)


class WebhookResponse(BaseModel):
    """Webhook processing response"""
    success: bool
    message: str
    event_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    queued: bool = False


# ============================================================================
# DEPENDENCY: WEBHOOK AUTHENTICATION
# ============================================================================

async def verify_webhook_key(x_webhook_key: Optional[str] = Header(None)) -> bool:
    """
    Verify webhook API key

    Args:
        x_webhook_key: Webhook key from header

    Returns:
        bool: True if authenticated

    Raises:
        HTTPException: If authentication fails
    """
    webhook_key = getattr(settings, 'webhook_api_key', None)

    # If no key is configured, allow all webhooks (development mode)
    if not webhook_key:
        logger.warning("No webhook API key configured - accepting all webhooks")
        return True

    # Verify the provided key matches
    if not x_webhook_key or x_webhook_key != webhook_key:
        logger.warning(f"Invalid webhook key attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing webhook API key"
        )

    return True


# ============================================================================
# HELPER FUNCTION
# ============================================================================

async def process_webhook_helper(
    webhook: SimpleWebhook,
    request: Request,
    db: AsyncSession,
    authenticated: bool
) -> WebhookResponse:
    """
    Helper function for processing webhooks

    Reduces code duplication across webhook endpoints
    """
    try:
        processor = ProcessorService(db)

        result = await processor.process_webhook(
            webhook=webhook,
            source_type="zoho",
            webhook_headers=dict(request.headers),
            ip_address=request.client.host if request.client else None,
            signature_verified=authenticated
        )

        return WebhookResponse(
            success=result["success"],
            message=f"{webhook.entity_type.title()} webhook processed and queued" if result["success"] else f"{webhook.entity_type.title()} webhook validation failed",
            event_id=result.get("inbox_event_id"),
            idempotency_key=result.get("idempotency_key"),
            queued=result.get("queued", False)
        )

    except ValueError as e:
        # Duplicate or validation error
        error_msg = str(e)
        if "Duplicate event" in error_msg:
            # Return success for duplicates to prevent Zoho from retrying
            logger.info(f"{webhook.entity_type} webhook duplicate - returning success: {e}")
            return WebhookResponse(
                success=True,
                message=f"Duplicate event already processed: {webhook.entity_type}",
                event_id=None,
                idempotency_key=f"zoho:{webhook.entity_type}:{webhook.entity_id}:{webhook.event_type}",
                queued=False
            )
        else:
            # Other validation errors
            logger.warning(f"{webhook.entity_type} webhook validation failed: {e}")
            return WebhookResponse(
                success=False,
                message=str(e),
                event_id=None,
                idempotency_key=f"zoho:{webhook.entity_type}:{webhook.entity_id}:{webhook.event_type}",
                queued=False
            )

    except Exception as e:
        logger.error(f"{webhook.entity_type} webhook processing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process webhook: {str(e)}"
        )


# ============================================================================
# WEBHOOK ENDPOINTS
# ============================================================================

@router.post(
    "/products",
    response_model=WebhookResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Receive product/item webhook from Zoho Books",
    description="Accepts product creation, update, or deletion events from Zoho Books"
)
async def receive_product_webhook(
    payload: ZohoWebhookRequest,
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    authenticated: bool = Depends(verify_webhook_key)
):
    """
    Receive product/item webhook from Zoho Books

    Zoho sends: {"item": {...}} or direct entity data
    """
    # Extract item data (Zoho sends in "item" field)
    item_data = payload.item or payload.data or {}
    item_id = (
        item_data.get('item_id') or
        item_data.get('item_account_id') or
        payload.entity_id or
        'unknown'
    )

    webhook = SimpleWebhook(
        event_type="update",
        entity_type="product",
        entity_id=str(item_id),
        data=item_data
    )

    logger.info(f"Product webhook received: {webhook.entity_id}")
    return await process_webhook_helper(webhook, request, db, authenticated)


@router.post(
    "/customers",
    response_model=WebhookResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Receive customer/contact webhook from Zoho Books"
)
async def receive_customer_webhook(
    payload: ZohoWebhookRequest,
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    authenticated: bool = Depends(verify_webhook_key)
):
    """Receive customer/contact webhook from Zoho Books"""
    contact_data = payload.contact or payload.data or {}
    contact_id = contact_data.get('contact_id') or payload.entity_id or 'unknown'

    webhook = SimpleWebhook(
        event_type="update",
        entity_type="customer",
        entity_id=str(contact_id),
        data=contact_data
    )

    logger.info(f"Customer webhook received: {webhook.entity_id}")
    return await process_webhook_helper(webhook, request, db, authenticated)


@router.post(
    "/invoices",
    response_model=WebhookResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Receive invoice webhook from Zoho Books"
)
async def receive_invoice_webhook(
    payload: ZohoWebhookRequest,
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    authenticated: bool = Depends(verify_webhook_key)
):
    """Receive invoice webhook from Zoho Books"""
    invoice_data = payload.invoice or payload.data or {}
    invoice_id = (
        invoice_data.get('invoice_id') or
        invoice_data.get('invoice_number') or
        payload.entity_id or
        'unknown'
    )

    webhook = SimpleWebhook(
        event_type="update",
        entity_type="invoice",
        entity_id=str(invoice_id),
        data=invoice_data
    )

    logger.info(f"Invoice webhook received: {webhook.entity_id}")
    return await process_webhook_helper(webhook, request, db, authenticated)


@router.post(
    "/orders",
    response_model=WebhookResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Receive sales order webhook from Zoho Books"
)
async def receive_order_webhook(
    payload: ZohoWebhookRequest,
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    authenticated: bool = Depends(verify_webhook_key)
):
    """Receive sales order webhook from Zoho Books"""
    order_data = payload.salesorder or payload.data or {}
    order_id = (
        order_data.get('salesorder_id') or
        order_data.get('salesorder_number') or
        payload.entity_id or
        'unknown'
    )

    webhook = SimpleWebhook(
        event_type="update",
        entity_type="order",
        entity_id=str(order_id),
        data=order_data
    )

    logger.info(f"Order webhook received: {webhook.entity_id}")
    return await process_webhook_helper(webhook, request, db, authenticated)


@router.post(
    "/stock",
    response_model=WebhookResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Receive stock adjustment webhook from Zoho Books"
)
async def receive_stock_webhook(
    payload: ZohoWebhookRequest,
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    authenticated: bool = Depends(verify_webhook_key)
):
    """Receive stock adjustment webhook from Zoho Inventory"""
    stock_data = payload.data or {}
    adjustment_id = payload.entity_id or 'unknown'

    webhook = SimpleWebhook(
        event_type="update",
        entity_type="stock",
        entity_id=str(adjustment_id),
        data=stock_data
    )

    logger.info(f"Stock webhook received: {webhook.entity_id}")
    return await process_webhook_helper(webhook, request, db, authenticated)


@router.post(
    "/prices",
    response_model=WebhookResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Receive price list webhook from Zoho Books"
)
async def receive_price_webhook(
    payload: ZohoWebhookRequest,
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    authenticated: bool = Depends(verify_webhook_key)
):
    """Receive price list webhook from Zoho Books"""
    price_data = payload.data or {}
    price_id = payload.entity_id or 'unknown'

    webhook = SimpleWebhook(
        event_type="update",
        entity_type="price",
        entity_id=str(price_id),
        data=price_data
    )

    logger.info(f"Price webhook received: {webhook.entity_id}")
    return await process_webhook_helper(webhook, request, db, authenticated)


# ============================================================================
# HEALTH & MONITORING ENDPOINTS
# ============================================================================

@router.get(
    "/health",
    summary="Get webhook system health status"
)
async def get_webhook_health(
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get webhook system health and statistics

    Returns health metrics and processing stats
    """
    try:
        from app.models.zoho_sync import TDSInboxEvent, TDSSyncQueue
        from sqlalchemy import select, func
        from datetime import timedelta

        # Get inbox stats from last 24 hours
        yesterday = datetime.utcnow() - timedelta(hours=24)

        inbox_count_result = await db.execute(
            select(func.count(TDSInboxEvent.id)).where(
                TDSInboxEvent.received_at >= yesterday
            )
        )
        inbox_count = inbox_count_result.scalar() or 0

        # Get queue stats
        queue_count_result = await db.execute(
            select(func.count(TDSSyncQueue.id))
        )
        queue_count = queue_count_result.scalar() or 0

        return {
            "status": "healthy",
            "webhooks_received_24h": inbox_count,
            "queue_size": queue_count,
            "system": "tds",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check error: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get(
    "/stats",
    summary="Get webhook processing statistics"
)
async def get_webhook_stats(
    db: AsyncSession = Depends(get_async_db)
):
    """Get detailed webhook processing statistics"""
    try:
        from app.models.zoho_sync import TDSInboxEvent, EventStatus
        from sqlalchemy import select, func
        from datetime import timedelta

        # Get stats from last 24 hours
        yesterday = datetime.utcnow() - timedelta(hours=24)

        # Total received
        total_result = await db.execute(
            select(func.count(TDSInboxEvent.id)).where(
                TDSInboxEvent.received_at >= yesterday
            )
        )
        total_received = total_result.scalar() or 0

        # Processed count
        processed_result = await db.execute(
            select(func.count(TDSInboxEvent.id)).where(
                TDSInboxEvent.received_at >= yesterday,
                TDSInboxEvent.status == EventStatus.PROCESSED
            )
        )
        processed = processed_result.scalar() or 0

        # Failed count
        failed_result = await db.execute(
            select(func.count(TDSInboxEvent.id)).where(
                TDSInboxEvent.received_at >= yesterday,
                TDSInboxEvent.status == EventStatus.FAILED
            )
        )
        failed = failed_result.scalar() or 0

        # Calculate success rate
        success_rate = (processed / total_received * 100) if total_received > 0 else 0

        return {
            "period": "last_24_hours",
            "total_received": total_received,
            "total_processed": processed,
            "total_failed": failed,
            "success_rate": round(success_rate, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Stats error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get webhook stats: {str(e)}"
        )
