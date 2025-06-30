"""
Migration Schemas for TSH ERP System
مخططات الهجرة لنظام TSH ERP

Pydantic schemas for migration data validation and API responses.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum


class MigrationStatusEnum(str, Enum):
    """حالات الهجرة"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"


class CurrencyEnum(str, Enum):
    """العملات المدعومة"""
    IQD = "IQD"
    USD = "USD"
    RMB = "RMB"


# ====== Migration Batch Schemas ======

class MigrationBatchCreate(BaseModel):
    """إنشاء دفعة هجرة"""
    batch_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    source_system: str = Field(..., min_length=1, max_length=100)
    migration_config: Optional[Dict[str, Any]] = None


class MigrationBatchUpdate(BaseModel):
    """تحديث دفعة هجرة"""
    batch_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[MigrationStatusEnum] = None
    error_log: Optional[str] = None


class MigrationBatch(BaseModel):
    """دفعة الهجرة"""
    id: int
    batch_number: str
    batch_name: str
    description: Optional[str]
    status: MigrationStatusEnum
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    total_entities: Optional[int] = 0
    total_records: Optional[int] = 0
    successful_records: Optional[int] = 0
    failed_records: Optional[int] = 0
    source_system: Optional[str]
    migration_config: Optional[str]
    error_log: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]

    class Config:
        from_attributes = True


# ====== Migration Record Schemas ======

class MigrationRecordCreate(BaseModel):
    """إنشاء سجل هجرة"""
    batch_id: int
    entity_type: str = Field(..., min_length=1, max_length=100)
    source_id: str = Field(..., min_length=1, max_length=100)
    source_data: Optional[Dict[str, Any]] = None


class MigrationRecordUpdate(BaseModel):
    """تحديث سجل هجرة"""
    status: Optional[MigrationStatusEnum] = None
    target_id: Optional[int] = None
    error_message: Optional[str] = None
    requires_manual_review: Optional[bool] = None
    manual_review_notes: Optional[str] = None


class MigrationRecord(BaseModel):
    """سجل الهجرة"""
    id: int
    batch_id: int
    entity_type: str
    source_id: str
    source_data: Optional[str]
    target_id: Optional[int]
    status: MigrationStatusEnum
    processed_at: Optional[datetime]
    error_message: Optional[str]
    retry_count: Optional[int] = 0
    requires_manual_review: Optional[bool] = False
    manual_review_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ====== Item Migration Schemas ======

class ItemCategoryCreate(BaseModel):
    """إنشاء فئة صنف"""
    code: str = Field(..., min_length=1, max_length=50)
    name_ar: str = Field(..., min_length=1, max_length=255)
    name_en: str = Field(..., min_length=1, max_length=255)
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = 0
    is_active: bool = True


class ItemCategoryUpdate(BaseModel):
    """تحديث فئة صنف"""
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name_ar: Optional[str] = Field(None, min_length=1, max_length=255)
    name_en: Optional[str] = Field(None, min_length=1, max_length=255)
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class ItemCategory(BaseModel):
    """فئة الصنف"""
    id: int
    code: str
    name_ar: str
    name_en: str
    description_ar: Optional[str]
    description_en: Optional[str]
    parent_id: Optional[int]
    level: Optional[int] = 1
    sort_order: Optional[int] = 0
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ItemCreate(BaseModel):
    """إنشاء صنف"""
    code: str = Field(..., min_length=1, max_length=100)
    name_ar: str = Field(..., min_length=1, max_length=255)
    name_en: str = Field(..., min_length=1, max_length=255)
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    specifications: Optional[Dict[str, Any]] = None
    unit_of_measure: str = Field(default="PCS", max_length=50)
    cost_price_usd: Optional[Decimal] = Field(default=0.000, ge=0)
    cost_price_iqd: Optional[Decimal] = Field(default=0.000, ge=0)
    selling_price_usd: Optional[Decimal] = Field(default=0.000, ge=0)
    selling_price_iqd: Optional[Decimal] = Field(default=0.000, ge=0)
    track_inventory: bool = True
    reorder_level: Optional[Decimal] = Field(default=0.000, ge=0)
    reorder_quantity: Optional[Decimal] = Field(default=0.000, ge=0)
    weight: Optional[Decimal] = Field(None, ge=0)
    dimensions: Optional[str] = Field(None, max_length=100)
    is_active: bool = True
    is_serialized: bool = False
    is_batch_tracked: bool = False
    zoho_item_id: Optional[str] = Field(None, max_length=100)


