from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


# Enums
class InvoiceTypeEnum(str, Enum):
    SALES = "SALES"
    PURCHASE = "PURCHASE"
    CREDIT_NOTE = "CREDIT_NOTE"
    DEBIT_NOTE = "DEBIT_NOTE"


class InvoiceStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    PAID = "PAID"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class PaymentTermsEnum(str, Enum):
    IMMEDIATE = "IMMEDIATE"
    NET_7 = "NET_7"
    NET_15 = "NET_15"
    NET_30 = "NET_30"
    NET_60 = "NET_60"
    NET_90 = "NET_90"
    CUSTOM = "CUSTOM"


# Sales Invoice Item Schemas
class SalesInvoiceItemBase(BaseModel):
    product_id: int
    sales_item_id: Optional[int] = None
    quantity: Decimal
    unit_price: Decimal
    discount_percentage: Optional[Decimal] = 0
    discount_amount: Optional[Decimal] = 0
    line_total: Decimal
    description: Optional[str] = None
    notes: Optional[str] = None


class SalesInvoiceItemCreate(SalesInvoiceItemBase):
    pass


class SalesInvoiceItemUpdate(BaseModel):
    product_id: Optional[int] = None
    sales_item_id: Optional[int] = None
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    line_total: Optional[Decimal] = None
    description: Optional[str] = None
    notes: Optional[str] = None


class SalesInvoiceItem(SalesInvoiceItemBase):
    id: int
    invoice_id: int

    class Config:
        from_attributes = True


# Sales Invoice Schemas
class SalesInvoiceBase(BaseModel):
    invoice_number: str
    customer_id: int
    sales_order_id: Optional[int] = None
    branch_id: int
    warehouse_id: Optional[int] = None
    invoice_date: date
    due_date: date
    currency_id: int
    exchange_rate: Optional[Decimal] = Decimal("1.0000")
    invoice_type: Optional[InvoiceTypeEnum] = InvoiceTypeEnum.SALES
    status: Optional[InvoiceStatusEnum] = InvoiceStatusEnum.DRAFT
    payment_terms: Optional[PaymentTermsEnum] = PaymentTermsEnum.NET_30
    subtotal: Decimal
    discount_percentage: Optional[Decimal] = 0
    discount_amount: Optional[Decimal] = 0
    tax_percentage: Optional[Decimal] = 0
    tax_amount: Optional[Decimal] = 0
    shipping_amount: Optional[Decimal] = 0
    total_amount: Decimal
    paid_amount: Optional[Decimal] = 0
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None
    is_recurring: Optional[bool] = False
    recurring_frequency: Optional[str] = None
    parent_invoice_id: Optional[int] = None


class SalesInvoiceCreate(SalesInvoiceBase):
    created_by: int
    invoice_items: List[SalesInvoiceItemCreate] = []


class SalesInvoiceUpdate(BaseModel):
    invoice_number: Optional[str] = None
    customer_id: Optional[int] = None
    sales_order_id: Optional[int] = None
    branch_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    currency_id: Optional[int] = None
    exchange_rate: Optional[Decimal] = None
    invoice_type: Optional[InvoiceTypeEnum] = None
    status: Optional[InvoiceStatusEnum] = None
    payment_terms: Optional[PaymentTermsEnum] = None
    subtotal: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    tax_percentage: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    shipping_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    paid_amount: Optional[Decimal] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurring_frequency: Optional[str] = None
    parent_invoice_id: Optional[int] = None


