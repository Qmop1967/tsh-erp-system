"""
Sales Service - Business Logic for Sales Order Management

Refactored for Phase 5 P3 Batch 1 using Phase 4 patterns:
- Instance methods with BaseRepository
- Custom exceptions instead of HTTPException
- Pagination and search support

Author: Claude Code (Senior Software Engineer AI)
Date: January 7, 2025
Phase: 5 P3 Batch 1 - Sales Router Migration
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_
from typing import List, Optional, Tuple
from decimal import Decimal
from datetime import date, datetime
from fastapi import Depends

from app.models.sales import SalesOrder, SalesItem
from app.models.customer import Customer
from app.models.product import Product
from app.schemas.sales import SalesOrderCreate, SalesOrderUpdate, SalesItemCreate
from app.services.inventory_service import InventoryService
from app.repositories import BaseRepository
from app.exceptions import EntityNotFoundError, ValidationError


class SalesService:
    """
    Service for sales order management.

    Handles all business logic for sales orders and items,
    replacing direct database operations in the router.
    """

    def __init__(self, db: Session):
        """
        Initialize sales service.

        Args:
            db: Database session
        """
        self.db = db
        self.sales_order_repo = BaseRepository(SalesOrder, db)
        self.sales_item_repo = BaseRepository(SalesItem, db)
        self.customer_repo = BaseRepository(Customer, db)
        self.product_repo = BaseRepository(Product, db)

    # ========================================================================
    # Order Number Generation
    # ========================================================================

    def generate_order_number(self) -> str:
        """
        Generate unique sales order number.

        Format: SO-YYYY-NNNN

        Returns:
            Generated order number
        """
        current_year = date.today().year
        prefix = f"SO-{current_year}-"

        last_order = self.db.query(SalesOrder).filter(
            SalesOrder.order_number.like(f"{prefix}%")
        ).order_by(desc(SalesOrder.id)).first()

        if last_order:
            try:
                last_number = int(last_order.order_number.split("-")[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1

        return f"{prefix}{new_number:04d}"

    # ========================================================================
    # Calculation Helpers
    # ========================================================================

    def calculate_item_totals(
        self,
        quantity: Decimal,
        unit_price: Decimal,
        discount_percentage: Decimal = 0,
        discount_amount: Decimal = 0
    ) -> dict:
        """
        Calculate sales item totals.

        Args:
            quantity: Item quantity
            unit_price: Unit price
            discount_percentage: Discount percentage
            discount_amount: Discount amount (overrides percentage)

        Returns:
            Dictionary with line_total and discount_amount
        """
        line_subtotal = quantity * unit_price

        # Calculate discount
        if discount_percentage > 0:
            discount_amount = line_subtotal * (discount_percentage / 100)

        line_total = line_subtotal - discount_amount

        return {
            "line_total": line_total,
            "discount_amount": discount_amount
        }

    # ========================================================================
    # Sales Order CRUD Operations
    # ========================================================================

    def get_all_sales_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        customer_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        search: Optional[str] = None
    ) -> Tuple[List[SalesOrder], int]:
        """
        Get all sales orders with optional filters.

        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            status: Filter by status
            customer_id: Filter by customer
            date_from: Filter from date
            date_to: Filter to date
            search: Search in order_number or notes

        Returns:
            Tuple of (orders list, total count)
        """
        query = self.db.query(SalesOrder).order_by(desc(SalesOrder.created_at))

        # Apply filters
        if status:
            query = query.filter(SalesOrder.status == status)

        if customer_id:
            query = query.filter(SalesOrder.customer_id == customer_id)

        if date_from:
            query = query.filter(SalesOrder.order_date >= date_from)

        if date_to:
            query = query.filter(SalesOrder.order_date <= date_to)

        # Apply search
        if search:
            search_filter = or_(
                SalesOrder.order_number.ilike(f"%{search}%"),
                SalesOrder.notes.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        # Get total count before pagination
        total = query.count()

        # Apply pagination
        orders = query.offset(skip).limit(limit).all()

        return orders, total

    def get_sales_order_by_id(self, order_id: int) -> SalesOrder:
        """
        Get sales order by ID.

        Args:
            order_id: Sales order ID

        Returns:
            SalesOrder instance

        Raises:
            EntityNotFoundError: If order not found
        """
        order = self.sales_order_repo.get(order_id)
        if not order:
            raise EntityNotFoundError("Sales order", order_id)
        return order

    def create_sales_order(
        self,
        sales_order: SalesOrderCreate,
        created_by: int
    ) -> SalesOrder:
        """
        Create new sales order with items.

        Args:
            sales_order: Sales order creation data
            created_by: User ID creating the order

        Returns:
            Created sales order

        Raises:
            EntityNotFoundError: If customer or product not found
            ValidationError: If validation fails
        """
        # Verify customer exists
        customer = self.customer_repo.get(sales_order.customer_id)
        if not customer:
            raise EntityNotFoundError("Customer", sales_order.customer_id)

        # Generate order number
        order_number = self.generate_order_number()

        # Create sales order
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

        self.db.add(db_order)
        self.db.flush()  # Get order ID

        # Add sales items
        total_subtotal = Decimal(0)
        for item_data in sales_order.sales_items:
            # Verify product exists
            product = self.product_repo.get(item_data.product_id)
            if not product:
                raise EntityNotFoundError("Product", item_data.product_id)

            # Calculate item totals
            totals = self.calculate_item_totals(
                item_data.quantity,
                item_data.unit_price,
                item_data.discount_percentage,
                item_data.discount_amount
            )

            # Create sales item
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

            self.db.add(sales_item)
            total_subtotal += totals["line_total"]

        # Calculate final totals
        db_order.subtotal = total_subtotal
        db_order.discount_amount = total_subtotal * (sales_order.discount_percentage / 100)
        subtotal_after_discount = total_subtotal - db_order.discount_amount
        db_order.tax_amount = subtotal_after_discount * (sales_order.tax_percentage / 100)
        db_order.total_amount = subtotal_after_discount + db_order.tax_amount

        self.db.commit()
        self.db.refresh(db_order)
        return db_order

    # ========================================================================
    # Order Lifecycle Operations
    # ========================================================================

    def confirm_sales_order(self, order_id: int, user_id: int) -> SalesOrder:
        """
        Confirm sales order and reserve inventory.

        Args:
            order_id: Sales order ID
            user_id: User ID confirming the order

        Returns:
            Updated sales order

        Raises:
            EntityNotFoundError: If order not found
            ValidationError: If order cannot be confirmed
        """
        db_order = self.get_sales_order_by_id(order_id)

        if db_order.status != "DRAFT":
            raise ValidationError(
                "Only draft orders can be confirmed",
                "يمكن تأكيد الطلبات المسودة فقط"
            )

        # Reserve inventory for each item
        try:
            for item in db_order.sales_items:
                InventoryService.reserve_stock(
                    self.db, item.product_id, db_order.warehouse_id, item.quantity
                )
        except Exception as e:
            # Release all reservations if any item fails
            for item in db_order.sales_items:
                try:
                    InventoryService.release_reservation(
                        self.db, item.product_id, db_order.warehouse_id, item.quantity
                    )
                except:
                    pass
            raise e

        # Update order status
        db_order.status = "CONFIRMED"
        self.db.commit()
        self.db.refresh(db_order)
        return db_order

    def ship_sales_order(self, order_id: int, user_id: int) -> SalesOrder:
        """
        Ship sales order and deduct inventory.

        Args:
            order_id: Sales order ID
            user_id: User ID shipping the order

        Returns:
            Updated sales order

        Raises:
            EntityNotFoundError: If order not found
            ValidationError: If order cannot be shipped
        """
        db_order = self.get_sales_order_by_id(order_id)

        if db_order.status != "CONFIRMED":
            raise ValidationError(
                "Only confirmed orders can be shipped",
                "يمكن شحن الطلبات المؤكدة فقط"
            )

        # Deduct inventory for each item
        for item in db_order.sales_items:
            # Release reservation first
            InventoryService.release_reservation(
                self.db, item.product_id, db_order.warehouse_id, item.quantity
            )

            # Deduct from inventory
            inventory_item = InventoryService.get_or_create_inventory_item(
                self.db, item.product_id, db_order.warehouse_id
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

            InventoryService.record_stock_movement(self.db, stock_movement)

            # Update delivered quantity
            item.delivered_quantity = item.quantity

        # Update order status
        db_order.status = "SHIPPED"
        self.db.commit()
        self.db.refresh(db_order)
        return db_order

    def cancel_sales_order(self, order_id: int, user_id: int) -> SalesOrder:
        """
        Cancel sales order and release reservations.

        Args:
            order_id: Sales order ID
            user_id: User ID cancelling the order

        Returns:
            Updated sales order

        Raises:
            EntityNotFoundError: If order not found
            ValidationError: If order cannot be cancelled
        """
        db_order = self.get_sales_order_by_id(order_id)

        if db_order.status in ["DELIVERED", "CANCELLED"]:
            raise ValidationError(
                "Cannot cancel delivered or already cancelled orders",
                "لا يمكن إلغاء الطلبات المسلمة أو الملغاة"
            )

        # Release inventory reservations if order is confirmed
        if db_order.status == "CONFIRMED":
            for item in db_order.sales_items:
                InventoryService.release_reservation(
                    self.db, item.product_id, db_order.warehouse_id, item.quantity
                )

        # Update order status
        db_order.status = "CANCELLED"
        self.db.commit()
        self.db.refresh(db_order)
        return db_order


# ============================================================================
# Dependency for FastAPI
# ============================================================================

from app.db.database import get_db


def get_sales_service(db: Session = Depends(get_db)) -> SalesService:
    """
    Dependency to get SalesService instance.

    Usage in routers:
        @router.get("/orders")
        def get_orders(
            service: SalesService = Depends(get_sales_service)
        ):
            orders, total = service.get_all_sales_orders()
            return orders
    """
    return SalesService(db)
