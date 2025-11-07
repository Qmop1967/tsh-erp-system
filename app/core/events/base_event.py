"""
Base Event Classes
Foundation for all domain events in the system
"""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4, UUID
from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    """
    Base class for all domain events

    Every event in the system inherits from this class.
    Events represent something that has happened in the system.
    """
    event_id: UUID = Field(default_factory=uuid4, description="Unique event identifier")
    event_type: str = Field(..., description="Type of event (e.g., 'sales.order.created')")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the event occurred")
    module: str = Field(..., description="Source module that published this event")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event payload")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    correlation_id: Optional[UUID] = Field(None, description="ID to correlate related events")
    causation_id: Optional[UUID] = Field(None, description="ID of the event that caused this one")
    user_id: Optional[int] = Field(None, description="User who triggered this event")
    version: int = Field(default=1, description="Event schema version")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return self.dict()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(event_type='{self.event_type}', event_id='{self.event_id}')"


class DomainEvent(BaseEvent):
    """
    Domain Event - represents a business event

    Use this for events that represent business logic changes
    Example: OrderCreated, ProductStockUpdated, InvoiceGenerated
    """
    aggregate_id: Optional[str] = Field(None, description="ID of the aggregate (entity) this event relates to")
    aggregate_type: Optional[str] = Field(None, description="Type of aggregate (e.g., 'Order', 'Product')")

    def __init__(self, **data):
        """
        Initialize domain event

        Automatically sets correlation_id if not provided
        """
        if 'correlation_id' not in data:
            data['correlation_id'] = data.get('event_id') or uuid4()
        super().__init__(**data)
