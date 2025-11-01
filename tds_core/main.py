"""
TDS Core - Main FastAPI Application
Webhook receiver and API endpoints for TSH DataSync Core
"""
import time
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, Request, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import init_db, close_db, check_db_health, get_db
from schemas.webhook_schemas import (
    WebhookEvent,
    ProductWebhook,
    ZohoItemWebhook,
    CustomerWebhook,
    InvoiceWebhook,
    BillWebhook,
    CreditNoteWebhook,
    StockWebhook,
    PriceListWebhook,
    BatchWebhookRequest,
    ManualSyncRequest,
)
from schemas.response_schemas import (
    WebhookResponse,
    HealthResponse,
    ErrorResponse,
    QueueStatsResponse,
)
from services.processor_service import ProcessorService
from services.queue_service import QueueService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# APPLICATION LIFESPAN
# ============================================================================

app_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"🚀 Starting TDS Core API v{settings.app_version}")
    logger.info(f"📊 Environment: {settings.environment}")
    logger.info(f"🔧 Debug Mode: {settings.debug}")

    try:
        # Initialize database
        await init_db()
        logger.info("✅ Database initialized")

    except Exception as e:
        logger.error(f"❌ Failed to initialize application: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down TDS Core API")
    try:
        await close_db()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="TDS Core API",
    description="TSH DataSync Core - Resilient data synchronization system",
    version=settings.app_version,
    docs_url=settings.docs_url if settings.docs_enabled else None,
    redoc_url=settings.redoc_url if settings.docs_enabled else None,
    lifespan=lifespan,
)


# ============================================================================
# MIDDLEWARE
# ============================================================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = time.time()

    # Log request
    logger.info(f"→ {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Log response
    duration_ms = (time.time() - start_time) * 1000
    logger.info(
        f"← {request.method} {request.url.path} "
        f"[{response.status_code}] {duration_ms:.2f}ms"
    )

    return response


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "ValidationError",
            "message": "Invalid request data",
            "details": exc.errors()
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": "HTTPException",
            "message": exc.detail
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "InternalServerError",
            "message": "An unexpected error occurred"
        }
    )


# ============================================================================
# AUTHENTICATION
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
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@app.get("/", tags=["Status"])
async def root():
    """API root endpoint"""
    return {
        "service": "TDS Core API",
        "version": settings.app_version,
        "status": "running",
        "environment": settings.environment,
        "docs_url": settings.docs_url if settings.docs_enabled else None
    }


