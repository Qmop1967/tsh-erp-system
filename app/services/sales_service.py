from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
from decimal import Decimal
from datetime import date, datetime
from app.models.sales import SalesOrder, SalesItem
from app.models.customer import Customer
from app.models.product import Product
from app.schemas.sales import SalesOrderCreate, SalesOrderUpdate, SalesItemCreate
from app.services.inventory_service import InventoryService
from fastapi import HTTPException, status


class SalesService:
    """خدمة إدارة المبيعات"""

    @staticmethod
    def generate_order_number(db: Session) -> str:
        """إنشاء رقم أمر البيع"""
        # الحصول على آخر رقم أمر لهذا العام
        current_year = date.today().year
        prefix = f"SO-{current_year}-"
        
        last_order = db.query(SalesOrder).filter(
            SalesOrder.order_number.like(f"{prefix}%")
        ).order_by(desc(SalesOrder.id)).first()
        
        if last_order:
            # استخراج الرقم التسلسلي من آخر أمر
            try:
                last_number = int(last_order.order_number.split("-")[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:04d}"

    @staticmethod
    def calculate_order_totals(items: List[SalesItem]) -> dict:
        """حساب إجماليات الأمر"""
        subtotal = sum(item.line_total for item in items)
        return {
            "subtotal": subtotal,
            "item_count": len(items),
            "total_quantity": sum(item.quantity for item in items)
        }

    @staticmethod
    def calculate_item_totals(quantity: Decimal, unit_price: Decimal, 
                            discount_percentage: Decimal = 0, 
                            discount_amount: Decimal = 0) -> dict:
        """حساب إجماليات عنصر البيع"""
        line_subtotal = quantity * unit_price
        
        # حساب الخصم
        if discount_percentage > 0:
            discount_amount = line_subtotal * (discount_percentage / 100)
        
        line_total = line_subtotal - discount_amount
        
        return {
            "line_total": line_total,
            "discount_amount": discount_amount
        }

    @staticmethod
    def create_sales_order(db: Session, sales_order: SalesOrderCreate, created_by: int) -> SalesOrder:
        """إنشاء أمر بيع جديد"""
        # التحقق من وجود العميل
        customer = db.query(Customer).filter(Customer.id == sales_order.customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )

        # إنشاء رقم الأمر
        order_number = SalesService.generate_order_number(db)
        
        # إنشاء أمر البيع
        db_order = SalesOrder(
            order_number=order_number,
            customer_id=sales_order.customer_id,
            branch_id=sales_order.branch_id,
            warehouse_id=sales_order.warehouse_id,
            order_date=sales_order.order_date,
            expected_delivery_date=sales_order.expected_delivery_date,
            status=sales_order.status,
            payment_method=sales_order.payment_method,
            discount_percentage=sales_order.discount_percentage,
            tax_percentage=sales_order.tax_percentage,
            notes=sales_order.notes,
            created_by=created_by
        )
        
        db.add(db_order)
        db.flush()  # للحصول على ID الأمر
        
        # إضافة عناصر البيع
        total_subtotal = Decimal(0)
        for item_data in sales_order.sales_items:
            # التحقق من وجود المنتج
            product = db.query(Product).filter(Product.id == item_data.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product with ID {item_data.product_id} not found"
                )
            
            # حساب إجماليات العنصر
            totals = SalesService.calculate_item_totals(
                item_data.quantity,
                item_data.unit_price,
                item_data.discount_percentage,
                item_data.discount_amount
            )
            
            # إنشاء عنصر البيع
            sales_item = SalesItem(
                sales_order_id=db_order.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                discount_percentage=item_data.discount_percentage,
                discount_amount=totals["discount_amount"],
                line_total=totals["line_total"],
                notes=item_data.notes
            )
            
            db.add(sales_item)
            total_subtotal += totals["line_total"]
        
        # حساب الإجماليات النهائية
        db_order.subtotal = total_subtotal
        db_order.discount_amount = total_subtotal * (sales_order.discount_percentage / 100)
        subtotal_after_discount = total_subtotal - db_order.discount_amount
        db_order.tax_amount = subtotal_after_discount * (sales_order.tax_percentage / 100)
        db_order.total_amount = subtotal_after_discount + db_order.tax_amount
        
        db.commit()
        db.refresh(db_order)
        return db_order

    @staticmethod
    def confirm_sales_order(db: Session, order_id: int, user_id: int) -> SalesOrder:
        """تأكيد أمر البيع وحجز المخزون"""
        db_order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
        if not db_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sales order not found"
            )
        
        if db_order.status != "DRAFT":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft orders can be confirmed"
            )
        
        # حجز المخزون لكل عنصر
        try:
            for item in db_order.sales_items:
                InventoryService.reserve_stock(
                    db, item.product_id, db_order.warehouse_id, item.quantity
                )
        except Exception as e:
            # إذا فشل حجز أي عنصر، إلغاء كل الحجوزات
            for item in db_order.sales_items:
                try:
                    InventoryService.release_reservation(
                        db, item.product_id, db_order.warehouse_id, item.quantity
                    )
                except:
                    pass
            raise e
        
        # تحديث حالة الأمر
        db_order.status = "CONFIRMED"
        db.commit()
        db.refresh(db_order)
        return db_order

    @staticmethod
    def ship_sales_order(db: Session, order_id: int, user_id: int) -> SalesOrder:
        """شحن أمر البيع وخصم المخزون"""
        db_order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
        if not db_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sales order not found"
            )
        
        if db_order.status != "CONFIRMED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only confirmed orders can be shipped"
            )
        
        # خصم المخزون لكل عنصر
        for item in db_order.sales_items:
            # إلغاء الحجز أولاً
            InventoryService.release_reservation(
                db, item.product_id, db_order.warehouse_id, item.quantity
            )
            
            # خصم من المخزون
            inventory_item = InventoryService.get_or_create_inventory_item(
                db, item.product_id, db_order.warehouse_id
            )
            
            from app.schemas.inventory import StockMovementCreate
            stock_movement = StockMovementCreate(
                inventory_item_id=inventory_item.id,
                movement_type="OUT",
                reference_type="SALE",
                reference_id=db_order.id,
                quantity=-item.quantity,
                notes=f"Sale order: {db_order.order_number}",
                created_by=user_id
            )
            
            InventoryService.record_stock_movement(db, stock_movement)
            
            # تحديث الكمية المسلمة
            item.delivered_quantity = item.quantity
        
        # تحديث حالة الأمر
        db_order.status = "SHIPPED"
        db.commit()
        db.refresh(db_order)
        return db_order

    @staticmethod
    def get_sales_orders(db: Session, skip: int = 0, limit: int = 100,
                        status: Optional[str] = None, customer_id: Optional[int] = None,
                        date_from: Optional[date] = None, date_to: Optional[date] = None) -> List[SalesOrder]:
        """الحصول على قائمة أوامر البيع مع التصفية"""
        query = db.query(SalesOrder).order_by(desc(SalesOrder.created_at))
        
        if status:
            query = query.filter(SalesOrder.status == status)
        
        if customer_id:
            query = query.filter(SalesOrder.customer_id == customer_id)
        
        if date_from:
            query = query.filter(SalesOrder.order_date >= date_from)
        
        if date_to:
            query = query.filter(SalesOrder.order_date <= date_to)
        
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_sales_order_by_id(db: Session, order_id: int) -> SalesOrder:
        """الحصول على أمر بيع بالمعرف"""
        order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sales order not found"
            )
        return order

    @staticmethod
    def cancel_sales_order(db: Session, order_id: int, user_id: int) -> SalesOrder:
        """إلغاء أمر البيع"""
        db_order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
        if not db_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sales order not found"
            )
        
        if db_order.status in ["DELIVERED", "CANCELLED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel delivered or already cancelled orders"
            )
        
        # إلغاء حجز المخزون إذا كان الأمر مؤكداً
        if db_order.status == "CONFIRMED":
            for item in db_order.sales_items:
                InventoryService.release_reservation(
                    db, item.product_id, db_order.warehouse_id, item.quantity
                )
        
        # تحديث حالة الأمر
        db_order.status = "CANCELLED"
        db.commit()
        db.refresh(db_order)
        return db_order
