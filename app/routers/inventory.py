from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.schemas.inventory import (
    InventoryItem, StockMovementCreate, StockMovement, 
    InventoryReport, StockAdjustment
)
from app.services.inventory_service import InventoryService

router = APIRouter(tags=["inventory"])


@router.get("/items", response_model=List[InventoryItem])
def get_inventory_items(
    warehouse_id: Optional[int] = Query(None, description="معرف المستودع"),
    product_id: Optional[int] = Query(None, description="معرف المنتج"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """الحصول على عناصر المخزون"""
    return InventoryService.get_inventory_items(db, warehouse_id, product_id, skip, limit)


@router.get("/report", response_model=List[InventoryReport])
def get_inventory_report(
    warehouse_id: Optional[int] = Query(None, description="معرف المستودع"),
    low_stock_only: bool = Query(False, description="المخزون المنخفض فقط"),
    db: Session = Depends(get_db)
):
    """تقرير المخزون"""
    return InventoryService.get_inventory_report(db, warehouse_id, low_stock_only)


@router.post("/movements", response_model=StockMovement, status_code=201)
def record_stock_movement(
    stock_movement: StockMovementCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """تسجيل حركة مخزون"""
    return InventoryService.record_stock_movement(db, stock_movement)


@router.get("/movements", response_model=List[StockMovement])
def get_stock_movements(
    inventory_item_id: Optional[int] = Query(None, description="معرف عنصر المخزون"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """الحصول على حركات المخزون"""
    return InventoryService.get_stock_movements(db, inventory_item_id, skip, limit)


@router.post("/adjust", response_model=StockMovement, status_code=201)
def adjust_stock(
    adjustment: StockAdjustment,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """تعديل المخزون"""
    return InventoryService.adjust_stock(db, adjustment, user_id=1)