class ItemUpdate(BaseModel):
    """تحديث صنف"""
    code: Optional[str] = Field(None, min_length=1, max_length=100)
    name_ar: Optional[str] = Field(None, min_length=1, max_length=255)
    name_en: Optional[str] = Field(None, min_length=1, max_length=255)
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    specifications: Optional[Dict[str, Any]] = None
    unit_of_measure: Optional[str] = Field(None, max_length=50)
    cost_price_usd: Optional[Decimal] = Field(None, ge=0)
    cost_price_iqd: Optional[Decimal] = Field(None, ge=0)
    selling_price_usd: Optional[Decimal] = Field(None, ge=0)
    selling_price_iqd: Optional[Decimal] = Field(None, ge=0)
    track_inventory: Optional[bool] = None
    reorder_level: Optional[Decimal] = Field(None, ge=0)
    reorder_quantity: Optional[Decimal] = Field(None, ge=0)
    weight: Optional[Decimal] = Field(None, ge=0)
    dimensions: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    is_serialized: Optional[bool] = None
    is_batch_tracked: Optional[bool] = None


class Item(BaseModel):
    """الصنف"""
    id: int
    code: str
    name_ar: str
    name_en: str
    description_ar: Optional[str]
    description_en: Optional[str]
    category_id: Optional[int]
    brand: Optional[str]
    model: Optional[str]
    specifications: Optional[str]
    unit_of_measure: str
    cost_price_usd: Decimal
    cost_price_iqd: Decimal
    selling_price_usd: Decimal
    selling_price_iqd: Decimal
    track_inventory: bool
    reorder_level: Decimal
    reorder_quantity: Decimal
    weight: Optional[Decimal]
    dimensions: Optional[str]
    is_active: bool
    is_serialized: bool
    is_batch_tracked: bool
    zoho_item_id: Optional[str]
    zoho_last_sync: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]

    class Config:
        from_attributes = True


# ====== Price List Schemas ======

class PriceListCreate(BaseModel):
    """إنشاء قائمة أسعار"""
    code: str = Field(..., min_length=1, max_length=50)
    name_ar: str = Field(..., min_length=1, max_length=255)
    name_en: str = Field(..., min_length=1, max_length=255)
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    currency: CurrencyEnum
    is_default: bool = False
    is_active: bool = True
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    zoho_price_list_id: Optional[str] = Field(None, max_length=100)


class PriceListUpdate(BaseModel):
    """تحديث قائمة أسعار"""
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name_ar: Optional[str] = Field(None, min_length=1, max_length=255)
    name_en: Optional[str] = Field(None, min_length=1, max_length=255)
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    currency: Optional[CurrencyEnum] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None


class PriceList(BaseModel):
    """قائمة الأسعار"""
    id: int
    code: str
    name_ar: str
    name_en: str
    description_ar: Optional[str]
    description_en: Optional[str]
    currency: CurrencyEnum
    is_default: bool
    is_active: bool
    effective_from: Optional[datetime]
    effective_to: Optional[datetime]
    zoho_price_list_id: Optional[str]
    zoho_last_sync: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]

    class Config:
        from_attributes = True


class PriceListItemCreate(BaseModel):
    """إنشاء عنصر قائمة أسعار"""
    price_list_id: int
    item_id: int
    unit_price: Decimal = Field(..., ge=0)
    discount_percentage: Optional[Decimal] = Field(default=0.00, ge=0, le=100)
    minimum_quantity: Optional[Decimal] = Field(default=1.000, ge=0)
    is_active: bool = True


class PriceListItemUpdate(BaseModel):
    """تحديث عنصر قائمة أسعار"""
    unit_price: Optional[Decimal] = Field(None, ge=0)
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    minimum_quantity: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None


class PriceListItem(BaseModel):
    """عنصر قائمة الأسعار"""
    id: int
    price_list_id: int
    item_id: int
    unit_price: Decimal
    discount_percentage: Decimal
    minimum_quantity: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ====== Customer Schemas ======