@app.get("/health", response_model=HealthResponse, tags=["Status"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    System health check endpoint

    Returns database status, queue stats, and uptime
    """
    try:
        # Check database health
        db_health = await check_db_health()

        # Calculate uptime
        uptime_seconds = int(time.time() - app_start_time)

        # Get real queue statistics
        queue_service = QueueService(db)
        queue_stats_data = await queue_service.get_queue_stats()

        queue_stats = {
            "pending": queue_stats_data["by_status"].get("pending", 0),
            "processing": queue_stats_data["by_status"].get("processing", 0),
            "failed": queue_stats_data["by_status"].get("failed", 0) +
                     queue_stats_data["by_status"].get("dead_letter", 0)
        }

        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            database=db_health,
            queue=queue_stats,
            uptime_seconds=uptime_seconds
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )


@app.get("/ping", tags=["Status"])
async def ping():
    """Simple ping endpoint for load balancers"""
    return {"status": "ok", "timestamp": time.time()}


# ============================================================================
# WEBHOOK ENDPOINTS
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

@app.post(
    "/webhooks/products",
    response_model=WebhookResponse,
    tags=["Webhooks"],
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


@app.post(
    "/webhooks/customers",
    response_model=WebhookResponse,
    tags=["Webhooks"],
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


@app.post(
    "/webhooks/invoices",
    response_model=WebhookResponse,
    tags=["Webhooks"],
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


@app.post(
    "/webhooks/bills",
    response_model=WebhookResponse,
    tags=["Webhooks"],
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


@app.post(
    "/webhooks/credit-notes",
    response_model=WebhookResponse,
    tags=["Webhooks"],
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


@app.post(
    "/webhooks/stock",
    response_model=WebhookResponse,
    tags=["Webhooks"],
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


@app.post(
    "/webhooks/prices",
    response_model=WebhookResponse,
    tags=["Webhooks"],
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


# ============================================================================
# MANUAL SYNC ENDPOINT
# ============================================================================

@app.post("/sync/manual", tags=["Sync"])
async def trigger_manual_sync(
    request: ManualSyncRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger manual synchronization

    Allows administrators to manually trigger sync for specific entities
    """
    logger.info(f"Manual sync requested: {request.entity_type}")

    # TODO: Implement manual sync logic

    return {
        "success": True,
        "message": f"Manual sync triggered for {request.entity_type}",
        "entity_type": request.entity_type,
        "entity_count": len(request.entity_ids) if request.entity_ids else "all",
        "priority": request.priority
    }


# ============================================================================
# QUEUE MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/queue/stats", response_model=QueueStatsResponse, tags=["Queue"])
async def get_queue_stats(db: AsyncSession = Depends(get_db)):
    """
    Get queue statistics

    Returns current queue status and processing metrics
    """
    from datetime import datetime

    queue_service = QueueService(db)
    stats = await queue_service.get_queue_stats()

    # Parse oldest_pending
    oldest_pending = None
    if stats.get("oldest_pending"):
        try:
            oldest_pending = datetime.fromisoformat(stats["oldest_pending"])
        except:
            pass

    return QueueStatsResponse(
        total_events=stats["total_events"],
        by_status=stats["by_status"],
        by_entity=stats["by_entity_type"],
        by_priority=stats["by_priority"],
        oldest_pending=oldest_pending,
        processing_rate=None  # TODO: Calculate from metrics
    )


# ============================================================================
# WEBHOOK HEALTH MONITORING ENDPOINTS
# ============================================================================

@app.get("/webhooks/health", tags=["Webhooks", "Monitoring"])
async def get_webhook_health(
    hours: int = 24,
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive webhook health metrics

    Returns:
        - Health score (0-100)
        - Webhook statistics
        - Detected issues
        - Recommendations

    Use this endpoint to proactively monitor webhook health
    """
    from services.webhook_health_service import WebhookHealthService

    health_service = WebhookHealthService(db)
    metrics = await health_service.get_health_metrics(hours=hours)

    return {
        "success": True,
        "metrics": metrics
    }


@app.get("/webhooks/duplicates", tags=["Webhooks", "Monitoring"])
async def get_duplicate_webhook_analysis(
    hours: int = 24,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze duplicate webhook attempts

    Helps identify if Zoho or other sources are retrying webhooks excessively

    Returns:
        - List of events with multiple delivery attempts
        - Retry counts and time spans
        - Patterns in duplicate deliveries
    """
    from services.webhook_health_service import WebhookHealthService

    health_service = WebhookHealthService(db)
    stats = await health_service.get_duplicate_webhook_stats(hours=hours)

    return {
        "success": True,
        "analysis": stats
    }


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.get("/admin/config", tags=["Admin"])
async def get_configuration(db: AsyncSession = Depends(get_db)):
    """
    Get current system configuration

    Returns non-sensitive configuration values
    """
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "api_workers": settings.api_workers,
        "database": {
            "host": settings.database_host,
            "name": settings.database_name,
            "pool_size": settings.database_pool_size
        },
        "tds_config": {
            "max_retry_attempts": settings.tds_max_retry_attempts,
            "batch_size": settings.tds_batch_size,
            "alert_failure_threshold": settings.tds_alert_failure_rate_threshold
        }
    }


# ============================================================================
# STARTUP MESSAGE
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting TDS Core API on {settings.api_host}:{settings.api_port}")

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )


# ============================================================================
# DASHBOARD & MONITORING ENDPOINTS
# ============================================================================

@app.get(
    "/dashboard/metrics",
    tags=["Dashboard"],
    summary="Get system metrics"
)
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive system metrics for dashboard

    Returns:
        - Queue statistics
        - Processing performance
        - Database metrics
        - Recent alerts
    """
    from services.monitoring_service import MonitoringService
    from services.alert_service import AlertService

    try:
        monitoring = MonitoringService()
        metrics = await monitoring.get_system_metrics(db)

        # Get recent alerts
        alert_service = AlertService(db)
        active_alerts = await alert_service.get_active_alerts(acknowledged=False)

        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics,
            "active_alerts": [
                {
                    "id": str(alert.id),
                    "severity": alert.severity,
                    "title": alert.title,
                    "message": alert.message,
                    "created_at": alert.created_at.isoformat()
                }
                for alert in active_alerts[:10]
            ]
        }
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/dashboard/queue-stats",
    tags=["Dashboard"],
    summary="Get queue statistics"
)
async def get_queue_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get detailed queue statistics"""
    from services.queue_service import QueueService

    try:
        queue_service = QueueService(db)
        stats = await queue_service.get_queue_stats()

        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting queue stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/dashboard/recent-events",
    tags=["Dashboard"],
    summary="Get recent sync events"
)
async def get_recent_events(
    limit: int = 50,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get recent sync queue events"""
    from models.tds_models import TDSSyncQueue, EventStatus

    try:
        query = select(TDSSyncQueue).order_by(TDSSyncQueue.queued_at.desc()).limit(limit)

        if status_filter:
            try:
                status_enum = EventStatus(status_filter.upper())
                query = query.where(TDSSyncQueue.status == status_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status_filter}")

        result = await db.execute(query)
        events = result.scalars().all()

        return {
            "success": True,
            "count": len(events),
            "events": [
                {
                    "id": str(event.id),
                    "entity_type": event.entity_type,
                    "source_entity_id": event.source_entity_id,
                    "operation": event.operation_type,
                    "status": event.status,
                    "attempt_count": event.attempt_count,
                    "queued_at": event.queued_at.isoformat() if event.queued_at else None,
                    "completed_at": event.completed_at.isoformat() if event.completed_at else None,
                    "last_error": event.last_error
                }
                for event in events
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recent events: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/dashboard/dead-letter",
    tags=["Dashboard"],
    summary="Get dead letter queue"
)
async def get_dead_letter_queue(
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get events in dead letter queue"""
    from models.tds_models import TDSDeadLetterQueue

    try:
        result = await db.execute(
            select(TDSDeadLetterQueue)
            .order_by(TDSDeadLetterQueue.moved_at.desc())
            .limit(limit)
        )
        dlq_events = result.scalars().all()

        return {
            "success": True,
            "count": len(dlq_events),
            "events": [
                {
                    "id": str(event.id),
                    "entity_type": event.entity_type,
                    "source_entity_id": event.source_entity_id,
                    "failure_reason": event.failure_reason,
                    "error_code": event.error_code,
                    "attempt_count": event.attempt_count,
                    "moved_at": event.moved_at.isoformat() if event.moved_at else None,
                    "payload": event.payload
                }
                for event in dlq_events
            ]
        }
    except Exception as e:
        logger.error(f"Error getting dead letter queue: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/dashboard/alerts/{alert_id}/acknowledge",
    tags=["Dashboard"],
    summary="Acknowledge an alert"
)
async def acknowledge_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Mark an alert as acknowledged"""
    from services.alert_service import AlertService
    from uuid import UUID

    try:
        alert_service = AlertService(db)
        success = await alert_service.acknowledge_alert(UUID(alert_id))

        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")

        return {
            "success": True,
            "message": "Alert acknowledged"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/dashboard/dead-letter/{event_id}/retry",
    tags=["Dashboard"],
    summary="Retry a dead letter event"
)
async def retry_dead_letter_event(
    event_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Move an event from dead letter queue back to processing queue

    This allows manual retry of permanently failed events
    """
    from models.tds_models import TDSDeadLetterQueue, TDSSyncQueue, EventStatus
    from uuid import UUID

    try:
        # Get dead letter event
        result = await db.execute(
            select(TDSDeadLetterQueue).where(TDSDeadLetterQueue.id == UUID(event_id))
        )
        dlq_event = result.scalar_one_or_none()

        if not dlq_event:
            raise HTTPException(status_code=404, detail="Dead letter event not found")

        # Create new queue entry
        new_queue_entry = TDSSyncQueue(
            entity_type=dlq_event.entity_type,
            source_entity_id=dlq_event.source_entity_id,
            operation_type=dlq_event.operation_type,
            normalized_payload=dlq_event.payload,
            status=EventStatus.PENDING,
            priority=2,  # High priority for manual retries
            attempt_count=0,
            max_attempts=3
        )

        db.add(new_queue_entry)

        # Remove from dead letter queue
        await db.delete(dlq_event)

        await db.commit()

        return {
            "success": True,
            "message": "Event moved back to processing queue",
            "new_queue_id": str(new_queue_entry.id)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrying dead letter event: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
