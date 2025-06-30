from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Category(Base):
    """فئات المنتجات"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # العلاقات
    parent = relationship("Category", remote_side=[id], back_populates="subcategories")
    subcategories = relationship("Category", back_populates="parent")
    products = relationship("Product", back_populates="category")


class Product(Base):
    """المنتجات"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)  # رمز المنتج
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    cost_price = Column(Numeric(10, 2), nullable=True)  # سعر التكلفة
    unit_of_measure = Column(String(50), nullable=False)  # وحدة القياس (قطعة، كيلو، لتر...)
    min_stock_level = Column(Integer, default=0)  # الحد الأدنى للمخزون
    max_stock_level = Column(Integer, nullable=True)  # الحد الأقصى للمخزون
    reorder_point = Column(Integer, default=0)  # نقطة إعادة الطلب
    barcode = Column(String(100), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    is_trackable = Column(Boolean, default=True)  # هل يتم تتبع المخزون
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # العلاقات
    category = relationship("Category", back_populates="products")
    inventory_items = relationship("InventoryItem", back_populates="product")
    sales_items = relationship("SalesItem", back_populates="product")
    purchase_items = relationship("PurchaseItem", back_populates="product")
    sales_invoice_items = relationship("SalesInvoiceItem", back_populates="product")
    purchase_invoice_items = relationship("PurchaseInvoiceItem", back_populates="product")
    expense_items = relationship("ExpenseItem", back_populates="product")
