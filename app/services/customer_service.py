from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.models.customer import Customer, Supplier
from app.schemas.customer import CustomerCreate, CustomerUpdate, SupplierCreate, SupplierUpdate
from fastapi import HTTPException, status


class CustomerService:
    """خدمة إدارة العملاء"""

    @staticmethod
    def create_customer(db: Session, customer: CustomerCreate) -> Customer:
        """إنشاء عميل جديد"""
        # التحقق من عدم تكرار رقم العميل
        existing_customer = db.query(Customer).filter(
            Customer.customer_code == customer.customer_code
        ).first()
        
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer code already exists"
            )
        
        db_customer = Customer(**customer.dict())
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer

    @staticmethod
    def get_customers(db: Session, skip: int = 0, limit: int = 100, 
                     search: Optional[str] = None, active_only: bool = True) -> List[Customer]:
        """الحصول على قائمة العملاء"""
        query = db.query(Customer)
        
        if active_only:
            query = query.filter(Customer.is_active == True)
        
        if search:
            query = query.filter(
                or_(
                    Customer.name.ilike(f"%{search}%"),
                    Customer.customer_code.ilike(f"%{search}%"),
                    Customer.company_name.ilike(f"%{search}%")
                )
            )
        
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_customer(db: Session, customer_id: int) -> Customer:
        """الحصول على عميل محدد"""
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        return customer

    @staticmethod
    def update_customer(db: Session, customer_id: int, customer_update: CustomerUpdate) -> Customer:
        """تحديث بيانات عميل"""
        customer = CustomerService.get_customer(db, customer_id)
        
        # التحقق من عدم تكرار رقم العميل إذا تم تغييره
        if customer_update.customer_code and customer_update.customer_code != customer.customer_code:
            existing_customer = db.query(Customer).filter(
                Customer.customer_code == customer_update.customer_code
            ).first()
            
            if existing_customer:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Customer code already exists"
                )
        
        update_data = customer_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(customer, field, value)
        
        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def delete_customer(db: Session, customer_id: int) -> Customer:
        """حذف عميل (إلغاء تنشيط)"""
        customer = CustomerService.get_customer(db, customer_id)
        customer.is_active = False
        db.commit()
        db.refresh(customer)
        return customer


class SupplierService:
    """خدمة إدارة الموردين"""

    @staticmethod
    def create_supplier(db: Session, supplier: SupplierCreate) -> Supplier:
        """إنشاء مورد جديد"""
        # التحقق من عدم تكرار رقم المورد
        existing_supplier = db.query(Supplier).filter(
            Supplier.supplier_code == supplier.supplier_code
        ).first()
        
        if existing_supplier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Supplier code already exists"
            )
        
        db_supplier = Supplier(**supplier.dict())
        db.add(db_supplier)
        db.commit()
        db.refresh(db_supplier)
        return db_supplier

    @staticmethod
    def get_suppliers(db: Session, skip: int = 0, limit: int = 100, 
                     search: Optional[str] = None, active_only: bool = True) -> List[Supplier]:
        """الحصول على قائمة الموردين"""
        query = db.query(Supplier)
        
        if active_only:
            query = query.filter(Supplier.is_active == True)
        
        if search:
            query = query.filter(
                or_(
                    Supplier.name.ilike(f"%{search}%"),
                    Supplier.supplier_code.ilike(f"%{search}%"),
                    Supplier.company_name.ilike(f"%{search}%")
                )
            )
        
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_supplier(db: Session, supplier_id: int) -> Supplier:
        """الحصول على مورد محدد"""
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found"
            )
        return supplier

    @staticmethod
    def update_supplier(db: Session, supplier_id: int, supplier_update: SupplierUpdate) -> Supplier:
        """تحديث بيانات مورد"""
        supplier = SupplierService.get_supplier(db, supplier_id)
        
        # التحقق من عدم تكرار رقم المورد إذا تم تغييره
        if supplier_update.supplier_code and supplier_update.supplier_code != supplier.supplier_code:
            existing_supplier = db.query(Supplier).filter(
                Supplier.supplier_code == supplier_update.supplier_code
            ).first()
            
            if existing_supplier:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Supplier code already exists"
                )
        
        update_data = supplier_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(supplier, field, value)
        
        db.commit()
        db.refresh(supplier)
        return supplier

    @staticmethod
    def delete_supplier(db: Session, supplier_id: int) -> Supplier:
        """حذف مورد (إلغاء تنشيط)"""
        supplier = SupplierService.get_supplier(db, supplier_id)
        supplier.is_active = False
        db.commit()
        db.refresh(supplier)
        return supplier
