from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Date, Numeric, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from datetime import datetime
from decimal import Decimal
import enum


class InvoiceTypeEnum(str, enum.Enum):
    SALES = "SALES"
    PURCHASE = "PURCHASE"
    CREDIT_NOTE = "CREDIT_NOTE"
    DEBIT_NOTE = "DEBIT_NOTE"


class InvoiceStatusEnum(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    PAID = "PAID"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class PaymentTermsEnum(str, enum.Enum):
    IMMEDIATE = "IMMEDIATE"
    NET_7 = "NET_7"
    NET_15 = "NET_15"
    NET_30 = "NET_30"
    NET_60 = "NET_60"
    NET_90 = "NET_90"
    CUSTOM = "CUSTOM"


class SalesInvoice(Base):
    """فواتير المبيعات - Sales Invoices"""
    __tablename__ = "sales_invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(100), unique=True, nullable=False, index=True)
    
    # Customer and reference information
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=True)  # Optional reference to sales order
    
    # Organization references
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    
    # Invoice details
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    exchange_rate = Column(Numeric(10, 4), default=1.0000, nullable=False)
    
    # Status and type
    invoice_type = Column(Enum(InvoiceTypeEnum), default=InvoiceTypeEnum.SALES, nullable=False)
    status = Column(Enum(InvoiceStatusEnum), default=InvoiceStatusEnum.DRAFT, nullable=False)
    payment_terms = Column(Enum(PaymentTermsEnum), default=PaymentTermsEnum.NET_30, nullable=False)
    
    # Financial details
    subtotal = Column(Numeric(15, 2), nullable=False, default=0)
    discount_percentage = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    tax_percentage = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    shipping_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False, default=0)
    paid_amount = Column(Numeric(15, 2), default=0)
    
    # Additional information
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    payment_method = Column(String(50), nullable=True)
    reference_number = Column(String(100), nullable=True)
    
    # Tracking
    is_recurring = Column(Boolean, default=False)
    recurring_frequency = Column(String(20), nullable=True)  # MONTHLY, QUARTERLY, YEARLY
    parent_invoice_id = Column(Integer, ForeignKey("sales_invoices.id"), nullable=True)
    
    # Audit fields
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    issued_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="sales_invoices")
    sales_order = relationship("SalesOrder", back_populates="sales_invoices")
    branch = relationship("Branch")
    warehouse = relationship("Warehouse")
    currency = relationship("Currency")
    invoice_items = relationship("SalesInvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("InvoicePayment", back_populates="sales_invoice", cascade="all, delete-orphan")
    created_by_user = relationship("User")
    parent_invoice = relationship("SalesInvoice", remote_side=[id])
    
    @property
    def remaining_amount(self):
        """المبلغ المتبقي"""
        return self.total_amount - self.paid_amount

    @property
    def is_fully_paid(self):
        """هل تم دفع الفاتورة بالكامل"""
        return self.paid_amount >= self.total_amount

    @property
    def is_overdue(self):
        """هل الفاتورة متأخرة"""
        from datetime import date
        return self.due_date < date.today() and not self.is_fully_paid

    def __repr__(self):
        return f"<SalesInvoice {self.invoice_number}: {self.total_amount}>"


class SalesInvoiceItem(Base):
    """عناصر فواتير المبيعات - Sales Invoice Items"""
    __tablename__ = "sales_invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("sales_invoices.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    sales_item_id = Column(Integer, ForeignKey("sales_items.id"), nullable=True)  # Reference to original sales order item
    
    # Item details
    quantity = Column(Numeric(15, 3), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    discount_percentage = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    line_total = Column(Numeric(12, 2), nullable=False)
    
    # Additional information
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    invoice = relationship("SalesInvoice", back_populates="invoice_items")
    product = relationship("Product", back_populates="sales_invoice_items")
    sales_item = relationship("SalesItem")

    def __repr__(self):
        return f"<SalesInvoiceItem {self.product_id}: {self.quantity} x {self.unit_price}>"


class PurchaseInvoice(Base):
    """فواتير المشتريات - Purchase Invoices"""
    __tablename__ = "purchase_invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(100), unique=True, nullable=False, index=True)
    supplier_invoice_number = Column(String(100), nullable=True)  # Supplier's invoice number
    
    # Supplier and reference information
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True)
    
    # Organization references
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    
    # Invoice details
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    received_date = Column(Date, nullable=True)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    exchange_rate = Column(Numeric(10, 4), default=1.0000, nullable=False)
    
    # Status and type
    invoice_type = Column(Enum(InvoiceTypeEnum), default=InvoiceTypeEnum.PURCHASE, nullable=False)
    status = Column(Enum(InvoiceStatusEnum), default=InvoiceStatusEnum.DRAFT, nullable=False)
    payment_terms = Column(Enum(PaymentTermsEnum), default=PaymentTermsEnum.NET_30, nullable=False)
    
    # Financial details
    subtotal = Column(Numeric(15, 2), nullable=False, default=0)
    discount_percentage = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    tax_percentage = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    shipping_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False, default=0)
    paid_amount = Column(Numeric(15, 2), default=0)
    
    # Additional information
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    payment_method = Column(String(50), nullable=True)
    reference_number = Column(String(100), nullable=True)
    
    # Audit fields
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    received_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    supplier = relationship("Supplier", back_populates="purchase_invoices")
    purchase_order = relationship("PurchaseOrder", back_populates="purchase_invoices")
    branch = relationship("Branch")
    warehouse = relationship("Warehouse")
    currency = relationship("Currency")
    invoice_items = relationship("PurchaseInvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("InvoicePayment", back_populates="purchase_invoice", cascade="all, delete-orphan")
    created_by_user = relationship("User")

    @property
    def remaining_amount(self):
        """المبلغ المتبقي"""
        return self.total_amount - self.paid_amount

    @property
    def is_fully_paid(self):
        """هل تم دفع الفاتورة بالكامل"""
        return self.paid_amount >= self.total_amount

    @property
    def is_overdue(self):
        """هل الفاتورة متأخرة"""
        from datetime import date
        return self.due_date < date.today() and not self.is_fully_paid

    def __repr__(self):
        return f"<PurchaseInvoice {self.invoice_number}: {self.total_amount}>"


class PurchaseInvoiceItem(Base):
    """عناصر فواتير المشتريات - Purchase Invoice Items"""
    __tablename__ = "purchase_invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("purchase_invoices.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    purchase_item_id = Column(Integer, ForeignKey("purchase_items.id"), nullable=True)
    
    # Item details
    quantity = Column(Numeric(15, 3), nullable=False)
    unit_cost = Column(Numeric(10, 2), nullable=False)
    discount_percentage = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    line_total = Column(Numeric(12, 2), nullable=False)
    
    # Additional information
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    invoice = relationship("PurchaseInvoice", back_populates="invoice_items")
    product = relationship("Product", back_populates="purchase_invoice_items")
    purchase_item = relationship("PurchaseItem")

    def __repr__(self):
        return f"<PurchaseInvoiceItem {self.product_id}: {self.quantity} x {self.unit_cost}>"


class InvoicePayment(Base):
    """مدفوعات الفواتير - Invoice Payments"""
    __tablename__ = "invoice_payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(String(100), unique=True, nullable=False, index=True)
    
    # Invoice references
    sales_invoice_id = Column(Integer, ForeignKey("sales_invoices.id"), nullable=True)
    purchase_invoice_id = Column(Integer, ForeignKey("purchase_invoices.id"), nullable=True)
    
    # Payment details
    payment_date = Column(Date, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    exchange_rate = Column(Numeric(10, 4), default=1.0000, nullable=False)
    
    # Payment method and details
    payment_method = Column(String(50), nullable=False)  # CASH, BANK_TRANSFER, CHECK, CREDIT_CARD
    reference_number = Column(String(100), nullable=True)
    bank_account = Column(String(100), nullable=True)
    check_number = Column(String(50), nullable=True)
    check_date = Column(Date, nullable=True)
    
    # Additional information
    notes = Column(Text, nullable=True)
    
    # Audit fields
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    sales_invoice = relationship("SalesInvoice", back_populates="payments")
    purchase_invoice = relationship("PurchaseInvoice", back_populates="payments")
    currency = relationship("Currency")
    created_by_user = relationship("User")

    def __repr__(self):
        return f"<InvoicePayment {self.payment_number}: {self.amount}>"
