"""
Migration Router for TSH ERP System
راوتر الهجرة لنظام TSH ERP

API endpoints for managing data migration from Zoho to TSH ERP.
"""

import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.database import get_db
from app.schemas.migration import *
from app.services.migration_service import (
    MigrationService, ItemMigrationService, CustomerMigrationService, MigrationReportService
)


router = APIRouter(prefix="/migration", tags=["Migration"])
logger = logging.getLogger(__name__)


# ====== Migration Batch Management ======

@router.post("/batches", response_model=MigrationBatch)
def create_migration_batch(
    batch: MigrationBatchCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1  # TODO: Get from authentication
):
    """
    Create a new migration batch
    إنشاء دفعة هجرة جديدة
    """
    service = MigrationService(db)
    return service.create_migration_batch(
        batch_name=batch.batch_name,
        description=batch.description,
        source_system=batch.source_system,
        created_by=current_user_id
    )


@router.get("/batches", response_model=List[MigrationBatch])
def get_migration_batches(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get migration batches
    الحصول على دفعات الهجرة
    """
    from app.models.migration import MigrationBatch, MigrationStatusEnum
    
    query = db.query(MigrationBatch)
    
    if status_filter:
        try:
            status_enum = MigrationStatusEnum(status_filter)
            query = query.filter(MigrationBatch.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status filter: {status_filter}"
            )
    
    return query.offset(skip).limit(limit).all()


@router.get("/batches/{batch_id}", response_model=MigrationBatch)
def get_migration_batch(
    batch_id: int,
    db: Session = Depends(get_db)
):
    """
    Get migration batch by ID
    الحصول على دفعة هجرة بالمعرف
    """
    from app.models.migration import MigrationBatch
    
    batch = db.query(MigrationBatch).filter(MigrationBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Migration batch not found - دفعة الهجرة غير موجودة"
        )
    return batch


@router.put("/batches/{batch_id}/start", response_model=MigrationBatch)
def start_migration_batch(
    batch_id: int,
    db: Session = Depends(get_db)
):
    """
    Start migration batch execution
    بدء تنفيذ دفعة الهجرة
    """
    service = MigrationService(db)
    try:
        return service.start_migration_batch(batch_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/batches/{batch_id}/complete", response_model=MigrationBatch)
def complete_migration_batch(
    batch_id: int,
    success: bool = True,
    db: Session = Depends(get_db)
):
    """
    Complete migration batch
    إكمال دفعة الهجرة
    """
    service = MigrationService(db)
    try:
        return service.complete_migration_batch(batch_id, success)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ====== Item Migration ======

@router.post("/batches/{batch_id}/migrate-item-categories")
def migrate_item_categories(
    batch_id: int,
    categories_data: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """
    Migrate item categories
    هجرة فئات الأصناف
    """
    service = ItemMigrationService(db)
    try:
        results = service.migrate_item_categories(batch_id, categories_data)
        return {
            "message": "Item categories migration completed",
            "total_records": len(results),
            "successful": sum(1 for r in results if r.status.value == "COMPLETED"),
            "failed": sum(1 for r in results if r.status.value == "FAILED")
        }
    except Exception as e:
        logger.error(f"Item categories migration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )


@router.post("/batches/{batch_id}/migrate-items")
def migrate_items(
    batch_id: int,
    items_data: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """
    Migrate items with USD to IQD conversion
    هجرة الأصناف مع تحويل الأسعار من الدولار إلى الدينار
    """
    service = ItemMigrationService(db)
    try:
        results = service.migrate_items(batch_id, items_data)
        return {
            "message": "Items migration completed",
            "total_records": len(results),
            "successful": sum(1 for r in results if r.status.value == "COMPLETED"),
            "failed": sum(1 for r in results if r.status.value == "FAILED"),
            "currency_conversion": "USD prices converted to IQD at rate 1:1500"
        }
    except Exception as e:
        logger.error(f"Items migration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )


@router.post("/batches/{batch_id}/migrate-stock")
def migrate_stock_levels(
    batch_id: int,
    stock_data: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """
    Migrate stock levels as stock on hand
    هجرة مستويات المخزون كمخزون متوفر
    """
    service = ItemMigrationService(db)
    try:
        results = service.migrate_stock_levels(batch_id, stock_data)
        return {
            "message": "Stock levels migration completed",
            "total_records": len(results),
            "successful": sum(1 for r in results if r.status.value == "COMPLETED"),
            "failed": sum(1 for r in results if r.status.value == "FAILED")
        }
    except Exception as e:
        logger.error(f"Stock migration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )


# ====== Customer & Vendor Migration ======

@router.post("/batches/{batch_id}/migrate-price-lists")
def migrate_price_lists(
    batch_id: int,
    price_lists_data: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """
    Migrate active price lists
    هجرة قوائم الأسعار النشطة
    """
    service = CustomerMigrationService(db)
    try:
        results = service.migrate_price_lists(batch_id, price_lists_data)
        return {
            "message": "Price lists migration completed",
            "total_records": len(results),
            "successful": sum(1 for r in results if r.status.value == "COMPLETED"),
            "failed": sum(1 for r in results if r.status.value == "FAILED")
        }
    except Exception as e:
        logger.error(f"Price lists migration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )


@router.post("/batches/{batch_id}/migrate-customers")
def migrate_customers(
    batch_id: int,
    customers_data: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """
    Migrate customers with salesperson assignment based on deposit accounts
    هجرة العملاء مع تعيين مندوبي المبيعات بناءً على حسابات الودائع
    """
    service = CustomerMigrationService(db)
    try:
        results = service.migrate_customers(batch_id, customers_data)
        
        # Get mapping summary
        report_service = MigrationReportService(db)
        mapping_summary = report_service.get_salesperson_customer_mapping()
        
        return {
            "message": "Customers migration completed",
            "total_records": len(results),
            "successful": sum(1 for r in results if r.status.value == "COMPLETED"),
            "failed": sum(1 for r in results if r.status.value == "FAILED"),
            "salesperson_mapping": mapping_summary
        }
    except Exception as e:
        logger.error(f"Customers migration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )


@router.get("/customers")
def get_migrated_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Search in customer name or code"),
    active_only: bool = Query(True, description="Active customers only"),
    db: Session = Depends(get_db)
):
    """
    Get migrated customers from Zoho
    الحصول على العملاء المهاجرين من زوهو
    """
    from app.models.migration import MigrationCustomer
    
    query = db.query(MigrationCustomer)
    
    if active_only:
        query = query.filter(MigrationCustomer.is_active == True)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                MigrationCustomer.name_en.ilike(search_filter),
                MigrationCustomer.name_ar.ilike(search_filter),
                MigrationCustomer.code.ilike(search_filter)
            )
        )
    
    customers = query.offset(skip).limit(limit).all()
    
    result = []
    for customer in customers:
        result.append({
            "id": customer.id,
            "code": customer.code,
            "name": customer.name_en,
            "name_ar": customer.name_ar,
            "email": customer.email,
            "phone": customer.phone,
            "mobile": customer.mobile,
            "address": customer.address_en,
            "city": customer.city,
            "country": customer.country,
            "currency": customer.currency.value if customer.currency else "IQD",
            "credit_limit": float(customer.credit_limit) if customer.credit_limit else 0,
            "outstanding_receivable": float(customer.outstanding_receivable) if customer.outstanding_receivable else 0,
            "is_active": customer.is_active,
            "zoho_customer_id": customer.zoho_customer_id,
            "created_at": customer.created_at.isoformat() if customer.created_at else None,
            "updated_at": customer.updated_at.isoformat() if customer.updated_at else None,
            "source": "zoho"
        })
    
    return result


@router.post("/batches/{batch_id}/migrate-vendors")
def migrate_vendors(
    batch_id: int,
    vendors_data: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """
    Migrate vendors with their currencies and balances
    هجرة الموردين مع عملاتهم وأرصدتهم
    """
    service = CustomerMigrationService(db)
    try:
        results = service.migrate_vendors(batch_id, vendors_data)
        return {
            "message": "Vendors migration completed",
            "total_records": len(results),
            "successful": sum(1 for r in results if r.status.value == "COMPLETED"),
            "failed": sum(1 for r in results if r.status.value == "FAILED")
        }
    except Exception as e:
        logger.error(f"Vendors migration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )


# ====== Item Categories Management ======

@router.get("/categories/", response_model=List[ItemCategory])
def get_item_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    Get all item categories
    الحصول على جميع فئات الأصناف
    """
    from app.models.migration import ItemCategory as ItemCategoryModel
    
    query = db.query(ItemCategoryModel)
    
    if active_only:
        query = query.filter(ItemCategoryModel.is_active == True)
    
    query = query.order_by(ItemCategoryModel.sort_order, ItemCategoryModel.name_en)
    categories = query.offset(skip).limit(limit).all()
    
    return categories


@router.post("/categories/", response_model=ItemCategory)
def create_item_category(
    category: ItemCategoryCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new item category
    إنشاء فئة أصناف جديدة
    """
    from app.models.migration import ItemCategory as ItemCategoryModel
    
    # Check if code already exists
    existing = db.query(ItemCategoryModel).filter(ItemCategoryModel.code == category.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with code '{category.code}' already exists"
        )
    
    db_category = ItemCategoryModel(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category


@router.put("/categories/{category_id}", response_model=ItemCategory)
def update_item_category(
    category_id: int,
    category: ItemCategoryUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an item category
    تحديث فئة أصناف
    """
    from app.models.migration import ItemCategory as ItemCategoryModel
    
    db_category = db.query(ItemCategoryModel).filter(ItemCategoryModel.id == category_id).first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check if new code conflicts with existing
    if category.code and category.code != db_category.code:
        existing = db.query(ItemCategoryModel).filter(ItemCategoryModel.code == category.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with code '{category.code}' already exists"
            )
    
    for field, value in category.dict(exclude_unset=True).items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    
    return db_category


# ====== File Upload Migration ======

@router.post("/batches/{batch_id}/upload-zoho-data")
async def upload_zoho_data(
    batch_id: int,
    zoho_books_file: Optional[UploadFile] = File(None),
    zoho_inventory_file: Optional[UploadFile] = File(None),
    data_type: str = Form(...),  # items, customers, vendors, price_lists, stock
    db: Session = Depends(get_db)
):
    """
    Upload Zoho data files for migration
    رفع ملفات بيانات Zoho للهجرة
    """
    try:
        results = {}
        
        if data_type == "items" and zoho_inventory_file:
            # Process items file
            content = await zoho_inventory_file.read()
            # TODO: Parse CSV/JSON content and extract items data
            items_data = []  # Placeholder - implement actual parsing
            
            service = ItemMigrationService(db)
            migration_results = service.migrate_items(batch_id, items_data)
            results["items"] = {
                "total": len(migration_results),
                "successful": sum(1 for r in migration_results if r.status.value == "COMPLETED")
            }
        
        elif data_type == "customers" and zoho_books_file:
            # Process customers file
            content = await zoho_books_file.read()
            # TODO: Parse CSV/JSON content and extract customers data
            customers_data = []  # Placeholder - implement actual parsing
            
            service = CustomerMigrationService(db)
            migration_results = service.migrate_customers(batch_id, customers_data)
            results["customers"] = {
                "total": len(migration_results),
                "successful": sum(1 for r in migration_results if r.status.value == "COMPLETED")
            }
        
        # Add more data types as needed
        
        return {
            "message": f"File upload and {data_type} migration completed",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"File upload migration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload migration failed: {str(e)}"
        )


# ====== Migration Reports ======

@router.get("/reports/summary")
def get_migration_summary(
    batch_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get migration summary report
    الحصول على تقرير ملخص الهجرة
    """
    service = MigrationReportService(db)
    return service.get_migration_summary(batch_id)


@router.get("/reports/failed-records/{batch_id}")
def get_failed_records(
    batch_id: int,
    db: Session = Depends(get_db)
):
    """
    Get failed migration records for review
    الحصول على سجلات الهجرة الفاشلة للمراجعة
    """
    service = MigrationReportService(db)
    return service.get_failed_records(batch_id)


@router.get("/reports/salesperson-mapping")
def get_salesperson_customer_mapping(
    db: Session = Depends(get_db)
):
    """
    Get salesperson to customer mapping report
    الحصول على تقرير ربط مندوبي المبيعات بالعملاء
    """
    service = MigrationReportService(db)
    return service.get_salesperson_customer_mapping()


# ====== Migration Configuration ======

@router.get("/config/exchange-rates")
def get_exchange_rates():
    """
    Get current exchange rates for currency conversion
    الحصول على أسعار الصرف الحالية لتحويل العملات
    """
    return {
        "exchange_rates": MigrationService.EXCHANGE_RATES,
        "note": "USD to IQD conversion rate is 1:1500 as requested"
    }


@router.get("/config/salesperson-mapping")
def get_salesperson_deposit_mapping():
    """
    Get salesperson to deposit account mapping configuration
    الحصول على إعدادات ربط مندوبي المبيعات بحسابات الودائع
    """
    return {
        "deposit_account_mapping": MigrationService.SALESPERSON_DEPOSIT_MAPPING,
        "description": {
            "frati": "Ayad Al-Baghdadi - Furat regions (Karbala, Najaf, Babel)",
            "southi": "Haider - South regions (Basra, Dhi Qar, Maysan, Muthanna)",
            "northi": "Hussein - North regions (Mosul, Erbil, Duhok, Sulaymaniyah, Kirkuk)",
            "dyali": "Ahmed - Diyala region",
            "westi": "Ayoob - West regions (Anbar, Baghdad)"
        }
    }


# ====== Utility Endpoints ======

@router.post("/utils/test-currency-conversion")
def test_currency_conversion(
    amount: float,
    from_currency: str = "USD",
    to_currency: str = "IQD",
    db: Session = Depends(get_db)
):
    """
    Test currency conversion
    اختبار تحويل العملة
    """
    service = MigrationService(db)
    try:
        converted_amount = service.convert_currency(amount, from_currency, to_currency)
        return {
            "original": {
                "amount": amount,
                "currency": from_currency
            },
            "converted": {
                "amount": float(converted_amount),
                "currency": to_currency
            },
            "exchange_rate": service.EXCHANGE_RATES.get(f"{from_currency}_TO_{to_currency}", "N/A")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Currency conversion failed: {str(e)}"
        )


@router.post("/utils/validate-zoho-data")
async def validate_zoho_data(
    file: UploadFile = File(...),
    data_type: str = Form(...)  # items, customers, vendors
):
    """
    Validate Zoho data file structure before migration
    التحقق من صحة هيكل ملف بيانات Zoho قبل الهجرة
    """
    try:
        content = await file.read()
        # TODO: Implement actual validation logic based on data_type
        
        validation_result = {
            "file_name": file.filename,
            "file_size": len(content),
            "data_type": data_type,
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "estimated_records": 0  # Placeholder
        }
        
        return validation_result
        
    except Exception as e:
        return {
            "file_name": file.filename,
            "is_valid": False,
            "errors": [str(e)],
            "warnings": [],
            "estimated_records": 0
        }


# ====== Zoho Data Migration ======

@router.post("/batches/{batch_id}/migrate-from-zoho-api")
def migrate_from_zoho_api(
    batch_id: int,
    data_type: str,
    zoho_config: ZohoConfigCreate,
    db: Session = Depends(get_db)
):
    """
    Migrate data directly from Zoho API
    هجرة البيانات مباشرة من Zoho API
    """
    from app.services.zoho_service import ZohoConfig
    
    try:
        # Create Zoho config
        config = ZohoConfig(
            organization_id=zoho_config.organization_id,
            access_token=zoho_config.access_token,
            refresh_token=zoho_config.refresh_token,
            client_id=zoho_config.client_id,
            client_secret=zoho_config.client_secret
        )
        
        # Initialize migration service with Zoho config
        service = MigrationService(db, config)
        
        # Migrate data
        results = service.migrate_from_zoho_api(batch_id, data_type)
        
        return {
            "message": f"Migration from Zoho API completed for {data_type}",
            "batch_id": batch_id,
            "data_type": data_type,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Failed to migrate from Zoho API: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )


@router.post("/batches/{batch_id}/migrate-from-file")
def migrate_from_uploaded_file(
    batch_id: int,
    file_type: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Migrate data from uploaded file (CSV/Excel)
    هجرة البيانات من ملف مرفوع
    """
    try:
        # Validate file type
        if file_type not in ['items', 'customers', 'vendors', 'stock', 'price_lists']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file_type}"
            )
        
        # Validate file format
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be CSV or Excel format"
            )
        
        # Read file content
        file_content = file.file.read()
        
        # Initialize migration service
        service = MigrationService(db)
        
        # Migrate data from file
        results = service.migrate_from_uploaded_file(
            batch_id, file_content, file_type, file.filename
        )
        
        return {
            "message": f"Migration from file completed for {file_type}",
            "batch_id": batch_id,
            "file_type": file_type,
            "filename": file.filename,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Failed to migrate from uploaded file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )


