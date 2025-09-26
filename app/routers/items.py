"""
Inventory Management Router for TSH ERP System
راوتر إدارة المخزون لنظام TSH ERP
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.migration import MigrationItem
from app.models.user import User
from app.schemas.migration import Item, ItemCreate, ItemUpdate
from app.routers.auth import get_current_user
from app.services.permission_service import simple_require_permission

router = APIRouter(prefix="/items", tags=["inventory"])


@router.get("/", response_model=List[Item])
@simple_require_permission("items.view")
async def get_items(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all items with optional filtering"""
    query = db.query(MigrationItem)
    
    if search:
        query = query.filter(
            MigrationItem.name_en.ilike(f"%{search}%") |
            MigrationItem.name_ar.ilike(f"%{search}%") |
            MigrationItem.code.ilike(f"%{search}%")
        )
    
    if category_id:
        query = query.filter(MigrationItem.category_id == category_id)
    
    items = query.offset(skip).limit(limit).all()
    return items


@router.get("/{item_id}", response_model=Item)
async def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get item by ID"""
    item = db.query(MigrationItem).filter(MigrationItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return item


@router.post("/", response_model=Item)
async def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new item"""
    db_item = MigrationItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/{item_id}", response_model=Item)
async def update_item(
    item_id: int,
    item: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update item"""
    db_item = db.query(MigrationItem).filter(MigrationItem.id == item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    for field, value in item.dict(exclude_unset=True).items():
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/{item_id}")
async def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete item"""
    db_item = db.query(MigrationItem).filter(MigrationItem.id == item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}
