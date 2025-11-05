"""
TDS Core - Pydantic Schemas
Request and response validation models
"""
from schemas.webhook_schemas import (
    WebhookEvent,
    ProductWebhook,
    CustomerWebhook,
    InvoiceWebhook,
    BillWebhook,
    CreditNoteWebhook,
    StockWebhook,
    PriceListWebhook,
)
from schemas.response_schemas import (
    WebhookResponse,
    HealthResponse,
    QueueStatsResponse,
    SyncRunResponse,
)

__all__ = [
    # Webhook Requests
    "WebhookEvent",
    "ProductWebhook",
    "CustomerWebhook",
    "InvoiceWebhook",
    "BillWebhook",
    "CreditNoteWebhook",
    "StockWebhook",
    "PriceListWebhook",
    # Responses
    "WebhookResponse",
    "HealthResponse",
    "QueueStatsResponse",
    "SyncRunResponse",
]
