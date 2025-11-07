"""
Order Repository SQLAlchemy Implementation

Concrete implementation of the order repository using SQLAlchemy.
"""

from typing import List, Optional
from datetime import date, datetime
from sqlalchemy import select, or_, and_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.interfaces.repositories.order_repository import IOrderRepository
from app.models import SalesOrder, Customer


class OrderRepository(IOrderRepository):
    """
    SQLAlchemy implementation of the order repository.

    This class provides concrete implementations of all order
    data access operations using SQLAlchemy ORM.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.

        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    async def get_by_id(self, id: int) -> Optional[SalesOrder]:
        """Get an order by ID."""
        result = await self.db.execute(
            select(SalesOrder).where(SalesOrder.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[SalesOrder]:
        """Get all orders with optional pagination and filtering."""
        query = select(SalesOrder)

        # Apply filters
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(SalesOrder, key):
                    conditions.append(getattr(SalesOrder, key) == value)
            if conditions:
                query = query.where(and_(*conditions))

        query = query.order_by(SalesOrder.order_date.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, entity: SalesOrder) -> SalesOrder:
        """Create a new order."""
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update(self, id: int, entity: SalesOrder) -> Optional[SalesOrder]:
        """Update an existing order."""
        existing = await self.get_by_id(id)
        if not existing:
            return None

        # Update fields
        for key, value in entity.__dict__.items():
            if not key.startswith('_') and key != 'id':
                setattr(existing, key, value)

        await self.db.commit()
        await self.db.refresh(existing)
        return existing

    async def delete(self, id: int) -> bool:
        """Delete an order."""
        order = await self.get_by_id(id)
        if not order:
            return False

        await self.db.delete(order)
        await self.db.commit()
        return True

    async def exists(self, id: int) -> bool:
        """Check if an order exists."""
        result = await self.db.execute(
            select(SalesOrder.id).where(SalesOrder.id == id)
        )
        return result.scalar_one_or_none() is not None

    async def count(self, **filters) -> int:
        """Count orders with optional filtering."""
        query = select(func.count(SalesOrder.id))

        # Apply filters
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(SalesOrder, key):
                    conditions.append(getattr(SalesOrder, key) == value)
            if conditions:
                query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        return result.scalar_one()

    async def find_one(self, **filters) -> Optional[SalesOrder]:
        """Find a single order by filters."""
        query = select(SalesOrder)

        conditions = []
        for key, value in filters.items():
            if hasattr(SalesOrder, key):
                conditions.append(getattr(SalesOrder, key) == value)

        if conditions:
            query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def find_many(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[SalesOrder]:
        """Find multiple orders by filters."""
        return await self.get_all(skip=skip, limit=limit, **filters)

    # Order-specific methods

    async def get_by_order_number(self, order_number: str) -> Optional[SalesOrder]:
        """Get an order by order number."""
        result = await self.db.execute(
            select(SalesOrder).where(SalesOrder.order_number == order_number)
        )
        return result.scalar_one_or_none()

    async def get_by_customer(
        self,
        customer_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[SalesOrder]:
        """Get orders for a specific customer."""
        query = select(SalesOrder).where(SalesOrder.customer_id == customer_id)

        if status:
            query = query.where(SalesOrder.status == status)

        query = query.order_by(SalesOrder.order_date.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[SalesOrder]:
        """Get orders by status."""
        query = select(SalesOrder).where(SalesOrder.status == status)
        query = query.order_by(SalesOrder.order_date.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_payment_status(
        self,
        payment_status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[SalesOrder]:
        """Get orders by payment status."""
        query = select(SalesOrder).where(SalesOrder.payment_status == payment_status)
        query = query.order_by(SalesOrder.order_date.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_date_range(
        self,
        start_date: date,
        end_date: date,
        skip: int = 0,
        limit: int = 100
    ) -> List[SalesOrder]:
        """Get orders within a date range."""
        query = select(SalesOrder).where(
            and_(
                SalesOrder.order_date >= start_date,
                SalesOrder.order_date <= end_date
            )
        )
        query = query.order_by(SalesOrder.order_date.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_branch(
        self,
        branch_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[SalesOrder]:
        """Get orders for a specific branch."""
        query = select(SalesOrder).where(SalesOrder.branch_id == branch_id)
        query = query.order_by(SalesOrder.order_date.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_salesperson(
        self,
        salesperson_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[SalesOrder]:
        """Get orders created by a specific salesperson."""
        query = select(SalesOrder).where(SalesOrder.created_by == salesperson_id)
        query = query.order_by(SalesOrder.order_date.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_pending_orders(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[SalesOrder]:
        """Get pending orders (DRAFT status)."""
        query = select(SalesOrder).where(SalesOrder.status == "DRAFT")
        query = query.order_by(SalesOrder.order_date.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_overdue_orders(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[SalesOrder]:
        """Get overdue orders (expected delivery date passed)."""
        today = date.today()
        query = select(SalesOrder).where(
            and_(
                SalesOrder.expected_delivery_date < today,
                SalesOrder.status.in_(["CONFIRMED", "SHIPPED"]),
                SalesOrder.actual_delivery_date.is_(None)
            )
        )
        query = query.order_by(SalesOrder.expected_delivery_date.asc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[SalesOrder]:
        """Search orders by order number or customer name."""
        search_pattern = f"%{query}%"

        sql_query = select(SalesOrder).join(Customer).where(
            or_(
                SalesOrder.order_number.ilike(search_pattern),
                Customer.name.ilike(search_pattern)
            )
        )

        sql_query = sql_query.order_by(SalesOrder.order_date.desc())
        sql_query = sql_query.offset(skip).limit(limit)
        result = await self.db.execute(sql_query)
        return list(result.scalars().all())

    async def count_by_status(self, status: str) -> int:
        """Count orders by status."""
        query = select(func.count(SalesOrder.id)).where(SalesOrder.status == status)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def count_by_customer(
        self,
        customer_id: int,
        status: Optional[str] = None
    ) -> int:
        """Count orders for a customer."""
        query = select(func.count(SalesOrder.id)).where(
            SalesOrder.customer_id == customer_id
        )

        if status:
            query = query.where(SalesOrder.status == status)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_total_sales_amount(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        customer_id: Optional[int] = None
    ) -> float:
        """Get total sales amount with optional filters."""
        query = select(func.sum(SalesOrder.total_amount))

        conditions = []
        if start_date:
            conditions.append(SalesOrder.order_date >= start_date)
        if end_date:
            conditions.append(SalesOrder.order_date <= end_date)
        if customer_id:
            conditions.append(SalesOrder.customer_id == customer_id)

        # Only count confirmed orders
        conditions.append(SalesOrder.status.in_(["CONFIRMED", "SHIPPED", "DELIVERED"]))

        if conditions:
            query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        total = result.scalar_one()
        return float(total) if total else 0.0

    async def update_order_status(
        self,
        order_id: int,
        status: str
    ) -> Optional[SalesOrder]:
        """Update order status."""
        order = await self.get_by_id(order_id)
        if not order:
            return None

        order.status = status

        # If status is DELIVERED, set actual delivery date
        if status == "DELIVERED" and not order.actual_delivery_date:
            order.actual_delivery_date = date.today()

        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def update_payment_status(
        self,
        order_id: int,
        payment_status: str,
        paid_amount: Optional[float] = None
    ) -> Optional[SalesOrder]:
        """Update payment status and paid amount."""
        order = await self.get_by_id(order_id)
        if not order:
            return None

        order.payment_status = payment_status
        if paid_amount is not None:
            order.paid_amount = paid_amount

            # Auto-update payment status based on amount
            if order.paid_amount >= order.total_amount:
                order.payment_status = "PAID"
            elif order.paid_amount > 0:
                order.payment_status = "PARTIAL"

        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def get_with_items(self, order_id: int) -> Optional[SalesOrder]:
        """Get order with its items eagerly loaded."""
        result = await self.db.execute(
            select(SalesOrder)
            .options(selectinload(SalesOrder.sales_items))
            .where(SalesOrder.id == order_id)
        )
        return result.scalar_one_or_none()
