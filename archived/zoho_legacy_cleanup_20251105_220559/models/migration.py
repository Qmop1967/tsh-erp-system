"""
Migration Models for TSH ERP System
نماذج الهجرة لنظام TSH ERP

Models for tracking migration progress, storing master data, and managing inventory.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.database import Base


class MigrationStatusEnum(enum.Enum):
    """حالات الهجرة"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"


class CurrencyEnum(enum.Enum):
    """العملات المدعومة"""
    IQD = "IQD"  # Iraqi Dinar
    USD = "USD"  # US Dollar
    RMB = "RMB"  # Chinese Yuan


class ItemCategoryEnum(enum.Enum):
    """فئات الأصناف"""
    ELECTRONICS = "ELECTRONICS"
    COMPUTERS = "COMPUTERS"
    ACCESSORIES = "ACCESSORIES"
    CABLES = "CABLES"
    STORAGE = "STORAGE"
    NETWORKING = "NETWORKING"
    MOBILE = "MOBILE"
    TOOLS = "TOOLS"
    OTHER = "OTHER"


# ====== Migration Tracking Models ======

class MigrationBatch(Base):
    """
    دفعة الهجرة - Migration Batch
    Tracks migration batches and their overall status
    """
    __tablename__ = "migration_batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_number = Column(String(50), unique=True, nullable=False, index=True)
    batch_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Status and timing
    status = Column(SQLEnum(MigrationStatusEnum), default=MigrationStatusEnum.PENDING, nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    
    # Statistics
    total_entities = Column(Integer, default=0)
    total_records = Column(Integer, default=0)
    successful_records = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)
    
    # Metadata
    source_system = Column(String(100))  # ZOHO_BOOKS, ZOHO_INVENTORY
    migration_config = Column(Text)  # JSON configuration
    error_log = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    migration_records = relationship("MigrationRecord", back_populates="batch")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<MigrationBatch {self.batch_number}: {self.batch_name}>"


class MigrationRecord(Base):
    """
    سجل الهجرة - Migration Record
    Tracks individual record migration status
    """
    __tablename__ = "migration_records"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("migration_batches.id"), nullable=False)
    
    # Source and target information
    entity_type = Column(String(100), nullable=False)  # ITEM, CUSTOMER, VENDOR, etc.
    source_id = Column(String(100), nullable=False)
    source_data = Column(Text)  # JSON of original data
    target_id = Column(Integer)  # ID in TSH ERP system
    
    # Status and timing  
    status = Column(SQLEnum(MigrationStatusEnum), default=MigrationStatusEnum.PENDING, nullable=False)
    processed_at = Column(DateTime)
    
    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    requires_manual_review = Column(Boolean, default=False)
    manual_review_notes = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    batch = relationship("MigrationBatch", back_populates="migration_records")
    
    # Indexes for better performance
    __table_args__ = (
        Index('idx_migration_record_entity_source', 'entity_type', 'source_id'),
        Index('idx_migration_record_status', 'status'),
        Index('idx_migration_record_batch_entity', 'batch_id', 'entity_type'),
    )
    
    def __repr__(self):
        return f"<MigrationRecord {self.entity_type}:{self.source_id} - {self.status.value}>"


# ====== Master Data Models ======

class ItemCategory(Base):
    """
    فئة الصنف - Item Category
    Categories for organizing items/products
    """
    __tablename__ = "item_categories"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name_ar = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=False)
    description_ar = Column(Text)
    description_en = Column(Text)
    
    # Hierarchy support
    parent_id = Column(Integer, ForeignKey("item_categories.id"))
    level = Column(Integer, default=1)
    sort_order = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent_category = relationship("ItemCategory", remote_side=[id])
    child_categories = relationship("ItemCategory", back_populates="parent_category")
    items = relationship("MigrationItem", back_populates="category")
    
    def __repr__(self):
        return f"<ItemCategory {self.code}: {self.name_en}>"