class CustomerCreate(BaseModel):
    """إنشاء عميل"""
    code: str = Field(..., min_length=1, max_length=50)
    name_ar: str = Field(..., min_length=1, max_length=255)
    name_en: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    address_ar: Optional[str] = None
    address_en: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: str = Field(default="Iraq", max_length=100)
    tax_number: Optional[str] = Field(None, max_length=50)
    currency: CurrencyEnum = CurrencyEnum.IQD
    credit_limit: Optional[Decimal] = Field(default=0.000, ge=0)
    payment_terms: Optional[str] = Field(None, max_length=100)
    price_list_id: Optional[int] = None
    salesperson_id: Optional[int] = None
    assigned_region: Optional[str] = Field(None, max_length=100)
    outstanding_receivable: Optional[Decimal] = Field(default=0.000, ge=0)
    is_active: bool = True
    zoho_customer_id: Optional[str] = Field(None, max_length=100)
    zoho_deposit_account: Optional[str] = Field(None, max_length=255)


class CustomerUpdate(BaseModel):
    """تحديث عميل"""
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name_ar: Optional[str] = Field(None, min_length=1, max_length=255)
    name_en: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    address_ar: Optional[str] = None
    address_en: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    tax_number: Optional[str] = Field(None, max_length=50)
    currency: Optional[CurrencyEnum] = None
    credit_limit: Optional[Decimal] = Field(None, ge=0)
    payment_terms: Optional[str] = Field(None, max_length=100)
    price_list_id: Optional[int] = None
    salesperson_id: Optional[int] = None
    assigned_region: Optional[str] = Field(None, max_length=100)
    outstanding_receivable: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None


class Customer(BaseModel):
    """العميل"""
    id: int
    code: str
    name_ar: str
    name_en: str
    email: Optional[str]
    phone: Optional[str]
    mobile: Optional[str]
    address_ar: Optional[str]
    address_en: Optional[str]
    city: Optional[str]
    region: Optional[str]
    postal_code: Optional[str]
    country: str
    tax_number: Optional[str]
    currency: CurrencyEnum
    credit_limit: Decimal
    payment_terms: Optional[str]
    price_list_id: Optional[int]
    salesperson_id: Optional[int]
    assigned_region: Optional[str]
    outstanding_receivable: Decimal
    is_active: bool
    zoho_customer_id: Optional[str]
    zoho_deposit_account: Optional[str]
    zoho_last_sync: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ====== Vendor Schemas ======

class VendorCreate(BaseModel):
    """إنشاء مورد"""
    code: str = Field(..., min_length=1, max_length=50)
    name_ar: str = Field(..., min_length=1, max_length=255)
    name_en: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    contact_person: Optional[str] = Field(None, max_length=255)
    address_ar: Optional[str] = None
    address_en: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    tax_number: Optional[str] = Field(None, max_length=50)
    currency: CurrencyEnum = CurrencyEnum.USD
    payment_terms: Optional[str] = Field(None, max_length=100)
    outstanding_payable: Optional[Decimal] = Field(default=0.000, ge=0)
    is_active: bool = True
    zoho_vendor_id: Optional[str] = Field(None, max_length=100)


class VendorUpdate(BaseModel):
    """تحديث مورد"""
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name_ar: Optional[str] = Field(None, min_length=1, max_length=255)
    name_en: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    contact_person: Optional[str] = Field(None, max_length=255)
    address_ar: Optional[str] = None
    address_en: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    tax_number: Optional[str] = Field(None, max_length=50)
    currency: Optional[CurrencyEnum] = None
    payment_terms: Optional[str] = Field(None, max_length=100)
    outstanding_payable: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None


class Vendor(BaseModel):
    """المورد"""
    id: int
    code: str
    name_ar: str
    name_en: str
    email: Optional[str]
    phone: Optional[str]
    contact_person: Optional[str]
    address_ar: Optional[str]
    address_en: Optional[str]
    city: Optional[str]
    country: Optional[str]
    tax_number: Optional[str]
    currency: CurrencyEnum
    payment_terms: Optional[str]
    outstanding_payable: Decimal
    is_active: bool
    zoho_vendor_id: Optional[str]
    zoho_last_sync: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ====== Stock Schemas ======

