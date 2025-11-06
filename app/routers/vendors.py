"""
Vendor Management Router for TSH ERP System
راوتر إدارة الموردين لنظام TSH ERP
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.migration import MigrationVendor
from app.models.user import User
from app.schemas.migration import VendorCreate, VendorUpdate
from app.dependencies.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

# Vendor response schema
class Vendor(BaseModel):
    id: int
    code: str
    name_ar: str
    name_en: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address_ar: Optional[str] = None
    address_en: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

router = APIRouter(prefix="/vendors", tags=["vendors"])


@router.get("/", response_model=List[Vendor])
async def get_vendors(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all vendors with optional search"""
    query = db.query(MigrationVendor)
    
    if search:
        query = query.filter(
            MigrationVendor.name_en.ilike(f"%{search}%") |
            MigrationVendor.name_ar.ilike(f"%{search}%") |
            MigrationVendor.code.ilike(f"%{search}%") |
            MigrationVendor.email.ilike(f"%{search}%")
        )
    
    vendors = query.offset(skip).limit(limit).all()
    return vendors


@router.get("/{vendor_id}", response_model=Vendor)
async def get_vendor(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get vendor by ID"""
    vendor = db.query(MigrationVendor).filter(MigrationVendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    return vendor


@router.post("/", response_model=Vendor)
async def create_vendor(
    vendor: VendorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new vendor"""
    db_vendor = MigrationVendor(**vendor.dict())
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor


@router.put("/{vendor_id}", response_model=Vendor)
async def update_vendor(
    vendor_id: int,
    vendor: VendorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update vendor"""
    db_vendor = db.query(MigrationVendor).filter(MigrationVendor.id == vendor_id).first()
    if not db_vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    
    for field, value in vendor.dict(exclude_unset=True).items():
        setattr(db_vendor, field, value)
    
    db.commit()
    db.refresh(db_vendor)
    return db_vendor


@router.delete("/{vendor_id}")
async def delete_vendor(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete vendor"""
    db_vendor = db.query(MigrationVendor).filter(MigrationVendor.id == vendor_id).first()
    if not db_vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    
    db.delete(db_vendor)
    db.commit()
    return {"message": "Vendor deleted successfully"}
