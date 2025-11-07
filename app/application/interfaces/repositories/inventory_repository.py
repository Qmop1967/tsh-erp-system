"""
Inventory Repository Interface

Defines the contract for inventory repository implementations.
"""

from abc import abstractmethod
from typing import List, Optional
from datetime import date
from app.application.interfaces.repositories.base_repository import IBaseRepository
from app.models import InventoryItem, StockMovement


class IInventoryRepository(IBaseRepository[InventoryItem, int]):
    """
    Inventory repository interface for data access operations.

    This interface extends the base repository with inventory-specific
    operations for managing stock levels, movements, and availability.
    """

    @abstractmethod
    async def get_by_product_and_warehouse(
        self,
        product_id: int,
        warehouse_id: int
    ) -> Optional[InventoryItem]:
        """
        Get inventory item by product and warehouse.

        Args:
            product_id: Product ID
            warehouse_id: Warehouse ID

        Returns:
            Inventory item if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_product(
        self,
        product_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[InventoryItem]:
        """
        Get all inventory items for a product across warehouses.

        Args:
            product_id: Product ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of inventory items
        """
        pass

    @abstractmethod
    async def get_by_warehouse(
        self,
        warehouse_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[InventoryItem]:
        """
        Get all inventory items in a warehouse.

        Args:
            warehouse_id: Warehouse ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of inventory items
        """
        pass

    @abstractmethod
    async def get_low_stock_items(
        self,
        warehouse_id: Optional[int] = None,
        threshold: Optional[float] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[InventoryItem]:
        """
        Get inventory items with low stock.

        Args:
            warehouse_id: Filter by warehouse (optional)
            threshold: Stock threshold (optional)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of low stock inventory items
        """
        pass

    @abstractmethod
    async def get_out_of_stock_items(
        self,
        warehouse_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[InventoryItem]:
        """
        Get out of stock inventory items.

        Args:
            warehouse_id: Filter by warehouse (optional)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of out of stock inventory items
        """
        pass

    @abstractmethod
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
        """
        Update inventory quantity and create stock movement.

        Args:
            inventory_item_id: Inventory item ID
            quantity_change: Quantity change (positive for IN, negative for OUT)
            movement_type: Movement type (IN, OUT, TRANSFER, ADJUSTMENT)
            reference_type: Reference type (optional)
            reference_id: Reference ID (optional)
            unit_cost: Unit cost (optional)
            notes: Movement notes (optional)
            created_by: User ID who created the movement

        Returns:
            Updated inventory item if found, None otherwise
        """
        pass

    @abstractmethod
    async def reserve_quantity(
        self,
        inventory_item_id: int,
        quantity: float
    ) -> Optional[InventoryItem]:
        """
        Reserve quantity for an order.

        Args:
            inventory_item_id: Inventory item ID
            quantity: Quantity to reserve

        Returns:
            Updated inventory item if found, None otherwise
        """
        pass

    @abstractmethod
    async def release_quantity(
        self,
        inventory_item_id: int,
        quantity: float
    ) -> Optional[InventoryItem]:
        """
        Release reserved quantity.

        Args:
            inventory_item_id: Inventory item ID
            quantity: Quantity to release

        Returns:
            Updated inventory item if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_total_quantity_for_product(self, product_id: int) -> float:
        """
        Get total quantity for a product across all warehouses.

        Args:
            product_id: Product ID

        Returns:
            Total quantity
        """
        pass

    @abstractmethod
    async def get_available_quantity(
        self,
        product_id: int,
        warehouse_id: Optional[int] = None
    ) -> float:
        """
        Get available quantity (on_hand - reserved) for a product.

        Args:
            product_id: Product ID
            warehouse_id: Warehouse ID (optional, if None returns total across all warehouses)

        Returns:
            Available quantity
        """
        pass

    @abstractmethod
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
        """
        Transfer stock between warehouses.

        Args:
            product_id: Product ID
            from_warehouse_id: Source warehouse ID
            to_warehouse_id: Destination warehouse ID
            quantity: Quantity to transfer
            unit_cost: Unit cost (optional)
            notes: Transfer notes (optional)
            created_by: User ID who created the transfer

        Returns:
            True if transfer successful, False otherwise
        """
        pass


class IStockMovementRepository(IBaseRepository[StockMovement, int]):
    """
    Stock movement repository interface for data access operations.
    """

    @abstractmethod
    async def get_by_inventory_item(
        self,
        inventory_item_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[StockMovement]:
        """
        Get stock movements for an inventory item.

        Args:
            inventory_item_id: Inventory item ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of stock movements
        """
        pass

    @abstractmethod
    async def get_by_movement_type(
        self,
        movement_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[StockMovement]:
        """
        Get stock movements by type.

        Args:
            movement_type: Movement type (IN, OUT, TRANSFER, ADJUSTMENT)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of stock movements
        """
        pass

    @abstractmethod
    async def get_by_date_range(
        self,
        start_date: date,
        end_date: date,
        inventory_item_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[StockMovement]:
        """
        Get stock movements within a date range.

        Args:
            start_date: Start date
            end_date: End date
            inventory_item_id: Filter by inventory item (optional)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of stock movements
        """
        pass

    @abstractmethod
    async def get_by_reference(
        self,
        reference_type: str,
        reference_id: int
    ) -> List[StockMovement]:
        """
        Get stock movements by reference.

        Args:
            reference_type: Reference type (SALE, PURCHASE, etc.)
            reference_id: Reference ID

        Returns:
            List of stock movements
        """
        pass