class SalesInvoice(SalesInvoiceBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    issued_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    remaining_amount: Decimal
    is_fully_paid: bool
    is_overdue: bool
    invoice_items: List[SalesInvoiceItem] = []

    class Config:
        from_attributes = True


# Purchase Invoice Item Schemas
class PurchaseInvoiceItemBase(BaseModel):
    product_id: int
    purchase_item_id: Optional[int] = None
    quantity: Decimal
    unit_cost: Decimal
    discount_percentage: Optional[Decimal] = 0
    discount_amount: Optional[Decimal] = 0
    line_total: Decimal
    description: Optional[str] = None
    notes: Optional[str] = None


class PurchaseInvoiceItemCreate(PurchaseInvoiceItemBase):
    pass


class PurchaseInvoiceItemUpdate(BaseModel):
    product_id: Optional[int] = None
    purchase_item_id: Optional[int] = None
    quantity: Optional[Decimal] = None
    unit_cost: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    line_total: Optional[Decimal] = None
    description: Optional[str] = None
    notes: Optional[str] = None


class PurchaseInvoiceItem(PurchaseInvoiceItemBase):
    id: int
    invoice_id: int

    class Config:
        from_attributes = True


# Purchase Invoice Schemas
class PurchaseInvoiceBase(BaseModel):
    invoice_number: str
    supplier_invoice_number: Optional[str] = None
    supplier_id: int
    purchase_order_id: Optional[int] = None
    branch_id: int
    warehouse_id: Optional[int] = None
    invoice_date: date
    due_date: date
    received_date: Optional[date] = None
    currency_id: int
    exchange_rate: Optional[Decimal] = Decimal("1.0000")
    invoice_type: Optional[InvoiceTypeEnum] = InvoiceTypeEnum.PURCHASE
    status: Optional[InvoiceStatusEnum] = InvoiceStatusEnum.DRAFT
    payment_terms: Optional[PaymentTermsEnum] = PaymentTermsEnum.NET_30
    subtotal: Decimal
    discount_percentage: Optional[Decimal] = 0
    discount_amount: Optional[Decimal] = 0
    tax_percentage: Optional[Decimal] = 0
    tax_amount: Optional[Decimal] = 0
    shipping_amount: Optional[Decimal] = 0
    total_amount: Decimal
    paid_amount: Optional[Decimal] = 0
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None


class PurchaseInvoiceCreate(PurchaseInvoiceBase):
    created_by: int
    invoice_items: List[PurchaseInvoiceItemCreate] = []


class PurchaseInvoiceUpdate(BaseModel):
    invoice_number: Optional[str] = None
    supplier_invoice_number: Optional[str] = None
    supplier_id: Optional[int] = None
    purchase_order_id: Optional[int] = None
    branch_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    received_date: Optional[date] = None
    currency_id: Optional[int] = None
    exchange_rate: Optional[Decimal] = None
    invoice_type: Optional[InvoiceTypeEnum] = None
    status: Optional[InvoiceStatusEnum] = None
    payment_terms: Optional[PaymentTermsEnum] = None
    subtotal: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    tax_percentage: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    shipping_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    paid_amount: Optional[Decimal] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None


class PurchaseInvoice(PurchaseInvoiceBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    remaining_amount: Decimal
    is_fully_paid: bool
    is_overdue: bool
    invoice_items: List[PurchaseInvoiceItem] = []

    class Config:
        from_attributes = True


# Invoice Payment Schemas
class InvoicePaymentBase(BaseModel):
    payment_number: str
    sales_invoice_id: Optional[int] = None
    purchase_invoice_id: Optional[int] = None
    payment_date: date
    amount: Decimal
    currency_id: int
    exchange_rate: Optional[Decimal] = Decimal("1.0000")
    payment_method: str
    reference_number: Optional[str] = None
    bank_account: Optional[str] = None
    check_number: Optional[str] = None
    check_date: Optional[date] = None
    notes: Optional[str] = None


class InvoicePaymentCreate(InvoicePaymentBase):
    created_by: int


class InvoicePaymentUpdate(BaseModel):
    payment_number: Optional[str] = None
    sales_invoice_id: Optional[int] = None
    purchase_invoice_id: Optional[int] = None
    payment_date: Optional[date] = None
    amount: Optional[Decimal] = None
    currency_id: Optional[int] = None
    exchange_rate: Optional[Decimal] = None
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None
    bank_account: Optional[str] = None
    check_number: Optional[str] = None
    check_date: Optional[date] = None
    notes: Optional[str] = None


class InvoicePayment(InvoicePaymentBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Summary schemas for dashboards
class InvoiceSummary(BaseModel):
    total_sales_invoices: int
    total_purchase_invoices: int
    total_sales_amount: Decimal
    total_purchase_amount: Decimal
    pending_sales_amount: Decimal
    pending_purchase_amount: Decimal
    overdue_sales_count: int
    overdue_purchase_count: int


class InvoiceFilter(BaseModel):
    status: Optional[InvoiceStatusEnum] = None
    invoice_type: Optional[InvoiceTypeEnum] = None
    customer_id: Optional[int] = None
    supplier_id: Optional[int] = None
    branch_id: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    search: Optional[str] = None
