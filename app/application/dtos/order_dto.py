"""
Order Data Transfer Objects

DTOs for order data validation and transfer.
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from decimal import Decimal


class OrderItemDTO(BaseModel):
    """DTO for order item (line item)."""

    product_id: int = Field(..., description="Product ID")
    quantity: float = Field(..., gt=0, description="Quantity ordered")
    unit_price: float = Field(..., ge=0, description="Unit price")
    discount_percentage: float = Field(0.0, ge=0, le=100, description="Discount percentage")
    discount_amount: float = Field(0.0, ge=0, description="Discount amount")
    notes: Optional[str] = Field(None, description="Item notes")

    class Config:
        from_attributes = True


class OrderItemResponseDTO(BaseModel):
    """DTO for order item response."""

    id: int
    product_id: int
    quantity: float
    unit_price: float
    discount_percentage: float = 0.0
    discount_amount: float = 0.0
    line_total: float
    delivered_quantity: float = 0.0
    notes: Optional[str] = None

    @property
    def remaining_quantity(self) -> float:
        """Calculate remaining quantity to deliver."""
        return self.quantity - self.delivered_quantity

    class Config:
        from_attributes = True


class OrderCreateDTO(BaseModel):
    """DTO for creating a new order."""

    customer_id: int = Field(..., description="Customer ID")
    branch_id: int = Field(..., description="Branch ID")
    warehouse_id: int = Field(..., description="Warehouse ID")
    order_date: date = Field(..., description="Order date")
    expected_delivery_date: Optional[date] = Field(None, description="Expected delivery date")

    # Order items
    items: List[OrderItemDTO] = Field(..., min_items=1, description="Order items")

    # Payment
    payment_method: Optional[str] = Field(None, description="Payment method")

    # Discounts and taxes
    discount_percentage: float = Field(0.0, ge=0, le=100, description="Order discount percentage")
    discount_amount: float = Field(0.0, ge=0, description="Order discount amount")
    tax_percentage: float = Field(0.0, ge=0, le=100, description="Tax percentage")

    # Additional info
    notes: Optional[str] = Field(None, description="Order notes")
    created_by: int = Field(..., description="User ID who created the order")

    @validator('expected_delivery_date')
    def validate_delivery_date(cls, v, values):
        """Validate that delivery date is not before order date."""
        if v and 'order_date' in values and v < values['order_date']:
            raise ValueError('Expected delivery date cannot be before order date')
        return v

    @validator('items')
    def validate_items(cls, v):
        """Validate that there is at least one item."""
        if not v or len(v) == 0:
            raise ValueError('Order must have at least one item')
        return v

    class Config:
        from_attributes = True


class OrderUpdateDTO(BaseModel):
    """DTO for updating an existing order."""

    customer_id: Optional[int] = Field(None, description="Customer ID")
    branch_id: Optional[int] = Field(None, description="Branch ID")
    warehouse_id: Optional[int] = Field(None, description="Warehouse ID")
    order_date: Optional[date] = Field(None, description="Order date")
    expected_delivery_date: Optional[date] = Field(None, description="Expected delivery date")
    actual_delivery_date: Optional[date] = Field(None, description="Actual delivery date")

    status: Optional[str] = Field(None, description="Order status")
    payment_status: Optional[str] = Field(None, description="Payment status")
    payment_method: Optional[str] = Field(None, description="Payment method")

    # Amounts
    discount_percentage: Optional[float] = Field(None, ge=0, le=100, description="Discount percentage")
    discount_amount: Optional[float] = Field(None, ge=0, description="Discount amount")
    tax_percentage: Optional[float] = Field(None, ge=0, le=100, description="Tax percentage")

    notes: Optional[str] = Field(None, description="Order notes")

    class Config:
        from_attributes = True


class OrderResponseDTO(BaseModel):
    """DTO for order response."""

    id: int
    order_number: str
    customer_id: int
    branch_id: int
    warehouse_id: int
    order_date: date
    expected_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None

    status: str = "DRAFT"
    payment_status: str = "PENDING"
    payment_method: Optional[str] = None

    # Amounts
    subtotal: float = 0.0
    discount_percentage: float = 0.0
    discount_amount: float = 0.0
    tax_percentage: float = 0.0
    tax_amount: float = 0.0
    total_amount: float = 0.0
    paid_amount: float = 0.0

    notes: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    @property
    def remaining_amount(self) -> float:
        """Calculate remaining amount to pay."""
        return self.total_amount - self.paid_amount

    @property
    def is_fully_paid(self) -> bool:
        """Check if order is fully paid."""
        return self.paid_amount >= self.total_amount

    class Config:
        from_attributes = True


class OrderWithItemsResponseDTO(OrderResponseDTO):
    """DTO for order response with items included."""

    items: List[OrderItemResponseDTO] = []

    class Config:
        from_attributes = True


class OrderListResponseDTO(BaseModel):
    """DTO for order list response with pagination."""

    items: list[OrderResponseDTO]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True


class OrderSearchDTO(BaseModel):
    """DTO for order search parameters."""

    query: Optional[str] = Field(None, description="Search query")
    customer_id: Optional[int] = Field(None, description="Filter by customer")
    status: Optional[str] = Field(None, description="Filter by status")
    payment_status: Optional[str] = Field(None, description="Filter by payment status")
    branch_id: Optional[int] = Field(None, description="Filter by branch")
    salesperson_id: Optional[int] = Field(None, description="Filter by salesperson")
    start_date: Optional[date] = Field(None, description="Start date")
    end_date: Optional[date] = Field(None, description="End date")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum records to return")

    @validator('end_date')
    def validate_date_range(cls, v, values):
        """Validate that end date is not before start date."""
        if v and 'start_date' in values and values['start_date'] and v < values['start_date']:
            raise ValueError('End date cannot be before start date')
        return v

    class Config:
        from_attributes = True


class OrderSummaryDTO(BaseModel):
    """DTO for order summary information."""

    id: int
    order_number: str
    customer_id: int
    order_date: date
    status: str
    payment_status: str
    total_amount: float
    paid_amount: float

    class Config:
        from_attributes = True


class OrderStatusUpdateDTO(BaseModel):
    """DTO for updating order status."""

    order_id: int = Field(..., description="Order ID")
    status: str = Field(..., description="New status (DRAFT, CONFIRMED, SHIPPED, DELIVERED, CANCELLED)")

    @validator('status')
    def validate_status(cls, v):
        """Validate status values."""
        valid_statuses = ["DRAFT", "CONFIRMED", "SHIPPED", "DELIVERED", "CANCELLED"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

    class Config:
        from_attributes = True


class OrderPaymentUpdateDTO(BaseModel):
    """DTO for updating order payment."""

    order_id: int = Field(..., description="Order ID")
    payment_status: str = Field(..., description="Payment status (PENDING, PARTIAL, PAID, OVERDUE)")
    paid_amount: float = Field(..., ge=0, description="Amount paid")

    @validator('payment_status')
    def validate_payment_status(cls, v):
        """Validate payment status values."""
        valid_statuses = ["PENDING", "PARTIAL", "PAID", "OVERDUE"]
        if v not in valid_statuses:
            raise ValueError(f"Payment status must be one of: {', '.join(valid_statuses)}")
        return v

    class Config:
        from_attributes = True


class OrderStatisticsDTO(BaseModel):
    """DTO for order statistics."""

    total_orders: int
    confirmed_orders: int
    pending_orders: int
    delivered_orders: int
    cancelled_orders: int
    total_sales_amount: float
    average_order_value: float

    class Config:
        from_attributes = True
