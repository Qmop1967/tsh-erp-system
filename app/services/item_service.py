"""
Item Service - Business Logic for Inventory Item Management

Created for Phase 5 P2 migration using Phase 4 patterns:
- Instance methods with BaseRepository
- Custom exceptions instead of HTTPException
- Pagination and search support

Author: Claude Code (Senior Software Engineer AI)
Date: January 7, 2025
Phase: 5 P2 - Items Router Migration
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import Depends

from app.models.migration import MigrationItem
from app.schemas.migration import ItemCreate, ItemUpdate
from app.repositories import BaseRepository
from app.exceptions import EntityNotFoundError


class ItemService:
    """
    Service for inventory item management.

    Handles all business logic for migration items (inventory items),
    replacing direct database operations in the router.
    """

    def __init__(self, db: Session):
        """
        Initialize item service.

        Args:
            db: Database session
        """
        self.db = db
        self.item_repo = BaseRepository(MigrationItem, db)

    # ========================================================================
    # Item CRUD Operations
    # ========================================================================

    def get_all_items(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category_id: Optional[int] = None
    ) -> Tuple[List[MigrationItem], int]:
        """
        Get all items with optional filters.

        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            search: Search term for name_en, name_ar, code
            category_id: Filter by category ID

        Returns:
            Tuple of (items list, total count)
        """
        # Build filters
        filters = {}
        if category_id is not None:
            filters['category_id'] = category_id

        # Apply search if provided
        if search:
            items = self.item_repo.search(
                search_term=search,
                search_fields=['name_en', 'name_ar', 'code'],
                skip=skip,
                limit=limit
            )
            # Get count for search results
            total = len(self.item_repo.search(
                search_term=search,
                search_fields=['name_en', 'name_ar', 'code'],
                skip=0,
                limit=10000
            ))
        else:
            items = self.item_repo.get_all(
                skip=skip,
                limit=limit,
                filters=filters
            )
            total = self.item_repo.get_count(filters=filters)

        return items, total

    def get_item_by_id(self, item_id: int) -> MigrationItem:
        """
        Get item by ID.

        Args:
            item_id: Item ID

        Returns:
            MigrationItem instance

        Raises:
            EntityNotFoundError: If item not found
        """
        item = self.item_repo.get(item_id)
        if not item:
            raise EntityNotFoundError("Item", item_id)
        return item

    def create_item(self, item_data: ItemCreate) -> MigrationItem:
        """
        Create new item.

        Args:
            item_data: Item creation data

        Returns:
            Created item
        """
        return self.item_repo.create(item_data.dict())

    def update_item(
        self,
        item_id: int,
        item_data: ItemUpdate
    ) -> MigrationItem:
        """
        Update existing item.

        Args:
            item_id: Item ID
            item_data: Item update data

        Returns:
            Updated item

        Raises:
            EntityNotFoundError: If item not found
        """
        # Verify item exists
        self.get_item_by_id(item_id)

        # Update item
        update_dict = item_data.dict(exclude_unset=True)
        return self.item_repo.update(item_id, update_dict)

    def delete_item(self, item_id: int) -> bool:
        """
        Hard delete item.

        Args:
            item_id: Item ID

        Returns:
            True if deleted

        Raises:
            EntityNotFoundError: If item not found
        """
        return self.item_repo.delete(item_id)


# ============================================================================
# Dependency for FastAPI
# ============================================================================

from app.db.database import get_db


def get_item_service(db: Session = Depends(get_db)) -> ItemService:
    """
    Dependency to get ItemService instance.

    Usage in routers:
        @router.get("/items")
        def get_items(
            service: ItemService = Depends(get_item_service)
        ):
            items, total = service.get_all_items()
            return items
    """
    return ItemService(db)
