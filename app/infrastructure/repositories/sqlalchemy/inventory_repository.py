"""
Inventory Repository SQLAlchemy Implementation

Concrete implementation of the inventory repository using SQLAlchemy.
"""

from typing import List, Optional
from datetime import date, datetime
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.interfaces.repositories.inventory_repository import (
    IInventoryRepository,
    IStockMovementRepository
)
from app.models import InventoryItem, StockMovement, Product


class InventoryRepository(IInventoryRepository):
    """
    SQLAlchemy implementation of the inventory repository.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.

        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    async def get_by_id(self, id: int) -> Optional[InventoryItem]:
        """Get an inventory item by ID."""
        result = await self.db.execute(
            select(InventoryItem).where(InventoryItem.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[InventoryItem]:
        """Get all inventory items with optional pagination and filtering."""
        query = select(InventoryItem)

        # Apply filters
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(InventoryItem, key):
                    conditions.append(getattr(InventoryItem, key) == value)
            if conditions:
                query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, entity: InventoryItem) -> InventoryItem:
        """Create a new inventory item."""
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update(self, id: int, entity: InventoryItem) -> Optional[InventoryItem]:
        """Update an existing inventory item."""
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
        """Delete an inventory item."""
        item = await self.get_by_id(id)
        if not item:
            return False

        await self.db.delete(item)
        await self.db.commit()
        return True

    async def exists(self, id: int) -> bool:
        """Check if an inventory item exists."""
        result = await self.db.execute(
            select(InventoryItem.id).where(InventoryItem.id == id)
        )
        return result.scalar_one_or_none() is not None

    async def count(self, **filters) -> int:
        """Count inventory items with optional filtering."""
        query = select(func.count(InventoryItem.id))

        # Apply filters
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(InventoryItem, key):
                    conditions.append(getattr(InventoryItem, key) == value)
            if conditions:
                query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        return result.scalar_one()

    async def find_one(self, **filters) -> Optional[InventoryItem]:
        """Find a single inventory item by filters."""
        query = select(InventoryItem)

        conditions = []
        for key, value in filters.items():
            if hasattr(InventoryItem, key):
                conditions.append(getattr(InventoryItem, key) == value)

        if conditions:
            query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def find_many(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[InventoryItem]:
        """Find multiple inventory items by filters."""
        return await self.get_all(skip=skip, limit=limit, **filters)

    # Inventory-specific methods

    async def get_by_product_and_warehouse(
        self,
        product_id: int,
        warehouse_id: int
    ) -> Optional[InventoryItem]:
        """Get inventory item by product and warehouse."""
        result = await self.db.execute(
            select(InventoryItem).where(
                and_(
                    InventoryItem.product_id == product_id,
                    InventoryItem.warehouse_id == warehouse_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_product(
        self,
        product_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[InventoryItem]:
        """Get all inventory items for a product across warehouses."""
        query = select(InventoryItem).where(InventoryItem.product_id == product_id)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_warehouse(
        self,
        warehouse_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[InventoryItem]:
        """Get all inventory items in a warehouse."""
        query = select(InventoryItem).where(InventoryItem.warehouse_id == warehouse_id)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_low_stock_items(
        self,
        warehouse_id: Optional[int] = None,
        threshold: Optional[float] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[InventoryItem]:
        """Get inventory items with low stock."""
        query = select(InventoryItem).join(Product)

        conditions = [InventoryItem.quantity_on_hand > 0]

        if threshold is not None:
            conditions.append(InventoryItem.quantity_on_hand <= threshold)
        else:
            # Use product reorder level if available
            conditions.append(
                InventoryItem.quantity_on_hand <= Product.reorder_level
            )

        if warehouse_id:
            conditions.append(InventoryItem.warehouse_id == warehouse_id)

        query = query.where(and_(*conditions))
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_out_of_stock_items(
        self,
        warehouse_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[InventoryItem]:
        """Get out of stock inventory items."""
        query = select(InventoryItem).where(InventoryItem.quantity_on_hand <= 0)

        if warehouse_id:
            query = query.where(InventoryItem.warehouse_id == warehouse_id)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_quantity(
        self,
        inventory_item_id: int,
        quantity_change: float,
        movement_type: str,
        reference_type: Optional[str] = None,
        reference_id: Optional[int] = None,
        unit_cost: Optional[float] = None,
        notes: Optional[str] = None,
        created_by: int = None
    ) -> Optional[InventoryItem]:
        """Update inventory quantity and create stock movement."""
        item = await self.get_by_id(inventory_item_id)
        if not item:
            return None

        # Update quantity
        item.quantity_on_hand += quantity_change

        # Update costs if provided
        if unit_cost is not None:
            item.last_cost = unit_cost
            # Simple moving average for average cost
            if item.average_cost:
                item.average_cost = (item.average_cost + unit_cost) / 2
            else:
                item.average_cost = unit_cost

        # Create stock movement record
        movement = StockMovement(
            inventory_item_id=inventory_item_id,
            movement_type=movement_type,
            reference_type=reference_type,
            reference_id=reference_id,
            quantity=quantity_change,
            unit_cost=unit_cost,
            notes=notes,
            created_by=created_by
        )
        self.db.add(movement)

        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def reserve_quantity(
        self,
        inventory_item_id: int,
        quantity: float
    ) -> Optional[InventoryItem]:
        """Reserve quantity for an order."""
        item = await self.get_by_id(inventory_item_id)
        if not item:
            return None

        # Check if enough quantity available
        if item.quantity_on_hand - item.quantity_reserved < quantity:
            raise ValueError("Insufficient quantity available to reserve")

        item.quantity_reserved += quantity
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def release_quantity(
        self,
        inventory_item_id: int,
        quantity: float
    ) -> Optional[InventoryItem]:
        """Release reserved quantity."""
        item = await self.get_by_id(inventory_item_id)
        if not item:
            return None

        item.quantity_reserved -= quantity
        if item.quantity_reserved < 0:
            item.quantity_reserved = 0

        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def get_total_quantity_for_product(self, product_id: int) -> float:
        """Get total quantity for a product across all warehouses."""
        result = await self.db.execute(
            select(func.sum(InventoryItem.quantity_on_hand))
            .where(InventoryItem.product_id == product_id)
        )
        total = result.scalar_one()
        return float(total) if total else 0.0

    async def get_available_quantity(
        self,
        product_id: int,
        warehouse_id: Optional[int] = None
    ) -> float:
        """Get available quantity (on_hand - reserved) for a product."""
        query = select(
            func.sum(InventoryItem.quantity_on_hand - InventoryItem.quantity_reserved)
        ).where(InventoryItem.product_id == product_id)

        if warehouse_id:
            query = query.where(InventoryItem.warehouse_id == warehouse_id)

        result = await self.db.execute(query)
        available = result.scalar_one()
        return float(available) if available else 0.0

    async def transfer_stock(
        self,
        product_id: int,
        from_warehouse_id: int,
        to_warehouse_id: int,
        quantity: float,
        unit_cost: Optional[float] = None,
        notes: Optional[str] = None,
        created_by: int = None
    ) -> bool:
        """Transfer stock between warehouses."""
        # Get source inventory item
        source_item = await self.get_by_product_and_warehouse(
            product_id, from_warehouse_id
        )
        if not source_item or source_item.quantity_on_hand < quantity:
            return False

        # Get or create destination inventory item
        dest_item = await self.get_by_product_and_warehouse(
            product_id, to_warehouse_id
        )
        if not dest_item:
            dest_item = InventoryItem(
                product_id=product_id,
                warehouse_id=to_warehouse_id,
                quantity_on_hand=0,
                quantity_reserved=0,
                quantity_ordered=0
            )
            self.db.add(dest_item)
            await self.db.flush()

        # Update quantities
        await self.update_quantity(
            source_item.id,
            -quantity,
            "TRANSFER",
            "TRANSFER",
            dest_item.id,
            unit_cost,
            f"Transfer to warehouse {to_warehouse_id}: {notes or ''}",
            created_by
        )

        await self.update_quantity(
            dest_item.id,
            quantity,
            "TRANSFER",
            "TRANSFER",
            source_item.id,
            unit_cost,
            f"Transfer from warehouse {from_warehouse_id}: {notes or ''}",
            created_by
        )

        return True


class StockMovementRepository(IStockMovementRepository):
    """
    SQLAlchemy implementation of the stock movement repository.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.

        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    async def get_by_id(self, id: int) -> Optional[StockMovement]:
        """Get a stock movement by ID."""
        result = await self.db.execute(
            select(StockMovement).where(StockMovement.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[StockMovement]:
        """Get all stock movements with optional pagination and filtering."""
        query = select(StockMovement)

        # Apply filters
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(StockMovement, key):
                    conditions.append(getattr(StockMovement, key) == value)
            if conditions:
                query = query.where(and_(*conditions))

        query = query.order_by(StockMovement.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, entity: StockMovement) -> StockMovement:
        """Create a new stock movement."""
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update(self, id: int, entity: StockMovement) -> Optional[StockMovement]:
        """Update an existing stock movement."""
        existing = await self.get_by_id(id)
        if not existing:
            return None

        for key, value in entity.__dict__.items():
            if not key.startswith('_') and key != 'id':
                setattr(existing, key, value)

        await self.db.commit()
        await self.db.refresh(existing)
        return existing

    async def delete(self, id: int) -> bool:
        """Delete a stock movement."""
        movement = await self.get_by_id(id)
        if not movement:
            return False

        await self.db.delete(movement)
        await self.db.commit()
        return True

    async def exists(self, id: int) -> bool:
        """Check if a stock movement exists."""
        result = await self.db.execute(
            select(StockMovement.id).where(StockMovement.id == id)
        )
        return result.scalar_one_or_none() is not None

    async def count(self, **filters) -> int:
        """Count stock movements with optional filtering."""
        query = select(func.count(StockMovement.id))

        # Apply filters
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(StockMovement, key):
                    conditions.append(getattr(StockMovement, key) == value)
            if conditions:
                query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        return result.scalar_one()

    async def find_one(self, **filters) -> Optional[StockMovement]:
        """Find a single stock movement by filters."""
        query = select(StockMovement)

        conditions = []
        for key, value in filters.items():
            if hasattr(StockMovement, key):
                conditions.append(getattr(StockMovement, key) == value)

        if conditions:
            query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def find_many(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[StockMovement]:
        """Find multiple stock movements by filters."""
        return await self.get_all(skip=skip, limit=limit, **filters)

    # Stock movement-specific methods

    async def get_by_inventory_item(
        self,
        inventory_item_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[StockMovement]:
        """Get stock movements for an inventory item."""
        query = select(StockMovement).where(
            StockMovement.inventory_item_id == inventory_item_id
        )
        query = query.order_by(StockMovement.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_movement_type(
        self,
        movement_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[StockMovement]:
        """Get stock movements by type."""
        query = select(StockMovement).where(
            StockMovement.movement_type == movement_type
        )
        query = query.order_by(StockMovement.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_date_range(
        self,
        start_date: date,
        end_date: date,
        inventory_item_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[StockMovement]:
        """Get stock movements within a date range."""
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        query = select(StockMovement).where(
            and_(
                StockMovement.created_at >= start_datetime,
                StockMovement.created_at <= end_datetime
            )
        )

        if inventory_item_id:
            query = query.where(StockMovement.inventory_item_id == inventory_item_id)

        query = query.order_by(StockMovement.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_reference(
        self,
        reference_type: str,
        reference_id: int
    ) -> List[StockMovement]:
        """Get stock movements by reference."""
        query = select(StockMovement).where(
            and_(
                StockMovement.reference_type == reference_type,
                StockMovement.reference_id == reference_id
            )
        )
        query = query.order_by(StockMovement.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