class StockCreate(BaseModel):
    """إنشاء مخزون"""
    item_id: int
    warehouse_id: int
    quantity_on_hand: Decimal = Field(..., ge=0)
    quantity_reserved: Optional[Decimal] = Field(default=0.000, ge=0)
    quantity_available: Optional[Decimal] = Field(default=0.000, ge=0)
    average_cost: Optional[Decimal] = Field(default=0.000, ge=0)
    last_cost: Optional[Decimal] = Field(default=0.000, ge=0)
    reorder_level: Optional[Decimal] = Field(default=0.000, ge=0)
    reorder_quantity: Optional[Decimal] = Field(default=0.000, ge=0)
    max_stock_level: Optional[Decimal] = Field(None, ge=0)


class StockUpdate(BaseModel):
    """تحديث مخزون"""
    quantity_on_hand: Optional[Decimal] = Field(None, ge=0)
    quantity_reserved: Optional[Decimal] = Field(None, ge=0)
    quantity_available: Optional[Decimal] = Field(None, ge=0)
    average_cost: Optional[Decimal] = Field(None, ge=0)
    last_cost: Optional[Decimal] = Field(None, ge=0)
    reorder_level: Optional[Decimal] = Field(None, ge=0)
    reorder_quantity: Optional[Decimal] = Field(None, ge=0)
    max_stock_level: Optional[Decimal] = Field(None, ge=0)


class Stock(BaseModel):
    """المخزون"""
    id: int
    item_id: int
    warehouse_id: int
    quantity_on_hand: Decimal
    quantity_reserved: Decimal
    quantity_available: Decimal
    average_cost: Decimal
    last_cost: Decimal
    reorder_level: Decimal
    reorder_quantity: Decimal
    max_stock_level: Optional[Decimal]
    last_movement_date: Optional[datetime]
    last_movement_type: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ====== Migration Summary Schemas ======

class MigrationSummary(BaseModel):
    """ملخص الهجرة"""
    total_batches: int
    total_records: int
    successful_records: int
    failed_records: int
    success_rate: str
    
    class Config:
        from_attributes = True


class MigrationBatchSummary(BaseModel):
    """ملخص دفعة الهجرة"""
    id: int
    batch_number: str
    batch_name: str
    status: MigrationStatusEnum
    total_records: int
    successful_records: int
    failed_records: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    
    class Config:
        from_attributes = True


class FailedMigrationRecord(BaseModel):
    """سجل هجرة فاشل"""
    id: int
    entity_type: str
    source_id: str
    error_message: Optional[str]
    source_data: Optional[Dict[str, Any]]
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class SalespersonCustomerMapping(BaseModel):
    """خريطة ربط مندوب المبيعات بالعملاء"""
    salesperson_name: str
    customers: List[Dict[str, Any]]
    total_customers: int
    total_outstanding: Decimal


class MigrationReport(BaseModel):
    """تقرير الهجرة"""
    summary: MigrationSummary
    batches: List[MigrationBatchSummary]
    failed_records: Optional[List[FailedMigrationRecord]] = None
    salesperson_mapping: Optional[Dict[str, Any]] = None


# ====== Zoho Configuration Schemas ======

class ZohoConfigCreate(BaseModel):
    """إعدادات Zoho API"""
    organization_id: str = Field(..., min_length=1)
    access_token: str = Field(..., min_length=1)
    refresh_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    books_api_base: Optional[str] = "https://books.zoho.com/api/v3"
    inventory_api_base: Optional[str] = "https://inventory.zoho.com/api/v1"


class ZohoDataExtractRequest(BaseModel):
    """طلب استخراج بيانات Zoho"""
    data_type: str = Field(..., pattern="^(items|customers|vendors|price_lists|stock)$")
    page_size: Optional[int] = Field(200, ge=1, le=200)
    filters: Optional[Dict[str, Any]] = None


class ZohoMigrationRequest(BaseModel):
    """طلب هجرة بيانات Zoho"""
    batch_id: int = Field(..., gt=0)
    data_type: str = Field(..., pattern="^(items|customers|vendors|price_lists|stock)$")
    zoho_config: ZohoConfigCreate
    dry_run: Optional[bool] = False
    chunk_size: Optional[int] = Field(100, ge=1, le=500)


class ZohoAsyncExtractRequest(BaseModel):
    """طلب استخراج بيانات Zoho غير متزامن"""
    data_type: str = Field(..., pattern="^(items|customers|vendors|price_lists|stock)$")
    zoho_config: ZohoConfigCreate
    page_size: Optional[int] = Field(200, ge=1, le=200)
    filters: Optional[Dict[str, Any]] = None