class MigrationItem(Base):
    """
    صنف - Migration Item/Product
    Main items/products table for migration
    """
    __tablename__ = "migration_items"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)  # SKU
    name_ar = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=False)
    description_ar = Column(Text)
    description_en = Column(Text)
    
    # Classification
    category_id = Column(Integer, ForeignKey("item_categories.id"))
    brand = Column(String(100))
    model = Column(String(100))
    
    # Specifications
    specifications = Column(Text)  # JSON format
    unit_of_measure = Column(String(50), default="PCS")
    
    # Pricing (base prices before price lists)
    cost_price_usd = Column(Numeric(15, 3), default=0.000)
    cost_price_iqd = Column(Numeric(15, 3), default=0.000)
    selling_price_usd = Column(Numeric(15, 3), default=0.000)
    selling_price_iqd = Column(Numeric(15, 3), default=0.000)
    
    # Inventory settings
    track_inventory = Column(Boolean, default=True)
    reorder_level = Column(Numeric(10, 3), default=0.000)
    reorder_quantity = Column(Numeric(10, 3), default=0.000)
    
    # Physical attributes
    weight = Column(Numeric(10, 3))
    dimensions = Column(String(100))  # L x W x H

    # Product image
    image_url = Column(String(500))  # URL or path to product image

    # Status and flags
    is_active = Column(Boolean, default=True, nullable=False)
    is_serialized = Column(Boolean, default=False)
    is_batch_tracked = Column(Boolean, default=False)
    
    # Zoho migration data
    zoho_item_id = Column(String(100), index=True)
    zoho_last_sync = Column(DateTime)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    category = relationship("ItemCategory", back_populates="items")
    creator = relationship("User", foreign_keys=[created_by])
    stock_records = relationship("MigrationStock", back_populates="item")
    price_list_items = relationship("PriceListItem", back_populates="item")
    
    # Indexes
    __table_args__ = (
        Index('idx_item_category', 'category_id'),
        Index('idx_item_brand_model', 'brand', 'model'),
        Index('idx_item_zoho', 'zoho_item_id'),
    )
    
    def __repr__(self):
        return f"<Item {self.code}: {self.name_en}>"


class PriceList(Base):
    """
    قائمة الأسعار - Price List
    Different price lists for different customer segments
    """
    __tablename__ = "price_lists"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name_ar = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=False)
    description_ar = Column(Text)
    description_en = Column(Text)
    
    # Price list configuration
    currency = Column(SQLEnum(CurrencyEnum), nullable=False)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Validity period
    effective_from = Column(DateTime)
    effective_to = Column(DateTime)
    
    # Zoho migration data
    zoho_price_list_id = Column(String(100), index=True)
    zoho_last_sync = Column(DateTime)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    price_list_items = relationship("PriceListItem", back_populates="price_list")
    customers = relationship("MigrationCustomer", back_populates="price_list")
    
    def __repr__(self):
        return f"<PriceList {self.code}: {self.name_en}>"


