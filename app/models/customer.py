from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Customer(Base):
    """العملاء"""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    company_name = Column(String(200), nullable=True)
    phone = Column(String(20), nullable=True, index=True)
    email = Column(String(255), nullable=True, index=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    tax_number = Column(String(50), nullable=True)
    credit_limit = Column(Numeric(12, 2), default=0)  # حد الائتمان
    payment_terms = Column(Integer, default=0)  # شروط الدفع بالأيام
    discount_percentage = Column(Numeric(5, 2), default=0)  # نسبة الخصم
    currency = Column(String(3), default='IQD')  # عملة العميل (USD, EUR, IQD, etc.)
    portal_language = Column(String(5), default='en')  # لغة البوابة (en, ar, etc.)
    salesperson_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # مندوب المبيعات
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # العلاقات
    sales_orders = relationship("SalesOrder", back_populates="customer")
    sales_invoices = relationship("SalesInvoice", back_populates="customer")
    salesperson = relationship("User", foreign_keys=[salesperson_id])
    addresses = relationship("CustomerAddress", back_populates="customer")
    carts = relationship("Cart", back_populates="customer")


class Supplier(Base):
    """الموردين"""
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    supplier_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    company_name = Column(String(200), nullable=True)
    phone = Column(String(20), nullable=True, index=True)
    email = Column(String(255), nullable=True, index=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    tax_number = Column(String(50), nullable=True)
    payment_terms = Column(Integer, default=30)  # شروط الدفع بالأيام
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # العلاقات
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
    purchase_invoices = relationship("PurchaseInvoice", back_populates="supplier")
    expenses = relationship("Expense", back_populates="supplier")
