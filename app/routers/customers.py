from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.db.database import get_db
from app.schemas.customer import (
    CustomerCreate, CustomerUpdate, Customer,
    SupplierCreate, SupplierUpdate, Supplier
)
from app.services.customer_service import CustomerService, SupplierService
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.permission_service import simple_require_permission

router = APIRouter(tags=["customers"])


# Customer endpoints
@router.get("/generate-code")
def generate_customer_code(
    prefix: str = Query("CUST", description="Customer code prefix"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate next available customer code"""
    return {
        "customer_code": CustomerService.generate_customer_code(db, prefix),
        "format": "PREFIX-YYYY-NNNN",
        "example": "CUST-2025-0001"
    }


@router.post("/", response_model=Customer, status_code=201)
@simple_require_permission("create_customer")
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """إنشاء عميل جديد"""
    return CustomerService.create_customer(db, customer)


@router.get("/", response_model=List[Customer])
@simple_require_permission("customers.view")
def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="البحث في الاسم أو رقم العميل"),
    active_only: bool = Query(True, description="العملاء النشطين فقط"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """الحصول على قائمة العملاء"""
    return CustomerService.get_customers(db, skip, limit, search, active_only)


@router.get("/salespersons", response_model=List[dict])
def get_salespersons(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Temporarily disabled for development
):
    """Get all salespersons for customer assignment"""
    from app.models.user import User
    salespersons = db.query(User).filter(
        User.is_salesperson == True,
        User.is_active == True
    ).all()
    return [{"id": sp.id, "name": sp.name, "employee_code": sp.employee_code} for sp in salespersons]


@router.get("/{customer_id}", response_model=Customer)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Temporarily disabled for development
):
    """الحصول على عميل بالمعرف"""
    customer = CustomerService.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.get("/all/combined")
def get_all_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Search in customer name or code"),
    active_only: bool = Query(True, description="Active customers only"),
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Temporarily disabled for development
):
    """
    Get all customers (both regular and migrated from Zoho)
    الحصول على جميع العملاء (العاديين والمهاجرين من زوهو)
    """
    from app.models.migration import MigrationCustomer
    from app.models.customer import Customer as CustomerModel
    
    # Get regular customers
    regular_customers = CustomerService.get_customers(db, skip, limit, search, active_only)
    
    # Get migrated customers
    migrated_query = db.query(MigrationCustomer)
    
    if active_only:
        migrated_query = migrated_query.filter(MigrationCustomer.is_active == True)
    
    if search:
        search_filter = f"%{search}%"
        migrated_query = migrated_query.filter(
            or_(
                MigrationCustomer.name_en.ilike(search_filter),
                MigrationCustomer.name_ar.ilike(search_filter),
                MigrationCustomer.code.ilike(search_filter)
            )
        )
    
    migrated_customers = migrated_query.offset(0).limit(limit).all()
    
    # Combine results
    result = []
    
    # Add regular customers
    for customer in regular_customers:
        # Get salesperson info if assigned
        salesperson_name = None
        if customer.salesperson_id:
            from app.models.user import User
            salesperson = db.query(User).filter(User.id == customer.salesperson_id).first()
            if salesperson:
                salesperson_name = salesperson.name
        
        result.append({
            "id": customer.id,
            "code": customer.customer_code,
            "name": customer.name,
            "company_name": customer.company_name,
            "email": customer.email,
            "phone": customer.phone,
            "address": customer.address,
            "city": customer.city,
            "country": customer.country,
            "currency": customer.currency,
            "portal_language": customer.portal_language,
            "salesperson_id": customer.salesperson_id,
            "salesperson_name": salesperson_name,
            "tax_number": customer.tax_number,
            "credit_limit": float(customer.credit_limit) if customer.credit_limit else 0,
            "payment_terms": customer.payment_terms,
            "discount_percentage": float(customer.discount_percentage) if customer.discount_percentage else 0,
            "is_active": customer.is_active,
            "notes": customer.notes,
            "created_at": customer.created_at.isoformat() if customer.created_at else None,
            "updated_at": customer.updated_at.isoformat() if customer.updated_at else None,
            "source": "regular"
        })
    
    # Add migrated customers
    for customer in migrated_customers:
        result.append({
            "id": f"zoho_{customer.id}",
            "code": customer.code,
            "name": customer.name_en,
            "name_ar": customer.name_ar,
            "company_name": customer.name_en,
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
    
    return {
        "customers": result,
        "total_regular": len(regular_customers),
        "total_migrated": len(migrated_customers),
        "total": len(result)
    }


@router.put("/{customer_id}", response_model=Customer)
def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Temporarily disabled for development
):
    """تحديث عميل"""
    customer = CustomerService.update_customer(db, customer_id, customer_update)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.delete("/{customer_id}", response_model=Customer)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Temporarily disabled for development
):
    """حذف عميل (إلغاء تنشيط)"""
    customer = CustomerService.delete_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


# Supplier endpoints
@router.post("/suppliers", response_model=Supplier, status_code=201)
def create_supplier(
    supplier: SupplierCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Temporarily disabled for development
):
    """إنشاء مورد جديد"""
    return SupplierService.create_supplier(db, supplier)


@router.get("/suppliers", response_model=List[Supplier])
def get_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="البحث في الاسم أو رقم المورد"),
    active_only: bool = Query(True, description="الموردين النشطين فقط"),
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Temporarily disabled for development
):
    """الحصول على قائمة الموردين"""
    return SupplierService.get_suppliers(db, skip, limit, search, active_only)


@router.get("/suppliers/{supplier_id}", response_model=Supplier)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Temporarily disabled for development
):
    """الحصول على مورد بالمعرف"""
    supplier = SupplierService.get_supplier(db, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.put("/suppliers/{supplier_id}", response_model=Supplier)
def update_supplier(
    supplier_id: int,
    supplier_update: SupplierUpdate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Temporarily disabled for development
):
    """تحديث مورد"""
    supplier = SupplierService.update_supplier(db, supplier_id, supplier_update)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.delete("/suppliers/{supplier_id}", response_model=Supplier)
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Temporarily disabled for development
):
    """حذف مورد (إلغاء تنشيط)"""
    supplier = SupplierService.delete_supplier(db, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.get("/branches", response_model=List[dict])
def get_branches(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Temporarily disabled for development
):
    """Get all branches for customer assignment"""
    from app.models.branch import Branch
    branches = db.query(Branch).filter(Branch.is_active == True).all()
    return [{"id": branch.id, "name": branch.name} for branch in branches]


# ...existing code...