class PriceListItem(Base):
    """
    عنصر قائمة الأسعار - Price List Item
    Individual item prices in price lists
    """
    __tablename__ = "price_list_items"

    id = Column(Integer, primary_key=True, index=True)
    price_list_id = Column(Integer, ForeignKey("price_lists.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("migration_items.id"), nullable=False)
    
    # Pricing
    unit_price = Column(Numeric(15, 3), nullable=False)
    discount_percentage = Column(Numeric(5, 2), default=0.00)
    minimum_quantity = Column(Numeric(10, 3), default=1.000)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    price_list = relationship("PriceList", back_populates="price_list_items")
    item = relationship("MigrationItem", back_populates="price_list_items")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_price_list_item', 'price_list_id', 'item_id'),
    )
    
    def __repr__(self):
        return f"<PriceListItem {self.price_list_id}:{self.item_id} - {self.unit_price}>"


class MigrationCustomer(Base):
    """
    عميل - Migration Customer
    Customer master data for migration
    """
    __tablename__ = "migration_customers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name_ar = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=False)
    
    # Contact information
    email = Column(String(255), index=True)
    phone = Column(String(20))
    mobile = Column(String(20))
    
    # Address
    address_ar = Column(Text)
    address_en = Column(Text)
    city = Column(String(100))
    region = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100), default="Iraq")
    
    # Business information
    tax_number = Column(String(50))
    currency = Column(SQLEnum(CurrencyEnum), default=CurrencyEnum.IQD, nullable=False)
    credit_limit = Column(Numeric(15, 3), default=0.000)
    payment_terms = Column(String(100))
    
    # Price list assignment
    price_list_id = Column(Integer, ForeignKey("price_lists.id"))
    
    # Salesperson assignment
    salesperson_id = Column(Integer, ForeignKey("users.id"))
    assigned_region = Column(String(100))
    
    # Outstanding balance
    outstanding_receivable = Column(Numeric(15, 3), default=0.000)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Zoho migration data
    zoho_customer_id = Column(String(100), index=True)
    zoho_deposit_account = Column(String(255))  # For salesperson mapping
    zoho_last_sync = Column(DateTime)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    price_list = relationship("PriceList", back_populates="customers")
    salesperson = relationship("User", foreign_keys=[salesperson_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_customer_salesperson', 'salesperson_id'),
        Index('idx_customer_region', 'region'),
        Index('idx_customer_zoho', 'zoho_customer_id'),
    )
    
    def __repr__(self):
        return f"<Customer {self.code}: {self.name_en}>"


class MigrationVendor(Base):
    """
    مورد - Migration Vendor/Supplier
    Vendor master data for migration
    """
    __tablename__ = "migration_vendors"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name_ar = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=False)
    
    # Contact information
    email = Column(String(255), index=True)
    phone = Column(String(20))
    contact_person = Column(String(255))
    
    # Address
    address_ar = Column(Text)
    address_en = Column(Text)
    city = Column(String(100))
    country = Column(String(100))
    
    # Business information
    tax_number = Column(String(50))
    currency = Column(SQLEnum(CurrencyEnum), default=CurrencyEnum.USD, nullable=False)
    payment_terms = Column(String(100))
    
    # Outstanding balance
    outstanding_payable = Column(Numeric(15, 3), default=0.000)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Zoho migration data
    zoho_vendor_id = Column(String(100), index=True)
    zoho_last_sync = Column(DateTime)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_vendor_zoho', 'zoho_vendor_id'),
    )
    
    def __repr__(self):
        return f"<Vendor {self.code}: {self.name_en}>"


class MigrationStock(Base):
    """
    مخزون - Migration Stock/Inventory
    Stock levels and movements for migration
    """
    __tablename__ = "migration_stock"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("migration_items.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    
    # Stock quantities
    quantity_on_hand = Column(Numeric(12, 3), default=0.000, nullable=False)
    quantity_reserved = Column(Numeric(12, 3), default=0.000, nullable=False)
    quantity_available = Column(Numeric(12, 3), default=0.000, nullable=False)
    
    # Stock costs
    average_cost = Column(Numeric(15, 3), default=0.000)
    last_cost = Column(Numeric(15, 3), default=0.000)
    
    # Stock levels
    reorder_level = Column(Numeric(10, 3), default=0.000)
    reorder_quantity = Column(Numeric(10, 3), default=0.000)
    max_stock_level = Column(Numeric(10, 3))
    
    # Last movement tracking
    last_movement_date = Column(DateTime)
    last_movement_type = Column(String(50))
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    item = relationship("MigrationItem", back_populates="stock_records")
    warehouse = relationship("Warehouse")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_stock_item_warehouse', 'item_id', 'warehouse_id'),
        Index('idx_stock_item', 'item_id'),
        Index('idx_stock_warehouse', 'warehouse_id'),
    )
    
    def __repr__(self):
        return f"<Stock Item:{self.item_id} Warehouse:{self.warehouse_id} Qty:{self.quantity_on_hand}>"
