from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from .product import ProductSummary
from .customer import Customer


# Sales Item Schemas
class SalesItemBase(BaseModel):
    product_id: int
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)
    discount_percentage: Decimal = Field(0, ge=0, le=100)
    discount_amount: Decimal = Field(0, ge=0)
    notes: Optional[str] = None


class SalesItemCreate(SalesItemBase):
    pass


class SalesItemUpdate(BaseModel):
    product_id: Optional[int] = None
    quantity: Optional[Decimal] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, gt=0)
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None


class SalesItem(SalesItemBase):
    id: int
    sales_order_id: int
    line_total: Decimal
    delivered_quantity: Decimal
    remaining_quantity: Decimal
    product: ProductSummary
    
    class Config:
        from_attributes = True


# Sales Order Schemas
class SalesOrderBase(BaseModel):
    customer_id: int
    branch_id: int
    warehouse_id: int
    order_date: date
    expected_delivery_date: Optional[date] = None
    status: str = Field("DRAFT", max_length=50)
    payment_method: Optional[str] = Field(None, max_length=50)
    discount_percentage: Decimal = Field(0, ge=0, le=100)
    tax_percentage: Decimal = Field(0, ge=0, le=100)
    notes: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['DRAFT', 'CONFIRMED', 'SHIPPED', 'DELIVERED', 'CANCELLED']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

    @validator('payment_method')
    def validate_payment_method(cls, v):
        if v is not None:
            allowed_methods = ['CASH', 'CREDIT', 'BANK_TRANSFER', 'CHECK']
            if v not in allowed_methods:
                raise ValueError(f'Payment method must be one of: {", ".join(allowed_methods)}')
        return v


class SalesOrderCreate(SalesOrderBase):
    sales_items: List[SalesItemCreate] = Field(..., min_items=1)


class SalesOrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    branch_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    order_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    status: Optional[str] = Field(None, max_length=50)
    payment_status: Optional[str] = Field(None, max_length=50)
    payment_method: Optional[str] = Field(None, max_length=50)
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    tax_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    notes: Optional[str] = None


class SalesOrder(SalesOrderBase):
    id: int
    order_number: str
    actual_delivery_date: Optional[date]
    payment_status: str
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    remaining_amount: Decimal
    is_fully_paid: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]
    customer: Customer
    sales_items: List[SalesItem]
    
    class Config:
        from_attributes = True


class SalesOrderSummary(BaseModel):
    """ملخص أمر البيع للاستخدام في القوائم"""
    id: int
    order_number: str
    customer_name: str
    order_date: date
    status: str
    payment_status: str
    total_amount: Decimal
    remaining_amount: Decimal
    
    class Config:
        from_attributes = True
