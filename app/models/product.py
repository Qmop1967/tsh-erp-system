from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Category(Base):
    """فئات المنتجات"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    name_ar = Column(String(100), nullable=True)  # Arabic name
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)  # Arabic description
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
    name = Column(String(200), nullable=False, index=True)  # English name
    name_ar = Column(String(200), nullable=True, index=True)  # Arabic name
    description = Column(Text, nullable=True)  # English description
    description_ar = Column(Text, nullable=True)  # Arabic description
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    cost_price = Column(Numeric(10, 2), nullable=True)  # سعر التكلفة
    unit_of_measure = Column(String(50), nullable=False)  # وحدة القياس (قطعة، كيلو، لتر...)
    min_stock_level = Column(Integer, default=0)  # الحد الأدنى للمخزون
    max_stock_level = Column(Integer, nullable=True)  # الحد الأقصى للمخزون
    reorder_point = Column(Integer, default=0)  # نقطة إعادة الطلب
    barcode = Column(String(100), unique=True, nullable=True)
    
    # Media fields
    image_url = Column(String(500), nullable=True)  # Primary image
    images = Column(JSON, nullable=True, default=list)  # Multiple images
    videos = Column(JSON, nullable=True, default=list)  # Video URLs
    
    # Additional fields
    weight = Column(Numeric(10, 3), nullable=True)  # Weight in kg
    dimensions = Column(JSON, nullable=True)  # {"length": 10, "width": 5, "height": 3}
    color = Column(String(50), nullable=True)
    size = Column(String(50), nullable=True)
    brand = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    
    is_active = Column(Boolean, default=True)
    is_trackable = Column(Boolean, default=True)  # هل يتم تتبع المخزون
    is_digital = Column(Boolean, default=False)  # منتج رقمي
    is_featured = Column(Boolean, default=False)  # منتج مميز

    # Stock tracking (synced from Zoho)
    actual_available_stock = Column(Integer, default=0, nullable=False)  # المخزون المتاح الفعلي من Zoho

    # SEO fields
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True, default=list)  # Search tags

    # Zoho integration
    zoho_item_id = Column(String(100), nullable=True, unique=True, index=True)  # Zoho Books Item ID
    cdn_image_url = Column(String(500), nullable=True)  # CDN image URL
    image_name = Column(String(500), nullable=True)  # Image filename
    image_type = Column(String(50), nullable=True)  # Image MIME type

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
    reviews = relationship("Review", back_populates="product")
