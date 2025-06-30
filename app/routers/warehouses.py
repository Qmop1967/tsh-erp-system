"""
Warehouse Management Router for TSH ERP System
راوتر إدارة المخازن لنظام TSH ERP
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.warehouse import Warehouse
from app.models.user import User
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate, Warehouse as WarehouseSchema
from app.routers.auth import get_current_user

router = APIRouter(prefix="/warehouses", tags=["warehouses"])


@router.get("/", response_model=List[WarehouseSchema])
async def get_warehouses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all warehouses"""
    warehouses = db.query(Warehouse).offset(skip).limit(limit).all()
    return warehouses


@router.get("/{warehouse_id}", response_model=WarehouseSchema)
async def get_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get warehouse by ID"""
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
    return warehouse


@router.post("/", response_model=WarehouseSchema)
async def create_warehouse(
    warehouse: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new warehouse"""
    db_warehouse = Warehouse(**warehouse.dict())
    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse


@router.put("/{warehouse_id}", response_model=WarehouseSchema)
async def update_warehouse(
    warehouse_id: int,
    warehouse: WarehouseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update warehouse"""
    db_warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not db_warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
    
    for field, value in warehouse.dict(exclude_unset=True).items():
        setattr(db_warehouse, field, value)
    
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse


@router.delete("/{warehouse_id}")
async def delete_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete warehouse"""
    db_warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not db_warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
    
    db.delete(db_warehouse)
    db.commit()
    return {"message": "Warehouse deleted successfully"}
