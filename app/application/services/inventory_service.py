"""
Inventory Service

Business logic layer for inventory operations using repository pattern.
"""

from typing import List, Optional
from datetime import date
from app.application.interfaces.repositories.inventory_repository import (
    IInventoryRepository,
    IStockMovementRepository
)
from app.application.dtos.inventory_dto import (
    InventoryItemResponseDTO,
    InventoryItemListResponseDTO,
    StockMovementResponseDTO,
    StockMovementListResponseDTO,
    StockUpdateDTO as InventoryStockUpdateDTO,
    StockTransferDTO,
    StockReserveDTO,
    StockReleaseDTO,
    InventorySearchDTO,
    StockMovementSearchDTO,
    InventorySummaryDTO,
    WarehouseStockSummaryDTO,
    StockValuationDTO,
)


class InventoryService:
    """
    Service class for inventory business logic.

    This service class handles all inventory-related business logic
    using the repository pattern for data access.
    """

    def __init__(
        self,
        inventory_repository: IInventoryRepository,
        stock_movement_repository: IStockMovementRepository
    ):
        """
        Initialize the service with repositories.

        Args:
            inventory_repository: Inventory repository implementation
            stock_movement_repository: Stock movement repository implementation
        """
        self.inventory_repo = inventory_repository
        self.movement_repo = stock_movement_repository

    async def get_inventory_item(
        self,
        product_id: int,
        warehouse_id: int
    ) -> Optional[InventoryItemResponseDTO]:
        """
        Get inventory item for a product in a warehouse.

        Args:
            product_id: Product ID
            warehouse_id: Warehouse ID

        Returns:
            Inventory item response DTO if found, None otherwise
        """
        item = await self.inventory_repo.get_by_product_and_warehouse(
            product_id, warehouse_id
        )
        if not item:
            return None
        return InventoryItemResponseDTO.model_validate(item)

    async def get_inventory_by_product(
        self,
        product_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> InventoryItemListResponseDTO:
        """
        Get all inventory items for a product across warehouses.

        Args:
            product_id: Product ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Inventory item list response DTO
        """
        items = await self.inventory_repo.get_by_product(
            product_id, skip=skip, limit=limit
        )
        # Get total for this product
        all_items = await self.inventory_repo.get_by_product(
            product_id, skip=0, limit=10000
        )
        total = len(all_items)

        return InventoryItemListResponseDTO(
            items=[InventoryItemResponseDTO.model_validate(i) for i in items],
            total=total,
            skip=skip,
            limit=limit
        )

    async def get_inventory_by_warehouse(
        self,
        warehouse_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> InventoryItemListResponseDTO:
        """
        Get all inventory items in a warehouse.

        Args:
            warehouse_id: Warehouse ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Inventory item list response DTO
        """
        items = await self.inventory_repo.get_by_warehouse(
            warehouse_id, skip=skip, limit=limit
        )
        total = await self.inventory_repo.count(warehouse_id=warehouse_id)

        return InventoryItemListResponseDTO(
            items=[InventoryItemResponseDTO.model_validate(i) for i in items],
            total=total,
            skip=skip,
            limit=limit
        )

    async def search_inventory(
        self,
        dto: InventorySearchDTO
    ) -> InventoryItemListResponseDTO:
        """
        Search inventory items with filters.

        Args:
            dto: Inventory search DTO

        Returns:
            Inventory item list response DTO
        """
        items = []
        total = 0

        if dto.low_stock:
            # Low stock items
            items = await self.inventory_repo.get_low_stock_items(
                warehouse_id=dto.warehouse_id,
                skip=dto.skip,
                limit=dto.limit
            )
            all_low = await self.inventory_repo.get_low_stock_items(
                warehouse_id=dto.warehouse_id,
                skip=0,
                limit=10000
            )
            total = len(all_low)
        elif dto.out_of_stock:
            # Out of stock items
            items = await self.inventory_repo.get_out_of_stock_items(
                warehouse_id=dto.warehouse_id,
                skip=dto.skip,
                limit=dto.limit
            )
            all_out = await self.inventory_repo.get_out_of_stock_items(
                warehouse_id=dto.warehouse_id,
                skip=0,
                limit=10000
            )
            total = len(all_out)
        elif dto.product_id and dto.warehouse_id:
            # Specific product and warehouse
            item = await self.inventory_repo.get_by_product_and_warehouse(
                dto.product_id, dto.warehouse_id
            )
            items = [item] if item else []
            total = len(items)
        elif dto.product_id:
            # Specific product
            items = await self.inventory_repo.get_by_product(
                dto.product_id, skip=dto.skip, limit=dto.limit
            )
            all_product = await self.inventory_repo.get_by_product(
                dto.product_id, skip=0, limit=10000
            )
            total = len(all_product)
        elif dto.warehouse_id:
            # Specific warehouse
            items = await self.inventory_repo.get_by_warehouse(
                dto.warehouse_id, skip=dto.skip, limit=dto.limit
            )
            total = await self.inventory_repo.count(warehouse_id=dto.warehouse_id)
        else:
            # All inventory items
            items = await self.inventory_repo.get_all(skip=dto.skip, limit=dto.limit)
            total = await self.inventory_repo.count()

        return InventoryItemListResponseDTO(
            items=[InventoryItemResponseDTO.model_validate(i) for i in items],
            total=total,
            skip=dto.skip,
            limit=dto.limit
        )

    async def update_stock(
        self,
        dto: InventoryStockUpdateDTO
    ) -> InventoryItemResponseDTO:
        """
        Update stock quantity.

        Args:
            dto: Stock update DTO

        Returns:
            Updated inventory item response DTO

        Raises:
            ValueError: If inventory item not found or validation fails
        """
        # Get or create inventory item
        item = await self.inventory_repo.get_by_product_and_warehouse(
            dto.product_id, dto.warehouse_id
        )

        if not item:
            raise ValueError(
                f"No inventory record found for product {dto.product_id} "
                f"in warehouse {dto.warehouse_id}"
            )

        # Validate stock levels for OUT movements
        if dto.movement_type == "OUT" and item.quantity_on_hand + dto.quantity_change < 0:
            raise ValueError(
                f"Insufficient stock. Available: {item.quantity_on_hand}, "
                f"Requested: {abs(dto.quantity_change)}"
            )

        # Update quantity
        updated_item = await self.inventory_repo.update_quantity(
            inventory_item_id=item.id,
            quantity_change=dto.quantity_change,
            movement_type=dto.movement_type,
            reference_type=dto.reference_type,
            reference_id=dto.reference_id,
            unit_cost=dto.unit_cost,
            notes=dto.notes,
            created_by=dto.created_by
        )

        return InventoryItemResponseDTO.model_validate(updated_item)

    async def transfer_stock(
        self,
        dto: StockTransferDTO
    ) -> bool:
        """
        Transfer stock between warehouses.

        Args:
            dto: Stock transfer DTO

        Returns:
            True if transfer successful

        Raises:
            ValueError: If validation fails
        """
        # Validate source has enough stock
        source_item = await self.inventory_repo.get_by_product_and_warehouse(
            dto.product_id, dto.from_warehouse_id
        )

        if not source_item:
            raise ValueError(
                f"No inventory found for product {dto.product_id} "
                f"in warehouse {dto.from_warehouse_id}"
            )

        if source_item.quantity_on_hand < dto.quantity:
            raise ValueError(
                f"Insufficient stock for transfer. Available: {source_item.quantity_on_hand}, "
                f"Required: {dto.quantity}"
            )

        # Perform transfer
        success = await self.inventory_repo.transfer_stock(
            product_id=dto.product_id,
            from_warehouse_id=dto.from_warehouse_id,
            to_warehouse_id=dto.to_warehouse_id,
            quantity=dto.quantity,
            unit_cost=dto.unit_cost,
            notes=dto.notes,
            created_by=dto.created_by
        )

        if not success:
            raise ValueError("Stock transfer failed")

        return True

    async def reserve_stock(
        self,
        dto: StockReserveDTO
    ) -> InventoryItemResponseDTO:
        """
        Reserve stock quantity.

        Args:
            dto: Stock reserve DTO

        Returns:
            Updated inventory item response DTO

        Raises:
            ValueError: If insufficient stock available
        """
        item = await self.inventory_repo.get_by_product_and_warehouse(
            dto.product_id, dto.warehouse_id
        )

        if not item:
            raise ValueError(
                f"No inventory found for product {dto.product_id} "
                f"in warehouse {dto.warehouse_id}"
            )

        updated_item = await self.inventory_repo.reserve_quantity(
            item.id, dto.quantity
        )

        return InventoryItemResponseDTO.model_validate(updated_item)

    async def release_stock(
        self,
        dto: StockReleaseDTO
    ) -> InventoryItemResponseDTO:
        """
        Release reserved stock.

        Args:
            dto: Stock release DTO

        Returns:
            Updated inventory item response DTO

        Raises:
            ValueError: If inventory item not found
        """
        item = await self.inventory_repo.get_by_product_and_warehouse(
            dto.product_id, dto.warehouse_id
        )

        if not item:
            raise ValueError(
                f"No inventory found for product {dto.product_id} "
                f"in warehouse {dto.warehouse_id}"
            )

        updated_item = await self.inventory_repo.release_quantity(
            item.id, dto.quantity
        )

        return InventoryItemResponseDTO.model_validate(updated_item)

    async def get_product_summary(
        self,
        product_id: int
    ) -> InventorySummaryDTO:
        """
        Get inventory summary for a product.

        Args:
            product_id: Product ID

        Returns:
            Inventory summary DTO
        """
        items = await self.inventory_repo.get_by_product(product_id, skip=0, limit=1000)

        total_quantity = sum(item.quantity_on_hand for item in items)
        total_reserved = sum(item.quantity_reserved for item in items)
        total_available = total_quantity - total_reserved

        return InventorySummaryDTO(
            product_id=product_id,
            total_quantity=float(total_quantity),
            total_reserved=float(total_reserved),
            total_available=float(total_available),
            warehouses=len(items)
        )

    async def get_warehouse_summary(
        self,
        warehouse_id: int
    ) -> WarehouseStockSummaryDTO:
        """
        Get stock summary for a warehouse.

        Args:
            warehouse_id: Warehouse ID

        Returns:
            Warehouse stock summary DTO
        """
        all_items = await self.inventory_repo.get_by_warehouse(
            warehouse_id, skip=0, limit=10000
        )
        low_stock = await self.inventory_repo.get_low_stock_items(
            warehouse_id=warehouse_id, skip=0, limit=10000
        )
        out_of_stock = await self.inventory_repo.get_out_of_stock_items(
            warehouse_id=warehouse_id, skip=0, limit=10000
        )

        total_quantity = sum(item.quantity_on_hand for item in all_items)

        return WarehouseStockSummaryDTO(
            warehouse_id=warehouse_id,
            total_products=len(all_items),
            total_quantity=float(total_quantity),
            low_stock_items=len(low_stock),
            out_of_stock_items=len(out_of_stock)
        )

    async def get_stock_valuation(
        self,
        product_id: Optional[int] = None,
        warehouse_id: Optional[int] = None
    ) -> List[StockValuationDTO]:
        """
        Get stock valuation.

        Args:
            product_id: Filter by product (optional)
            warehouse_id: Filter by warehouse (optional)

        Returns:
            List of stock valuation DTOs
        """
        if product_id and warehouse_id:
            item = await self.inventory_repo.get_by_product_and_warehouse(
                product_id, warehouse_id
            )
            items = [item] if item else []
        elif product_id:
            items = await self.inventory_repo.get_by_product(product_id, skip=0, limit=1000)
        elif warehouse_id:
            items = await self.inventory_repo.get_by_warehouse(warehouse_id, skip=0, limit=1000)
        else:
            items = await self.inventory_repo.get_all(skip=0, limit=1000)

        valuations = []
        for item in items:
            if item.average_cost:
                total_value = float(item.quantity_on_hand) * float(item.average_cost)
                valuations.append(
                    StockValuationDTO(
                        product_id=item.product_id,
                        warehouse_id=item.warehouse_id,
                        quantity_on_hand=float(item.quantity_on_hand),
                        average_cost=float(item.average_cost),
                        total_value=total_value
                    )
                )

        return valuations

    async def get_stock_movements(
        self,
        dto: StockMovementSearchDTO
    ) -> StockMovementListResponseDTO:
        """
        Get stock movements with filters.

        Args:
            dto: Stock movement search DTO

        Returns:
            Stock movement list response DTO
        """
        movements = []
        total = 0

        if dto.inventory_item_id:
            movements = await self.movement_repo.get_by_inventory_item(
                dto.inventory_item_id, skip=dto.skip, limit=dto.limit
            )
            all_movements = await self.movement_repo.get_by_inventory_item(
                dto.inventory_item_id, skip=0, limit=10000
            )
            total = len(all_movements)
        elif dto.movement_type:
            movements = await self.movement_repo.get_by_movement_type(
                dto.movement_type, skip=dto.skip, limit=dto.limit
            )
            total = await self.movement_repo.count(movement_type=dto.movement_type)
        elif dto.reference_type and dto.reference_id:
            movements = await self.movement_repo.get_by_reference(
                dto.reference_type, dto.reference_id
            )
            total = len(movements)
        elif dto.start_date and dto.end_date:
            movements = await self.movement_repo.get_by_date_range(
                dto.start_date,
                dto.end_date,
                dto.inventory_item_id,
                skip=dto.skip,
                limit=dto.limit
            )
            all_date_movements = await self.movement_repo.get_by_date_range(
                dto.start_date,
                dto.end_date,
                dto.inventory_item_id,
                skip=0,
                limit=10000
            )
            total = len(all_date_movements)
        else:
            movements = await self.movement_repo.get_all(skip=dto.skip, limit=dto.limit)
            total = await self.movement_repo.count()

        return StockMovementListResponseDTO(
            items=[StockMovementResponseDTO.model_validate(m) for m in movements],
            total=total,
            skip=dto.skip,
            limit=dto.limit
        )
