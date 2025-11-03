"""
Zoho Webhooks Router
Webhook endpoints for receiving data from Zoho Books
(Unified from TDS Core - now part of main ERP)
"""
import logging
from typing import Dict, Any

from fastapi import APIRouter, Request, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.config import settings

# Import schemas from TDS Core (will be moved to app/schemas in Phase 3)
from tds_core.schemas.webhook_schemas import (
    WebhookEvent,
    ProductWebhook,
    ZohoItemWebhook,
    CustomerWebhook,
    InvoiceWebhook,
    BillWebhook,
    CreditNoteWebhook,
    StockWebhook,
    PriceListWebhook,
)
from tds_core.schemas.response_schemas import WebhookResponse

# Import services from TDS Core (will be moved to app/services in Phase 3)
from tds_core.services.processor_service import ProcessorService

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# DEPENDENCY: WEBHOOK AUTHENTICATION
# ============================================================================

async def verify_webhook_key(x_webhook_key: str = Header(None)):
    """Verify webhook API key"""
    if not settings.webhook_api_key:
        # No authentication required if not configured
        return True

    if not x_webhook_key or x_webhook_key != settings.webhook_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing webhook API key"
        )
    return True


# ============================================================================
# HELPER FUNCTION
# ============================================================================

async def process_webhook_helper(
    webhook: WebhookEvent,
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
    tags=["Zoho Webhooks"],
    status_code=status.HTTP_202_ACCEPTED
)
async def receive_product_webhook(
    zoho_webhook: ZohoItemWebhook,
    request: Request,
    db: AsyncSession = Depends(get_db),
    authenticated: bool = Depends(verify_webhook_key)
):
    """
    Receive product/item webhook from Zoho Books

    Accepts product creation, update, or deletion events
    Zoho sends: {"item": {...}}
    """
    # Transform Zoho format to internal format
    item_data = zoho_webhook.item
    item_id = item_data.get('item_id') or item_data.get('item_account_id') or 'unknown'

    webhook = ProductWebhook(
        event_type="update",  # Zoho doesn't specify, assume update
        entity_type="product",
        entity_id=str(item_id),
        data=item_data
    )

    logger.info(f"Product webhook received: {webhook.entity_id}")
    return await process_webhook_helper(webhook, request, db, authenticated)


@router.post(
    "/customers",
    response_model=WebhookResponse,
    tags=["Zoho Webhooks"],
    status_code=status.HTTP_202_ACCEPTED
)
async def receive_customer_webhook(
    webhook: CustomerWebhook,
    request: Request,
    db: AsyncSession = Depends(get_db),
    authenticated: bool = Depends(verify_webhook_key)
):
    """
    Receive customer/contact webhook from Zoho Books

    Accepts customer creation, update, or deletion events
    """
    logger.info(f"Customer webhook received: {webhook.entity_id}")
    return await process_webhook_helper(webhook, request, db, authenticated)


@router.post(
    "/invoices",
    response_model=WebhookResponse,
    tags=["Zoho Webhooks"],
    status_code=status.HTTP_202_ACCEPTED
)
async def receive_invoice_webhook(
    webhook: InvoiceWebhook,
    request: Request,
    db: AsyncSession = Depends(get_db),
    authenticated: bool = Depends(verify_webhook_key)
):
    """
    Receive invoice webhook from Zoho Books

    Accepts invoice creation, update, or deletion events
    """
    logger.info(f"Invoice webhook received: {webhook.entity_id}")
    return await process_webhook_helper(webhook, request, db, authenticated)


@router.post(
    "/bills",
    response_model=WebhookResponse,
    tags=["Zoho Webhooks"],
    status_code=status.HTTP_202_ACCEPTED
)
async def receive_bill_webhook(
    webhook: BillWebhook,
    request: Request,
    db: AsyncSession = Depends(get_db),
    authenticated: bool = Depends(verify_webhook_key)
):
    """
    Receive bill webhook from Zoho Books

    Accepts bill creation, update, or deletion events
    """
    logger.info(f"Bill webhook received: {webhook.entity_id}")
    return await process_webhook_helper(webhook, request, db, authenticated)


@router.post(
    "/credit-notes",
    response_model=WebhookResponse,
    tags=["Zoho Webhooks"],
    status_code=status.HTTP_202_ACCEPTED
)
async def receive_credit_note_webhook(
    webhook: CreditNoteWebhook,
    request: Request,
    db: AsyncSession = Depends(get_db),
    authenticated: bool = Depends(verify_webhook_key)
):
    """
    Receive credit note webhook from Zoho Books

    Accepts credit note creation, update, or deletion events
    """
    logger.info(f"Credit note webhook received: {webhook.entity_id}")
    return await process_webhook_helper(webhook, request, db, authenticated)


@router.post(
    "/stock",
    response_model=WebhookResponse,
    tags=["Zoho Webhooks"],
    status_code=status.HTTP_202_ACCEPTED
)
async def receive_stock_webhook(
    webhook: StockWebhook,
    request: Request,
    db: AsyncSession = Depends(get_db),
    authenticated: bool = Depends(verify_webhook_key)
):
    """
    Receive stock adjustment webhook from Zoho Books

    Accepts stock adjustment events
    """
    logger.info(f"Stock adjustment webhook received: {webhook.entity_id}")
    return await process_webhook_helper(webhook, request, db, authenticated)


@router.post(
    "/prices",
    response_model=WebhookResponse,
    tags=["Zoho Webhooks"],
    status_code=status.HTTP_202_ACCEPTED
)
async def receive_pricelist_webhook(
    webhook: PriceListWebhook,
    request: Request,
    db: AsyncSession = Depends(get_db),
    authenticated: bool = Depends(verify_webhook_key)
):
    """
    Receive price list webhook from Zoho Books

    Accepts price list creation, update, or deletion events
    """
    logger.info(f"Price list webhook received: {webhook.entity_id}")
    return await process_webhook_helper(webhook, request, db, authenticated)
