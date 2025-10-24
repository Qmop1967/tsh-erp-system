"""Return request schemas"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from prss.models.base import ReturnStatus


class ReturnRequestCreate(BaseModel):
    """Create return request"""
    customer_id: int
    sales_order_id: Optional[int] = None
    invoice_id: Optional[int] = None
    product_id: int
    serial_number: Optional[str] = None
    reason_code: str
    reason_description: Optional[str] = None
    photos: List[dict] = []
    videos: List[dict] = []


class ReturnRequestUpdate(BaseModel):
    """Update return request"""
    status: Optional[ReturnStatus] = None
    priority: Optional[int] = None
    photos: Optional[List[dict]] = None


class ReturnRequestResponse(BaseModel):
    """Return request response"""
    id: int
    customer_id: int
    sales_order_id: Optional[int]
    product_id: int
    serial_number: Optional[str]
    status: ReturnStatus
    reason_code: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReturnReceiveRequest(BaseModel):
    """Receive return request"""
    notes: Optional[str] = None
    received_by: int
    condition_photos: List[dict] = []
