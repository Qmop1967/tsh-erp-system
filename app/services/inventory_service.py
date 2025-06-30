from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from decimal import Decimal
from app.models.inventory import InventoryItem, StockMovement
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.schemas.inventory import (
    InventoryItemCreate, InventoryItemUpdate, StockMovementCreate, 
    InventoryReport, StockAdjustment
)
from fastapi import HTTPException, status


class InventoryService:
    """خدمة إدارة المخزون"""

    @staticmethod
    def get_or_create_inventory_item(db: Session, product_id: int, warehouse_id: int) -> InventoryItem:
        """الحصول على عنصر المخزون أو إنشاؤه إذا لم يكن موجوداً"""
        inventory_item = db.query(InventoryItem).filter(
            and_(
                InventoryItem.product_id == product_id,
                InventoryItem.warehouse_id == warehouse_id
            )
        ).first()
        
        if not inventory_item:
            # التحقق من وجود المنتج والمستودع
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found"
                )
            
            warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
            if not warehouse:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Warehouse not found"
                )
            
            inventory_item = InventoryItem(
                product_id=product_id,
                warehouse_id=warehouse_id,
                quantity_on_hand=0,
                quantity_reserved=0,
                quantity_ordered=0
            )
            db.add(inventory_item)
            db.commit()
            db.refresh(inventory_item)
        
        return inventory_item

    @staticmethod
    def record_stock_movement(db: Session, stock_movement: StockMovementCreate) -> StockMovement:
        """تسجيل حركة مخزون وتحديث الكميات"""
        # التحقق من وجود عنصر المخزون
        inventory_item = db.query(InventoryItem).filter(
            InventoryItem.id == stock_movement.inventory_item_id
        ).first()
        
        if not inventory_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory item not found"
            )
        
        # إنشاء حركة المخزون
        db_movement = StockMovement(**stock_movement.dict())
        db.add(db_movement)
        
        # تحديث كمية المخزون حسب نوع الحركة
        if stock_movement.movement_type == "IN":
            inventory_item.quantity_on_hand += abs(stock_movement.quantity)
            
            # تحديث التكلفة
            if stock_movement.unit_cost:
                if inventory_item.last_cost is None:
                    inventory_item.last_cost = stock_movement.unit_cost
                    inventory_item.average_cost = stock_movement.unit_cost
                else:
                    # حساب متوسط التكلفة
                    total_value = (inventory_item.quantity_on_hand * inventory_item.average_cost) + \
                                (stock_movement.quantity * stock_movement.unit_cost)
                    inventory_item.average_cost = total_value / inventory_item.quantity_on_hand
                    inventory_item.last_cost = stock_movement.unit_cost
                    
        elif stock_movement.movement_type == "OUT":
            quantity_to_deduct = abs(stock_movement.quantity)
            if inventory_item.quantity_on_hand < quantity_to_deduct:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient inventory quantity"
                )
            inventory_item.quantity_on_hand -= quantity_to_deduct
            
        elif stock_movement.movement_type == "ADJUSTMENT":
            # التعديل المباشر للكمية
            inventory_item.quantity_on_hand = abs(stock_movement.quantity)
        
        db.commit()
        db.refresh(db_movement)
        return db_movement

    @staticmethod
    def adjust_stock(db: Session, adjustment: StockAdjustment, user_id: int) -> StockMovement:
        """تعديل المخزون"""
        inventory_item = db.query(InventoryItem).filter(
            InventoryItem.id == adjustment.inventory_item_id
        ).first()
        
        if not inventory_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory item not found"
            )
        
        # حساب الفرق
        current_quantity = inventory_item.quantity_on_hand
        difference = adjustment.new_quantity - current_quantity
        
        # إنشاء حركة التعديل
        stock_movement = StockMovementCreate(
            inventory_item_id=adjustment.inventory_item_id,
            movement_type="ADJUSTMENT",
            reference_type="ADJUSTMENT",
            quantity=difference,
            notes=f"{adjustment.reason}. {adjustment.notes or ''}",
            created_by=user_id
        )
        
        return InventoryService.record_stock_movement(db, stock_movement)

    @staticmethod
    def reserve_stock(db: Session, product_id: int, warehouse_id: int, 
                     quantity: Decimal) -> bool:
        """حجز مخزون للبيع"""
        inventory_item = InventoryService.get_or_create_inventory_item(
            db, product_id, warehouse_id
        )
        
        if inventory_item.available_quantity < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient available inventory"
            )
        
        inventory_item.quantity_reserved += quantity
        db.commit()
        return True

    @staticmethod
    def release_reservation(db: Session, product_id: int, warehouse_id: int, 
                           quantity: Decimal) -> bool:
        """إلغاء حجز المخزون"""
        inventory_item = InventoryService.get_or_create_inventory_item(
            db, product_id, warehouse_id
        )
        
        if inventory_item.quantity_reserved < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot release more than reserved quantity"
            )
        
        inventory_item.quantity_reserved -= quantity
        db.commit()
        return True

    @staticmethod
    def get_inventory_report(db: Session, warehouse_id: Optional[int] = None,
                           low_stock_only: bool = False) -> List[InventoryReport]:
        """تقرير المخزون"""
        query = db.query(InventoryItem).join(Product).join(Warehouse)
        
        if warehouse_id:
            query = query.filter(InventoryItem.warehouse_id == warehouse_id)
        
        inventory_items = query.all()
        report = []
        
        for item in inventory_items:
            is_below_min = item.quantity_on_hand < item.product.min_stock_level
            is_below_reorder = item.quantity_on_hand < item.product.reorder_point
            
            if low_stock_only and not (is_below_min or is_below_reorder):
                continue
            
            total_value = None
            if item.average_cost:
                total_value = item.quantity_on_hand * item.average_cost
            
            report_item = InventoryReport(
                product_id=item.product.id,
                product_sku=item.product.sku,
                product_name=item.product.name,
                warehouse_id=item.warehouse.id,
                warehouse_name=item.warehouse.name,
                quantity_on_hand=item.quantity_on_hand,
                quantity_reserved=item.quantity_reserved,
                available_quantity=item.available_quantity,
                min_stock_level=item.product.min_stock_level,
                reorder_point=item.product.reorder_point,
                is_below_min=is_below_min,
                is_below_reorder=is_below_reorder,
                last_cost=item.last_cost,
                average_cost=item.average_cost,
                total_value=total_value
            )
            report.append(report_item)
        
        return report

    @staticmethod
    def get_stock_movements(db: Session, inventory_item_id: Optional[int] = None,
                           skip: int = 0, limit: int = 100) -> List[StockMovement]:
        """الحصول على حركات المخزون"""
        query = db.query(StockMovement).order_by(StockMovement.created_at.desc())
        
        if inventory_item_id:
            query = query.filter(StockMovement.inventory_item_id == inventory_item_id)
        
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_inventory_items(db: Session, warehouse_id: Optional[int] = None,
                          product_id: Optional[int] = None, skip: int = 0, 
                          limit: int = 100) -> List[InventoryItem]:
        """الحصول على عناصر المخزون مع إمكانية التصفية"""
        query = db.query(InventoryItem)
        
        if warehouse_id:
            query = query.filter(InventoryItem.warehouse_id == warehouse_id)
        
        if product_id:
            query = query.filter(InventoryItem.product_id == product_id)
        
        return query.offset(skip).limit(limit).all()