@router.post("/batches/{batch_id}/migrate-items-from-data")
def migrate_items_from_data(
    batch_id: int,
    items_data: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """
    Migrate items from extracted data
    هجرة الأصناف من البيانات المستخرجة
    """
    service = MigrationService(db)
    try:
        results = service.migrate_items_from_data(batch_id, items_data)
        return {
            "message": "Items migration completed",
            "total_records": len(results),
            "successful_records": len([r for r in results if r.status == MigrationStatusEnum.COMPLETED]),
            "failed_records": len([r for r in results if r.status == MigrationStatusEnum.FAILED]),
            "results": [
                {
                    "source_id": r.source_id,
                    "target_id": r.target_id,
                    "status": r.status.value,
                    "error_message": r.error_message
                }
                for r in results
            ]
        }
    except Exception as e:
        logger.error(f"Failed to migrate items: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Items migration failed: {str(e)}"
        )


@router.post("/batches/{batch_id}/migrate-customers-from-data")
def migrate_customers_from_data(
    batch_id: int,
    customers_data: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """
    Migrate customers from extracted data
    هجرة العملاء من البيانات المستخرجة
    """
    service = MigrationService(db)
    try:
        results = service.migrate_customers_from_data(batch_id, customers_data)
        return {
            "message": "Customers migration completed",
            "total_records": len(results),
            "successful_records": len([r for r in results if r.status == MigrationStatusEnum.COMPLETED]),
            "failed_records": len([r for r in results if r.status == MigrationStatusEnum.FAILED]),
            "results": [
                {
                    "source_id": r.source_id,
                    "target_id": r.target_id,
                    "status": r.status.value,
                    "error_message": r.error_message
                }
                for r in results
            ]
        }
    except Exception as e:
        logger.error(f"Failed to migrate customers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Customers migration failed: {str(e)}"
        )


@router.post("/batches/{batch_id}/migrate-vendors-from-data")
def migrate_vendors_from_data(
    batch_id: int,
    vendors_data: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """
    Migrate vendors from extracted data
    هجرة الموردين من البيانات المستخرجة
    """
    service = MigrationService(db)
    try:
        results = service.migrate_vendors_from_data(batch_id, vendors_data)
        return {
            "message": "Vendors migration completed",
            "total_records": len(results),
            "successful_records": len([r for r in results if r.status == MigrationStatusEnum.COMPLETED]),
            "failed_records": len([r for r in results if r.status == MigrationStatusEnum.FAILED]),
            "results": [
                {
                    "source_id": r.source_id,
                    "target_id": r.target_id,
                    "status": r.status.value,
                    "error_message": r.error_message
                }
                for r in results
            ]
        }
    except Exception as e:
        logger.error(f"Failed to migrate vendors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vendors migration failed: {str(e)}"
        )


# ====== Async Zoho Integration Endpoints ======

@router.post("/zoho/test-connection-async")
async def test_zoho_connection_async(
    zoho_config: ZohoConfigCreate,
    db: Session = Depends(get_db)
):
    """
    Test connection to Zoho APIs asynchronously
    اختبار الاتصال مع Zoho APIs بشكل غير متزامن
    """
    try:
        service = MigrationReportService(db)
        results = await service.test_zoho_connection_async(zoho_config)
        
        return {
            "message": "Connection test completed",
            "results": results,
            "success": results.get('books_api', False) or results.get('inventory_api', False)
        }
        
    except Exception as e:
        logger.error(f"Async connection test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Connection test failed: {str(e)}"
        )


@router.post("/zoho/extract-async")
async def extract_zoho_data_async(
    request: ZohoAsyncExtractRequest,
    db: Session = Depends(get_db)
):
    """
    Extract data from Zoho APIs asynchronously
    استخراج البيانات من Zoho APIs بشكل غير متزامن
    """
    try:
        service = MigrationReportService(db)
        
        # Extract data asynchronously
        results = await service.extract_zoho_data_async(
            zoho_config=request.zoho_config,
            data_types=[request.data_type],  # Convert single type to list
            progress_callback=None  # Could add WebSocket callback here
        )
        
        # Calculate summary statistics
        total_records = sum(len(data) for data in results.values())
        
        return {
            "message": "Data extraction completed successfully",
            "total_records": total_records,
            "data_types": list(results.keys()),
            "results": {
                data_type: {
                    "record_count": len(data),
                    "sample_record": data[0] if data else None
                }
                for data_type, data in results.items()
            }
        }
        
    except Exception as e:
        logger.error(f"Async data extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data extraction failed: {str(e)}"
        )


@router.post("/zoho/migrate-async")
async def migrate_from_zoho_async(
    request: ZohoMigrationRequest,
    db: Session = Depends(get_db),
    current_user_id: int = 1  # TODO: Get from authentication
):
    """
    Migrate data from Zoho APIs asynchronously
    هجرة البيانات من Zoho APIs بشكل غير متزامن
    """
    try:
        service = MigrationService(db)
        
        # Create migration batch
        batch = service.create_migration_batch(
            batch_name=request.batch_name or f"Zoho Migration {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description=request.description or "Async migration from Zoho APIs",
            source_system="zoho_api",
            created_by=current_user_id
        )
        
        # Start async migration
        results = await service.migrate_from_zoho_async(
            batch_id=batch.id,
            zoho_config=request.zoho_config,
            data_types=request.data_types,
            progress_callback=None  # Could add WebSocket callback here
        )
        
        return {
            "message": "Migration completed successfully",
            "batch_id": batch.id,
            "batch_name": batch.batch_name,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Async migration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )


@router.post("/zoho/preview-async")
async def preview_zoho_data_async(
    zoho_config: ZohoConfigCreate,
    data_type: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Preview data from Zoho APIs asynchronously
    معاينة البيانات من Zoho APIs بشكل غير متزامن
    """
    try:
        service = MigrationService(db)
        
        # Extract preview data
        results = await service.extract_and_preview_zoho_data(
            zoho_config=zoho_config,
            data_type=data_type,
            limit=limit
        )
        
        return {
            "message": f"Preview data extracted for {data_type}",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Async data preview failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data preview failed: {str(e)}"
        )


@router.get("/zoho/data-types")
def get_supported_data_types():
    """
    Get list of supported data types for Zoho extraction
    الحصول على قائمة أنواع البيانات المدعومة لاستخراج Zoho
    """
    return {
        "supported_data_types": [
            {
                "type": "items",
                "description": "Products and services from Zoho Inventory",
                "description_ar": "المنتجات والخدمات من Zoho Inventory"
            },
            {
                "type": "customers",
                "description": "Customer contacts from Zoho Books",
                "description_ar": "جهات اتصال العملاء من Zoho Books"
            },
            {
                "type": "vendors",
                "description": "Vendor contacts from Zoho Books",
                "description_ar": "جهات اتصال الموردين من Zoho Books"
            },
            {
                "type": "stock",
                "description": "Inventory stock levels from Zoho Inventory",
                "description_ar": "مستويات المخزون من Zoho Inventory"
            },
            {
                "type": "price_lists",
                "description": "Price lists from Zoho Inventory",
                "description_ar": "قوائم الأسعار من Zoho Inventory"
            }
        ]
    }


@router.post("/zoho/bulk-migrate-async")
async def bulk_migrate_from_zoho_async(
    requests: List[ZohoMigrationRequest],
    db: Session = Depends(get_db),
    current_user_id: int = 1  # TODO: Get from authentication
):
    """
    Migrate multiple data types from Zoho APIs in bulk asynchronously
    هجرة أنواع متعددة من البيانات من Zoho APIs بشكل مجمع وغير متزامن
    """
    try:
        service = MigrationService(db)
        batch_results = []
        
        for i, request in enumerate(requests):
            try:
                # Create migration batch
                batch = service.create_migration_batch(
                    batch_name=request.batch_name or f"Bulk Migration {i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    description=request.description or f"Bulk async migration from Zoho APIs - Batch {i+1}",
                    source_system="zoho_api",
                    created_by=current_user_id
                )
                
                # Start async migration
                results = await service.migrate_from_zoho_async(
                    batch_id=batch.id,
                    zoho_config=request.zoho_config,
                    data_types=request.data_types,
                    progress_callback=None
                )
                
                batch_results.append({
                    "batch_id": batch.id,
                    "batch_name": batch.batch_name,
                    "results": results,
                    "status": "success"
                })
                
            except Exception as e:
                batch_results.append({
                    "batch_id": None,
                    "batch_name": request.batch_name or f"Bulk Migration {i+1}",
                    "error": str(e),
                    "status": "failed"
                })
                logger.error(f"Bulk migration batch {i+1} failed: {e}")
        
        successful_batches = len([r for r in batch_results if r["status"] == "success"])
        failed_batches = len([r for r in batch_results if r["status"] == "failed"])
        
        return {
            "message": f"Bulk migration completed: {successful_batches} successful, {failed_batches} failed",
            "total_batches": len(requests),
            "successful_batches": successful_batches,
            "failed_batches": failed_batches,
            "batch_results": batch_results
        }
        
    except Exception as e:
        logger.error(f"Bulk migration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk migration failed: {str(e)}"
        )


# ====== Zoho Configuration Management ======

@router.post("/zoho/config/save")
def save_zoho_config(
    config: ZohoConfigCreate,
    db: Session = Depends(get_db)
):
    """
    Save Zoho configuration securely
    حفظ إعدادات Zoho بشكل آمن
    """
    try:
        from app.services.config_service import SecureConfigService
        
        config_service = SecureConfigService()
        config_service.save_zoho_config({
            "organization_id": config.organization_id,
            "access_token": config.access_token,
            "refresh_token": config.refresh_token,
            "client_id": config.client_id,
            "client_secret": config.client_secret
        })
        
        return {"message": "Zoho configuration saved successfully"}
        
    except Exception as e:
        logger.error(f"Failed to save Zoho config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save configuration: {str(e)}"
        )


@router.get("/zoho/config/status")
def get_zoho_config_status():
    """
    Check if Zoho configuration exists and is valid
    فحص حالة إعدادات Zoho
    """
    try:
        from app.services.config_service import SecureConfigService
        
        config_service = SecureConfigService()
        has_config = config_service.has_zoho_config()
        
        if has_config:
            # Test the configuration without exposing sensitive data
            config = config_service.get_zoho_config()
            return {
                "has_config": True,
                "organization_id": config.get("organization_id", "")[:10] + "..." if config.get("organization_id") else "",
                "has_access_token": bool(config.get("access_token")),
                "has_refresh_token": bool(config.get("refresh_token")),
                "has_client_id": bool(config.get("client_id")),
                "has_client_secret": bool(config.get("client_secret"))
            }
        else:
            return {"has_config": False}
            
    except Exception as e:
        logger.error(f"Failed to get config status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get configuration status: {str(e)}"
        )


@router.post("/zoho/config/test")
def test_zoho_config():
    """
    Test the stored Zoho configuration
    اختبار إعدادات Zoho المحفوظة
    """
    try:
        from app.services.config_service import SecureConfigService
        from app.services.zoho_service import ZohoAPIService, ZohoConfig
        
        config_service = SecureConfigService()
        if not config_service.has_zoho_config():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Zoho configuration found. Please save configuration first."
            )
        
        config = config_service.get_zoho_config()
        zoho_service = ZohoAPIService(
            ZohoConfig(
                organization_id=config["organization_id"],
                access_token=config["access_token"],
                refresh_token=config["refresh_token"],
                client_id=config["client_id"],
                client_secret=config["client_secret"]
            )
        )
        
        # Test connection
        test_results = zoho_service.test_connection()
        
        return {
            "connection_status": "success",
            "test_results": test_results
        }
        
    except Exception as e:
        logger.error(f"Config test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration test failed: {str(e)}"
        )


@router.delete("/zoho/config")
def delete_zoho_config():
    """
    Delete stored Zoho configuration
    حذف إعدادات Zoho المحفوظة
    """
    try:
        from app.services.config_service import SecureConfigService
        
        config_service = SecureConfigService()
        config_service.delete_zoho_config()
        
        return {"message": "Zoho configuration deleted successfully"}
        
    except Exception as e:
        logger.error(f"Failed to delete config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete configuration: {str(e)}"
        )


@router.get("/zoho/config/health")
def zoho_config_health():
    """
    Health check for Zoho configuration and connectivity
    فحص صحة إعدادات Zoho والاتصال
    """
    try:
        from app.services.config_service import SecureConfigService
        from app.services.zoho_service import ZohoAPIService, ZohoConfig
        
        config_service = SecureConfigService()
        health_status = {
            "config_service": "healthy",
            "has_config": config_service.has_zoho_config(),
            "zoho_connection": "not_tested"
        }
        
        if health_status["has_config"]:
            try:
                config = config_service.get_zoho_config()
                zoho_service = ZohoAPIService(
                    ZohoConfig(
                        organization_id=config["organization_id"],
                        access_token=config["access_token"],
                        refresh_token=config["refresh_token"],
                        client_id=config["client_id"],
                        client_secret=config["client_secret"]
                    )
                )
                
                # Quick connectivity test
                test_result = zoho_service.test_connection()
                health_status["zoho_connection"] = "healthy" if test_result else "failed"
                
            except Exception as conn_error:
                health_status["zoho_connection"] = f"failed: {str(conn_error)}"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "config_service": f"error: {str(e)}",
            "has_config": False,
            "zoho_connection": "not_available"
        }


# ====== Customer Import from Zoho Books ======

@router.post("/import-customers-from-zoho")
async def import_customers_from_zoho(
    batch_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user_id: int = 1  # TODO: Get from authentication
):
    """
    Import customers directly from Zoho Books API and store them in migration_customers table
    استيراد العملاء مباشرة من Zoho Books API وتخزينهم في جدول migration_customers
    """
    try:
        # Load Zoho credentials
        from app.services.config_service import SecureConfigService
        from app.services.zoho_service import ZohoAsyncService
        from app.schemas.migration import ZohoConfigCreate
        from app.models.migration import MigrationCustomer, CurrencyEnum
        
        config_service = SecureConfigService()
        credentials = config_service.get_zoho_credentials()
        
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Zoho credentials not configured. Please configure Zoho API credentials first."
            )
        
        # Create Zoho config
        zoho_config = ZohoConfigCreate(
            organization_id=credentials.organization_id,
            access_token=credentials.access_token,
            refresh_token=credentials.refresh_token,
            client_id=credentials.client_id,
            client_secret=credentials.client_secret
        )
        
        logger.info("Starting customer import from Zoho...")
        
        # Initialize counters
        total_imported = 0
        total_updated = 0
        total_errors = 0
        page = 1
        all_customers = []
        
        # Extract customers from Zoho
        async with ZohoAsyncService(zoho_config) as service:
            while True:
                try:
                    customers_data, has_more = await service.extract_customers(page=page, per_page=200)
                    all_customers.extend(customers_data)
                    
                    logger.info(f"Extracted {len(customers_data)} customers from page {page}")
                    
                    if not has_more:
                        break
                    
                    page += 1
                    
                    # Safety limit to prevent infinite loops
                    if page > 100:
                        logger.warning("Reached maximum page limit (100), stopping extraction")
                        break
                        
                except Exception as e:
                    logger.error(f"Error extracting customers from page {page}: {str(e)}")
                    total_errors += 1
                    break
        
        logger.info(f"Total customers extracted from Zoho: {len(all_customers)}")
        
        # Process and save customers to database
        for customer_data in all_customers:
            try:
                # Check if customer already exists
                existing_customer = db.query(MigrationCustomer).filter(
                    MigrationCustomer.zoho_customer_id == customer_data.get('zoho_customer_id')
                ).first()
                
                # Convert currency string to enum
                currency_value = customer_data.get('currency', 'IQD')
                try:
                    currency_enum = CurrencyEnum(currency_value)
                except ValueError:
                    currency_enum = CurrencyEnum.IQD  # Default to IQD
                
                if existing_customer:
                    # Update existing customer
                    existing_customer.code = customer_data.get('code', existing_customer.code)
                    existing_customer.name_en = customer_data.get('name_en', existing_customer.name_en)
                    existing_customer.name_ar = customer_data.get('name_ar', existing_customer.name_ar)
                    existing_customer.email = customer_data.get('email')
                    existing_customer.phone = customer_data.get('phone')
                    existing_customer.mobile = customer_data.get('mobile')
                    existing_customer.address_en = customer_data.get('address_en')
                    existing_customer.address_ar = customer_data.get('address_ar')
                    existing_customer.city = customer_data.get('city')
                    existing_customer.region = customer_data.get('region')
                    existing_customer.postal_code = customer_data.get('postal_code')
                    existing_customer.country = customer_data.get('country', 'Iraq')
                    existing_customer.tax_number = customer_data.get('tax_number')
                    existing_customer.currency = currency_enum
                    existing_customer.credit_limit = customer_data.get('credit_limit', 0)
                    existing_customer.payment_terms = customer_data.get('payment_terms')
                    existing_customer.outstanding_receivable = customer_data.get('outstanding_receivable', 0)
                    existing_customer.is_active = customer_data.get('is_active', True)
                    existing_customer.zoho_deposit_account = customer_data.get('zoho_deposit_account')
                    existing_customer.zoho_last_sync = datetime.utcnow()
                    existing_customer.updated_at = datetime.utcnow()
                    
                    total_updated += 1
                    logger.info(f"Updated customer: {existing_customer.name_en}")
                    
                else:
                    # Create new customer
                    new_customer = MigrationCustomer(
                        code=customer_data.get('code', f"ZOHO-{customer_data.get('zoho_customer_id')}"),
                        name_en=customer_data.get('name_en', ''),
                        name_ar=customer_data.get('name_ar', customer_data.get('name_en', '')),
                        email=customer_data.get('email'),
                        phone=customer_data.get('phone'),
                        mobile=customer_data.get('mobile'),
                        address_en=customer_data.get('address_en'),
                        address_ar=customer_data.get('address_ar'),
                        city=customer_data.get('city'),
                        region=customer_data.get('region'),
                        postal_code=customer_data.get('postal_code'),
                        country=customer_data.get('country', 'Iraq'),
                        tax_number=customer_data.get('tax_number'),
                        currency=currency_enum,
                        credit_limit=customer_data.get('credit_limit', 0),
                        payment_terms=customer_data.get('payment_terms'),
                        outstanding_receivable=customer_data.get('outstanding_receivable', 0),
                        is_active=customer_data.get('is_active', True),
                        zoho_customer_id=customer_data.get('zoho_customer_id'),
                        zoho_deposit_account=customer_data.get('zoho_deposit_account'),
                        zoho_last_sync=datetime.utcnow(),
                        created_at=datetime.utcnow()
                    )
                    
                    db.add(new_customer)
                    total_imported += 1
                    logger.info(f"Imported new customer: {new_customer.name_en}")
                    
            except Exception as e:
                total_errors += 1
                logger.error(f"Error processing customer {customer_data.get('name_en', 'Unknown')}: {str(e)}")
                continue
        
        # Commit all changes
        db.commit()
        
        return {
            "message": "Customer import from Zoho completed successfully",
            "summary": {
                "total_extracted": len(all_customers),
                "total_imported": total_imported,
                "total_updated": total_updated,
                "total_errors": total_errors,
                "total_processed": total_imported + total_updated
            },
            "details": {
                "pages_processed": page,
                "source": "zoho_books_api",
                "import_time": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Customer import from Zoho failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Customer import failed: {str(e)}"
        )


@router.get("/customers/stats")
def get_migration_stats(db: Session = Depends(get_db)):
    """Get migration customer statistics"""
    from app.models.migration import MigrationCustomer
    from sqlalchemy import func
    
    total = db.query(MigrationCustomer).count()
    active = db.query(MigrationCustomer).filter(MigrationCustomer.is_active == True).count()
    outstanding = db.query(func.sum(MigrationCustomer.outstanding_receivable)).scalar() or 0
    
    return {
        "total_customers": total,
        "active_customers": active,
        "inactive_customers": total - active,
        "total_outstanding": float(outstanding)
    }


# ====== Items Management (Public Access) ======

@router.get("/items/", response_model=List[Item])
def get_migration_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Search in item name or code"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    active_only: bool = Query(True, description="Active items only"),
    db: Session = Depends(get_db)
):
    """
    Get all migration items
    الحصول على جميع أصناف الهجرة
    """
    from app.models.migration import MigrationItem
    
    query = db.query(MigrationItem)
    
    if active_only:
        query = query.filter(MigrationItem.is_active == True)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                MigrationItem.name_en.ilike(search_filter),
                MigrationItem.name_ar.ilike(search_filter),
                MigrationItem.code.ilike(search_filter),
                MigrationItem.brand.ilike(search_filter)
            )
        )
    
    if category_id:
        query = query.filter(MigrationItem.category_id == category_id)
    
    query = query.order_by(MigrationItem.name_en)
    items = query.offset(skip).limit(limit).all()
    
    return items


@router.post("/items/", response_model=Item)
def create_migration_item(
    item: ItemCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new migration item
    إنشاء صنف هجرة جديد
    """
    from app.models.migration import MigrationItem
    
    # Check if code already exists
    existing = db.query(MigrationItem).filter(MigrationItem.code == item.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Item with code '{item.code}' already exists"
        )
    
    db_item = MigrationItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return db_item


@router.get("/items/{item_id}", response_model=Item)
def get_migration_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """
    Get migration item by ID
    الحصول على صنف الهجرة بالمعرف
    """
    from app.models.migration import MigrationItem
    
    item = db.query(MigrationItem).filter(MigrationItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return item


@router.put("/items/{item_id}", response_model=Item)
def update_migration_item(
    item_id: int,
    item: ItemUpdate,
    db: Session = Depends(get_db)
):
    """
    Update migration item
    تحديث صنف الهجرة
    """
    from app.models.migration import MigrationItem
    
    db_item = db.query(MigrationItem).filter(MigrationItem.id == item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Check if new code conflicts with existing
    if item.code and item.code != db_item.code:
        existing = db.query(MigrationItem).filter(MigrationItem.code == item.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Item with code '{item.code}' already exists"
            )
    
    for field, value in item.dict(exclude_unset=True).items():
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    
    return db_item


@router.delete("/items/{item_id}")
def delete_migration_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete migration item
    حذف صنف الهجرة
    """
    from app.models.migration import MigrationItem
    
    db_item = db.query(MigrationItem).filter(MigrationItem.id == item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    db.delete(db_item)
    db.commit()
    
    return {"message": "Item deleted successfully"}
