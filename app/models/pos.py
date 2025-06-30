from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime
import enum


class PaymentMethodEnum(str, enum.Enum):
    CASH = "CASH"
    CARD = "CARD"
    MOBILE = "MOBILE"
    CREDIT = "CREDIT"
    VOUCHER = "VOUCHER"


class POSTransactionTypeEnum(str, enum.Enum):
    SALE = "SALE"
    REFUND = "REFUND"
    EXCHANGE = "EXCHANGE"
    VOID = "VOID"


class POSSessionStatusEnum(str, enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    SUSPENDED = "SUSPENDED"


class POSTerminal(Base):
    """محطة نقاط البيع - POS Terminal"""
    __tablename__ = "pos_terminals"

    id = Column(Integer, primary_key=True, index=True)
    terminal_code = Column(String(50), unique=True, nullable=False, index=True)
    name_ar = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    
    # Hardware configuration
    receipt_printer = Column(String(255))  # Receipt printer name/IP
    barcode_scanner = Column(String(255))  # Barcode scanner config
    cash_drawer = Column(String(255))     # Cash drawer config
    display = Column(String(255))         # Customer display config
    
    # Software configuration
    default_tax_rate = Column(Numeric(5, 2), default=0)
    allow_discount = Column(Boolean, default=True)
    max_discount_percent = Column(Numeric(5, 2), default=100)
    allow_negative_stock = Column(Boolean, default=False)
    auto_print_receipt = Column(Boolean, default=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    branch = relationship("Branch")
    warehouse = relationship("Warehouse")
    pos_sessions = relationship("POSSession", back_populates="terminal")
    pos_transactions = relationship("POSTransaction", back_populates="terminal")


class POSSession(Base):
    """جلسة نقاط البيع - POS Session"""
    __tablename__ = "pos_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_number = Column(String(50), unique=True, nullable=False, index=True)
    terminal_id = Column(Integer, ForeignKey("pos_terminals.id"), nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime)
    status = Column(Enum(POSSessionStatusEnum), nullable=False, default=POSSessionStatusEnum.OPEN)
    
    # Opening balances
    opening_cash_amount = Column(Numeric(15, 2), nullable=False, default=0)
    opening_notes = Column(Text)
    
    # Closing balances
    closing_cash_amount = Column(Numeric(15, 2), default=0)
    closing_card_amount = Column(Numeric(15, 2), default=0)
    closing_mobile_amount = Column(Numeric(15, 2), default=0)
    closing_total_amount = Column(Numeric(15, 2), default=0)
    closing_notes = Column(Text)
    
    # Calculated totals
    total_sales = Column(Numeric(15, 2), default=0)
    total_refunds = Column(Numeric(15, 2), default=0)
    total_discounts = Column(Numeric(15, 2), default=0)
    total_tax = Column(Numeric(15, 2), default=0)
    transaction_count = Column(Integer, default=0)
    
    closed_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    terminal = relationship("POSTerminal", back_populates="pos_sessions")
    currency = relationship("Currency", back_populates="pos_sessions")
    user = relationship("User", foreign_keys=[user_id])
    closer = relationship("User", foreign_keys=[closed_by])
    pos_transactions = relationship("POSTransaction", back_populates="pos_session")


class POSTransaction(Base):
    """معاملة نقاط البيع - POS Transaction"""
    __tablename__ = "pos_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_number = Column(String(50), unique=True, nullable=False, index=True)
    terminal_id = Column(Integer, ForeignKey("pos_terminals.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("pos_sessions.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=True)
    
    transaction_type = Column(Enum(POSTransactionTypeEnum), nullable=False, default=POSTransactionTypeEnum.SALE)
    transaction_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Amounts
    subtotal = Column(Numeric(15, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(15, 2), nullable=False, default=0)
    discount_percent = Column(Numeric(5, 2), nullable=False, default=0)
    tax_amount = Column(Numeric(15, 2), nullable=False, default=0)
    tax_percent = Column(Numeric(5, 2), nullable=False, default=0)
    total_amount = Column(Numeric(15, 2), nullable=False, default=0)
    
    # Payment details
    amount_paid = Column(Numeric(15, 2), nullable=False, default=0)
    change_amount = Column(Numeric(15, 2), nullable=False, default=0)
    
    # Additional info
    receipt_number = Column(String(50))
    notes = Column(Text)
    void_reason = Column(String(255))
    voided_at = Column(DateTime)
    voided_by = Column(Integer, ForeignKey("users.id"))
    
    cashier_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    terminal = relationship("POSTerminal", back_populates="pos_transactions")
    pos_session = relationship("POSSession", back_populates="pos_transactions")
    customer = relationship("Customer")
    sales_order = relationship("SalesOrder")
    cashier = relationship("User", foreign_keys=[cashier_id])
    voider = relationship("User", foreign_keys=[voided_by])
    pos_transaction_items = relationship("POSTransactionItem", back_populates="pos_transaction", cascade="all, delete-orphan")
    pos_payments = relationship("POSPayment", back_populates="pos_transaction", cascade="all, delete-orphan")


class POSTransactionItem(Base):
    """عنصر معاملة نقاط البيع - POS Transaction Item"""
    __tablename__ = "pos_transaction_items"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("pos_transactions.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    line_number = Column(Integer, nullable=False)
    quantity = Column(Numeric(10, 3), nullable=False)
    unit_price = Column(Numeric(15, 2), nullable=False)
    
    # Discounts
    discount_amount = Column(Numeric(15, 2), nullable=False, default=0)
    discount_percent = Column(Numeric(5, 2), nullable=False, default=0)
    
    # Tax
    tax_amount = Column(Numeric(15, 2), nullable=False, default=0)
    tax_percent = Column(Numeric(5, 2), nullable=False, default=0)
    
    # Totals
    line_total = Column(Numeric(15, 2), nullable=False)
    
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    pos_transaction = relationship("POSTransaction", back_populates="pos_transaction_items")
    product = relationship("Product")


class POSPayment(Base):
    """دفع نقاط البيع - POS Payment"""
    __tablename__ = "pos_payments"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("pos_transactions.id"), nullable=False)
    
    payment_method = Column(Enum(PaymentMethodEnum), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    
    # Card payment details
    card_type = Column(String(50))  # VISA, MASTERCARD, etc.
    card_last_four = Column(String(4))
    approval_code = Column(String(50))
    reference_number = Column(String(100))
    
    # Mobile payment details
    mobile_number = Column(String(20))
    mobile_provider = Column(String(50))  # ZAIN, ASIA_CELL, etc.
    mobile_reference = Column(String(100))
    
    # Credit payment details
    credit_reference = Column(String(100))
    
    # Voucher details
    voucher_code = Column(String(100))
    voucher_type = Column(String(50))
    
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    pos_transaction = relationship("POSTransaction", back_populates="pos_payments")


class POSDiscount(Base):
    """خصم نقاط البيع - POS Discount"""
    __tablename__ = "pos_discounts"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name_ar = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=False)
    
    discount_type = Column(String(20), nullable=False)  # PERCENTAGE, FIXED
    discount_value = Column(Numeric(15, 2), nullable=False)
    
    # Conditions
    min_amount = Column(Numeric(15, 2))
    max_amount = Column(Numeric(15, 2))
    min_quantity = Column(Integer)
    applicable_products = Column(Text)  # JSON list of product IDs
    applicable_categories = Column(Text)  # JSON list of category IDs
    
    # Validity
    valid_from = Column(DateTime)
    valid_to = Column(DateTime)
    usage_limit = Column(Integer)
    usage_count = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class POSPromotion(Base):
    """عرض ترويجي نقاط البيع - POS Promotion"""
    __tablename__ = "pos_promotions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name_ar = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=False)
    description_ar = Column(Text)
    description_en = Column(Text)
    
    promotion_type = Column(String(50), nullable=False)  # BUY_X_GET_Y, BUNDLE, DISCOUNT
    
    # Configuration (JSON)
    rules = Column(Text)  # JSON rules for promotion
    
    # Validity
    valid_from = Column(DateTime)
    valid_to = Column(DateTime)
    usage_limit = Column(Integer)
    usage_count = Column(Integer, default=0)
    
    # Priority (higher number = higher priority)
    priority = Column(Integer, default=1)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
