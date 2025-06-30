from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class SalesOrder(Base):
    """أوامر البيع"""
    __tablename__ = "sales_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    order_date = Column(Date, nullable=False, index=True)
    expected_delivery_date = Column(Date, nullable=True)
    actual_delivery_date = Column(Date, nullable=True)
    status = Column(String(50), default="DRAFT", index=True)  # DRAFT, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
    payment_status = Column(String(50), default="PENDING", index=True)  # PENDING, PARTIAL, PAID, OVERDUE
    payment_method = Column(String(50), nullable=True)  # CASH, CREDIT, BANK_TRANSFER, CHECK
    
    # المبالغ
    subtotal = Column(Numeric(12, 2), default=0)  # إجمالي قبل الخصم والضريبة
    discount_percentage = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(12, 2), default=0)
    tax_percentage = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(12, 2), default=0)
    total_amount = Column(Numeric(12, 2), default=0)  # الإجمالي النهائي
    paid_amount = Column(Numeric(12, 2), default=0)  # المبلغ المدفوع
    
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # العلاقات
    customer = relationship("Customer", back_populates="sales_orders")
    branch = relationship("Branch")
    warehouse = relationship("Warehouse")
    sales_items = relationship("SalesItem", back_populates="sales_order", cascade="all, delete-orphan")
    sales_invoices = relationship("SalesInvoice", back_populates="sales_order")
    created_by_user = relationship("User")

    @property
    def remaining_amount(self):
        """المبلغ المتبقي"""
        return self.total_amount - self.paid_amount

    @property
    def is_fully_paid(self):
        """هل تم دفع الفاتورة بالكامل"""
        return self.paid_amount >= self.total_amount


class SalesItem(Base):
    """عناصر أوامر البيع"""
    __tablename__ = "sales_items"

    id = Column(Integer, primary_key=True, index=True)
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Numeric(15, 3), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    discount_percentage = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    line_total = Column(Numeric(12, 2), nullable=False)  # السعر الإجمالي للسطر
    delivered_quantity = Column(Numeric(15, 3), default=0)  # الكمية المسلمة
    notes = Column(Text, nullable=True)

    # العلاقات
    sales_order = relationship("SalesOrder", back_populates="sales_items")
    product = relationship("Product", back_populates="sales_items")

    @property
    def remaining_quantity(self):
        """الكمية المتبقية للتسليم"""
        return self.quantity - self.delivered_quantity
