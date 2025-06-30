from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


class PaymentMethodEnum(str, Enum):
    CASH = "CASH"
    CARD = "CARD"
    MOBILE = "MOBILE"
    CREDIT = "CREDIT"
    VOUCHER = "VOUCHER"


class POSTransactionTypeEnum(str, Enum):
    SALE = "SALE"
    REFUND = "REFUND"
    EXCHANGE = "EXCHANGE"
    VOID = "VOID"


class POSSessionStatusEnum(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    SUSPENDED = "SUSPENDED"


# POS Terminal Schemas
class POSTerminalBase(BaseModel):
    terminal_code: str = Field(..., max_length=50)
    name_ar: str = Field(..., max_length=255)
    name_en: str = Field(..., max_length=255)
    branch_id: int
    warehouse_id: int
    receipt_printer: Optional[str] = Field(None, max_length=255)
    barcode_scanner: Optional[str] = Field(None, max_length=255)
    cash_drawer: Optional[str] = Field(None, max_length=255)
    display: Optional[str] = Field(None, max_length=255)
    default_tax_rate: Decimal = Field(0, ge=0, le=100)
    allow_discount: bool = True
    max_discount_percent: Decimal = Field(100, ge=0, le=100)
    allow_negative_stock: bool = False
    auto_print_receipt: bool = True
    is_active: bool = True


class POSTerminalCreate(POSTerminalBase):
    pass


class POSTerminalUpdate(BaseModel):
    name_ar: Optional[str] = Field(None, max_length=255)
    name_en: Optional[str] = Field(None, max_length=255)
    branch_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    receipt_printer: Optional[str] = Field(None, max_length=255)
    barcode_scanner: Optional[str] = Field(None, max_length=255)
    cash_drawer: Optional[str] = Field(None, max_length=255)
    display: Optional[str] = Field(None, max_length=255)
    default_tax_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    allow_discount: Optional[bool] = None
    max_discount_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    allow_negative_stock: Optional[bool] = None
    auto_print_receipt: Optional[bool] = None
    is_active: Optional[bool] = None


class POSTerminal(POSTerminalBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# POS Session Schemas
class POSSessionBase(BaseModel):
    terminal_id: int
    currency_id: int
    user_id: int
    opening_cash_amount: Decimal = Field(0, ge=0)
    opening_notes: Optional[str] = None


class POSSessionCreate(POSSessionBase):
    pass


class POSSessionUpdate(BaseModel):
    closing_cash_amount: Optional[Decimal] = Field(None, ge=0)
    closing_card_amount: Optional[Decimal] = Field(None, ge=0)
    closing_mobile_amount: Optional[Decimal] = Field(None, ge=0)
    closing_total_amount: Optional[Decimal] = Field(None, ge=0)
    closing_notes: Optional[str] = None
    status: Optional[POSSessionStatusEnum] = None


class POSSession(POSSessionBase):
    id: int
    session_number: str
    start_time: datetime
    end_time: Optional[datetime]
    status: POSSessionStatusEnum
    closing_cash_amount: Decimal
    closing_card_amount: Decimal
    closing_mobile_amount: Decimal
    closing_total_amount: Decimal
    closing_notes: Optional[str]
    total_sales: Decimal
    total_refunds: Decimal
    total_discounts: Decimal
    total_tax: Decimal
    transaction_count: int
    closed_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# POS Payment Schemas
class POSPaymentBase(BaseModel):
    payment_method: PaymentMethodEnum
    amount: Decimal = Field(..., gt=0)
    card_type: Optional[str] = Field(None, max_length=50)
    card_last_four: Optional[str] = Field(None, max_length=4)
    approval_code: Optional[str] = Field(None, max_length=50)
    reference_number: Optional[str] = Field(None, max_length=100)
    mobile_number: Optional[str] = Field(None, max_length=20)
    mobile_provider: Optional[str] = Field(None, max_length=50)
    mobile_reference: Optional[str] = Field(None, max_length=100)
    credit_reference: Optional[str] = Field(None, max_length=100)
    voucher_code: Optional[str] = Field(None, max_length=100)
    voucher_type: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class POSPaymentCreate(POSPaymentBase):
    pass


class POSPayment(POSPaymentBase):
    id: int
    transaction_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# POS Transaction Item Schemas
class POSTransactionItemBase(BaseModel):
    product_id: int
    line_number: int
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)
    discount_amount: Decimal = Field(0, ge=0)
    discount_percent: Decimal = Field(0, ge=0, le=100)
    tax_amount: Decimal = Field(0, ge=0)
    tax_percent: Decimal = Field(0, ge=0, le=100)
    line_total: Decimal = Field(..., ge=0)
    notes: Optional[str] = None


class POSTransactionItemCreate(POSTransactionItemBase):
    pass


class POSTransactionItem(POSTransactionItemBase):
    id: int
    transaction_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# POS Transaction Schemas
class POSTransactionBase(BaseModel):
    terminal_id: int
    session_id: int
    customer_id: Optional[int] = None
    sales_order_id: Optional[int] = None
    transaction_type: POSTransactionTypeEnum = POSTransactionTypeEnum.SALE
    transaction_date: datetime = Field(default_factory=datetime.utcnow)
    subtotal: Decimal = Field(0, ge=0)
    discount_amount: Decimal = Field(0, ge=0)
    discount_percent: Decimal = Field(0, ge=0, le=100)
    tax_amount: Decimal = Field(0, ge=0)
    tax_percent: Decimal = Field(0, ge=0, le=100)
    total_amount: Decimal = Field(0, ge=0)
    amount_paid: Decimal = Field(0, ge=0)
    change_amount: Decimal = Field(0, ge=0)
    receipt_number: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    cashier_id: int


class POSTransactionCreate(POSTransactionBase):
    items: List[POSTransactionItemCreate]
    payments: List[POSPaymentCreate]

    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('Transaction must have at least one item')
        return v

    @validator('payments')
    def validate_payments(cls, v):
        if not v:
            raise ValueError('Transaction must have at least one payment')
        return v


class POSTransactionUpdate(BaseModel):
    customer_id: Optional[int] = None
    notes: Optional[str] = None
    void_reason: Optional[str] = Field(None, max_length=255)


class POSTransaction(POSTransactionBase):
    id: int
    transaction_number: str
    void_reason: Optional[str]
    voided_at: Optional[datetime]
    voided_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    items: List[POSTransactionItem] = []
    payments: List[POSPayment] = []
    
    class Config:
        from_attributes = True


# POS Discount Schemas
class POSDiscountBase(BaseModel):
    code: str = Field(..., max_length=50)
    name_ar: str = Field(..., max_length=255)
    name_en: str = Field(..., max_length=255)
    discount_type: str = Field(..., max_length=20)  # PERCENTAGE, FIXED
    discount_value: Decimal = Field(..., gt=0)
    min_amount: Optional[Decimal] = Field(None, ge=0)
    max_amount: Optional[Decimal] = Field(None, ge=0)
    min_quantity: Optional[int] = Field(None, ge=1)
    applicable_products: Optional[str] = None  # JSON list
    applicable_categories: Optional[str] = None  # JSON list
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    usage_limit: Optional[int] = Field(None, ge=1)
    is_active: bool = True

    @validator('discount_type')
    def validate_discount_type(cls, v):
        if v not in ['PERCENTAGE', 'FIXED']:
            raise ValueError('Discount type must be PERCENTAGE or FIXED')
        return v


class POSDiscountCreate(POSDiscountBase):
    pass


class POSDiscountUpdate(BaseModel):
    name_ar: Optional[str] = Field(None, max_length=255)
    name_en: Optional[str] = Field(None, max_length=255)
    discount_type: Optional[str] = Field(None, max_length=20)
    discount_value: Optional[Decimal] = Field(None, gt=0)
    min_amount: Optional[Decimal] = Field(None, ge=0)
    max_amount: Optional[Decimal] = Field(None, ge=0)
    min_quantity: Optional[int] = Field(None, ge=1)
    applicable_products: Optional[str] = None
    applicable_categories: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    usage_limit: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class POSDiscount(POSDiscountBase):
    id: int
    usage_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# POS Promotion Schemas
class POSPromotionBase(BaseModel):
    code: str = Field(..., max_length=50)
    name_ar: str = Field(..., max_length=255)
    name_en: str = Field(..., max_length=255)
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    promotion_type: str = Field(..., max_length=50)  # BUY_X_GET_Y, BUNDLE, DISCOUNT
    rules: Optional[str] = None  # JSON rules
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    usage_limit: Optional[int] = Field(None, ge=1)
    priority: int = Field(1, ge=1)
    is_active: bool = True

    @validator('promotion_type')
    def validate_promotion_type(cls, v):
        if v not in ['BUY_X_GET_Y', 'BUNDLE', 'DISCOUNT']:
            raise ValueError('Promotion type must be BUY_X_GET_Y, BUNDLE, or DISCOUNT')
        return v


class POSPromotionCreate(POSPromotionBase):
    pass


class POSPromotionUpdate(BaseModel):
    name_ar: Optional[str] = Field(None, max_length=255)
    name_en: Optional[str] = Field(None, max_length=255)
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    promotion_type: Optional[str] = Field(None, max_length=50)
    rules: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    usage_limit: Optional[int] = Field(None, ge=1)
    priority: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class POSPromotion(POSPromotionBase):
    id: int
    usage_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# POS Report Schemas
class POSSalesReport(BaseModel):
    """تقرير مبيعات نقاط البيع"""
    from_date: datetime
    to_date: datetime
    terminal_id: Optional[int]
    total_transactions: int
    total_sales: Decimal
    total_refunds: Decimal
    total_discounts: Decimal
    total_tax: Decimal
    net_sales: Decimal
    payment_methods: List[dict]  # Breakdown by payment method


class POSSessionReport(BaseModel):
    """تقرير جلسة نقاط البيع"""
    session_id: int
    session_number: str
    terminal_code: str
    cashier_name: str
    start_time: datetime
    end_time: Optional[datetime]
    status: POSSessionStatusEnum
    opening_cash: Decimal
    closing_cash: Decimal
    total_sales: Decimal
    total_transactions: int
    cash_difference: Decimal


class POSProductSalesReport(BaseModel):
    """تقرير مبيعات المنتجات في نقاط البيع"""
    from_date: datetime
    to_date: datetime
    products: List[dict]  # Product sales details
    top_selling_products: List[dict]
    total_items_sold: int
