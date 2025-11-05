"""
TDS Core - Webhook Request Schemas
Pydantic models for validating incoming webhook payloads
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime


# ============================================================================
# BASE WEBHOOK SCHEMA
# ============================================================================

class WebhookEvent(BaseModel):
    """Base webhook event structure from Zoho"""

    # Event Metadata
    event_id: Optional[str] = Field(None, description="Unique event identifier from Zoho")
    event_type: str = Field(..., description="Event type (create, update, delete)")
    event_time: Optional[datetime] = Field(None, description="Event timestamp from Zoho")

    # Entity Information
    entity_type: str = Field(..., description="Type of entity (item, contact, invoice, etc.)")
    entity_id: str = Field(..., description="Zoho entity ID")

    # Payload
    data: Dict[str, Any] = Field(..., description="Entity data payload")

    # Additional Context
    organization_id: Optional[str] = Field(None, description="Zoho organization ID")
    user_id: Optional[str] = Field(None, description="User who triggered the event")

    @field_validator('event_type')
    @classmethod
    def validate_event_type(cls, v):
        """Validate event type"""
        allowed = ['create', 'update', 'delete', 'upsert']
        if v.lower() not in allowed:
            raise ValueError(f"event_type must be one of {allowed}")
        return v.lower()

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "evt_12345",
                "event_type": "update",
                "event_time": "2025-10-31T10:30:00Z",
                "entity_type": "item",
                "entity_id": "123456789",
                "data": {
                    "item_id": "123456789",
                    "name": "Product Name",
                    "sku": "SKU-001"
                }
            }
        }


# ============================================================================
# ENTITY-SPECIFIC WEBHOOKS
# ============================================================================

class ZohoItemWebhook(BaseModel):
    """
    Raw Zoho Books Item webhook format
    Zoho sends: {"item": {...}}
    """
    item: Dict[str, Any] = Field(..., description="Item data from Zoho")

    class Config:
        extra = "allow"  # Allow additional fields Zoho might send


class ProductWebhook(WebhookEvent):
    """Product/Item webhook from Zoho Books"""

    entity_type: str = Field(default="product", description="Fixed to 'product'")

    @field_validator('data')
    @classmethod
    def validate_product_data(cls, v):
        """Validate product data - flexible for various Zoho formats"""
        # Don't enforce strict validation - Zoho format varies
        # Just ensure we have some data
        if not v or not isinstance(v, dict):
            raise ValueError("Product data must be a non-empty dictionary")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "update",
                "entity_type": "product",
                "entity_id": "123456789",
                "data": {
                    "item_id": "123456789",
                    "name": "Laptop Computer",
                    "sku": "LAP-001",
                    "description": "15 inch laptop",
                    "rate": 1500.00,
                    "purchase_rate": 1200.00,
                    "stock_on_hand": 50,
                    "is_active": True
                }
            }
        }


class CustomerWebhook(WebhookEvent):
    """Customer/Contact webhook from Zoho Books"""

    entity_type: str = Field(default="customer", description="Fixed to 'customer'")

    @field_validator('data')
    @classmethod
    def validate_customer_data(cls, v):
        """Validate required customer fields"""
        required_fields = ['contact_id', 'contact_name']
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Customer data missing required field: {field}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "create",
                "entity_type": "customer",
                "entity_id": "987654321",
                "data": {
                    "contact_id": "987654321",
                    "contact_name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+1234567890",
                    "billing_address": {
                        "street": "123 Main St",
                        "city": "New York",
                        "country": "USA"
                    }
                }
            }
        }


class InvoiceWebhook(WebhookEvent):
    """Invoice webhook from Zoho Books"""

    entity_type: str = Field(default="invoice", description="Fixed to 'invoice'")

    @field_validator('data')
    @classmethod
    def validate_invoice_data(cls, v):
        """Validate required invoice fields"""
        required_fields = ['invoice_id', 'invoice_number', 'customer_id']
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Invoice data missing required field: {field}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "create",
                "entity_type": "invoice",
                "entity_id": "INV-001",
                "data": {
                    "invoice_id": "111222333",
                    "invoice_number": "INV-001",
                    "customer_id": "987654321",
                    "date": "2025-10-31",
                    "due_date": "2025-11-15",
                    "total": 1500.00,
                    "status": "sent",
                    "line_items": []
                }
            }
        }


class BillWebhook(WebhookEvent):
    """Bill webhook from Zoho Books"""

    entity_type: str = Field(default="bill", description="Fixed to 'bill'")

    @field_validator('data')
    @classmethod
    def validate_bill_data(cls, v):
        """Validate required bill fields"""
        required_fields = ['bill_id', 'bill_number', 'vendor_id']
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Bill data missing required field: {field}")
        return v


class CreditNoteWebhook(WebhookEvent):
    """Credit Note webhook from Zoho Books"""

    entity_type: str = Field(default="credit_note", description="Fixed to 'credit_note'")

    @field_validator('data')
    @classmethod
    def validate_credit_note_data(cls, v):
        """Validate required credit note fields"""
        required_fields = ['creditnote_id', 'creditnote_number']
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Credit note data missing required field: {field}")
        return v


class StockWebhook(WebhookEvent):
    """Stock Adjustment webhook from Zoho Books"""

    entity_type: str = Field(default="stock_adjustment", description="Fixed to 'stock_adjustment'")

    @field_validator('data')
    @classmethod
    def validate_stock_data(cls, v):
        """Validate required stock adjustment fields"""
        required_fields = ['adjustment_id', 'item_id']
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Stock adjustment data missing required field: {field}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "create",
                "entity_type": "stock_adjustment",
                "entity_id": "ADJ-001",
                "data": {
                    "adjustment_id": "444555666",
                    "item_id": "123456789",
                    "quantity_adjusted": 10,
                    "adjustment_type": "quantity",
                    "reason": "Stock count correction",
                    "date": "2025-10-31"
                }
            }
        }


class PriceListWebhook(WebhookEvent):
    """Price List webhook from Zoho Books"""

    entity_type: str = Field(default="price_list", description="Fixed to 'price_list'")

    @field_validator('data')
    @classmethod
    def validate_pricelist_data(cls, v):
        """Validate required price list fields"""
        required_fields = ['pricelist_id', 'name']
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Price list data missing required field: {field}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "update",
                "entity_type": "price_list",
                "entity_id": "PL-001",
                "data": {
                    "pricelist_id": "777888999",
                    "name": "Retail Prices",
                    "currency_code": "USD",
                    "is_active": True,
                    "items": [
                        {
                            "item_id": "123456789",
                            "rate": 1500.00,
                            "discount_percentage": 10
                        }
                    ]
                }
            }
        }


# ============================================================================
# BATCH WEBHOOK PROCESSING
# ============================================================================

class BatchWebhookRequest(BaseModel):
    """Batch webhook request for multiple events"""

    events: List[WebhookEvent] = Field(..., description="List of webhook events")
    batch_id: Optional[str] = Field(None, description="Batch identifier")

    @field_validator('events')
    @classmethod
    def validate_events_not_empty(cls, v):
        """Ensure at least one event in batch"""
        if not v or len(v) == 0:
            raise ValueError("Batch must contain at least one event")
        if len(v) > 100:
            raise ValueError("Batch cannot contain more than 100 events")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "batch_id": "batch_12345",
                "events": [
                    {
                        "event_type": "update",
                        "entity_type": "product",
                        "entity_id": "123",
                        "data": {"item_id": "123", "name": "Product 1"}
                    },
                    {
                        "event_type": "create",
                        "entity_type": "customer",
                        "entity_id": "456",
                        "data": {"contact_id": "456", "contact_name": "Customer 1"}
                    }
                ]
            }
        }


# ============================================================================
# MANUAL TRIGGER SCHEMA
# ============================================================================

class ManualSyncRequest(BaseModel):
    """Manual sync trigger request"""

    entity_type: str = Field(..., description="Entity type to sync")
    entity_ids: Optional[List[str]] = Field(None, description="Specific entity IDs (optional, syncs all if omitted)")
    force: bool = Field(default=False, description="Force re-sync even if up-to-date")
    priority: int = Field(default=5, ge=1, le=10, description="Priority (1=highest, 10=lowest)")

    @field_validator('entity_type')
    @classmethod
    def validate_entity_type(cls, v):
        """Validate entity type"""
        allowed = [
            'product', 'customer', 'invoice', 'bill',
            'credit_note', 'stock_adjustment', 'price_list'
        ]
        if v.lower() not in allowed:
            raise ValueError(f"entity_type must be one of {allowed}")
        return v.lower()

    class Config:
        json_schema_extra = {
            "example": {
                "entity_type": "product",
                "entity_ids": ["123", "456", "789"],
                "force": False,
                "priority": 5
            }
        }
