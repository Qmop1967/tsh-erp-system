"""
Warehouse Service - Business Logic for Warehouse Management

Moves database operations from router to service layer.
Uses BaseRepository for CRUD operations.

Author: Claude Code (Senior Software Engineer AI)
Date: January 7, 2025
Phase: 4 - Service Layer Consolidation
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.warehouse import Warehouse
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate
from app.repositories import BaseRepository
from app.exceptions import EntityNotFoundError, DuplicateEntityError, ValidationError


class WarehouseService:
    """
    Service for warehouse management.

    Handles all business logic for warehouses, replacing direct
    database operations in the router.
    """

    def __init__(self, db: Session):
        """
        Initialize warehouse service.

        Args:
            db: Database session
        """
        self.db = db
        self.repo = BaseRepository(Warehouse, db)

    def get_all_warehouses(
        self,
        skip: int = 0,
        limit: int = 100,
        branch_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Warehouse], int]:
        """
        Get all warehouses with optional filters.

        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            branch_id: Filter by branch ID
            search: Search term for name

        Returns:
            Tuple of (warehouses list, total count)
        """
        # Build filters
        filters = {}
        if branch_id is not None:
            filters['branch_id'] = branch_id

        # Apply search if provided
        if search:
            warehouses = self.repo.search(
                search_term=search,
                search_fields=['name'],
                skip=skip,
                limit=limit
            )
            total = len(self.repo.search(
                search_term=search,
                search_fields=['name'],
                skip=0,
                limit=10000
            ))
        else:
            warehouses = self.repo.get_all(
                skip=skip,
                limit=limit,
                filters=filters
            )
            total = self.repo.get_count(filters=filters)

        return warehouses, total

    def get_warehouse_by_id(self, warehouse_id: int) -> Warehouse:
        """
        Get warehouse by ID.

        Args:
            warehouse_id: Warehouse ID

        Returns:
            Warehouse instance

        Raises:
            EntityNotFoundError: If warehouse not found
        """
        return self.repo.get_or_404(
            warehouse_id,
            detail="Warehouse not found"
        )

    def create_warehouse(self, warehouse_data: WarehouseCreate) -> Warehouse:
        """
        Create new warehouse.

        Args:
            warehouse_data: Warehouse creation data

        Returns:
            Created warehouse

        Raises:
            ValidationError: If branch_id is invalid
        """
        # Validate branch exists
        from app.models.branch import Branch
        branch = self.db.query(Branch).filter(
            Branch.id == warehouse_data.branch_id
        ).first()
        if not branch:
            raise ValidationError(
                "Invalid branch_id",
                "معرف الفرع غير صالح"
            )

        # Create warehouse
        return self.repo.create(warehouse_data.dict())

    def update_warehouse(
        self,
        warehouse_id: int,
        warehouse_data: WarehouseUpdate
    ) -> Warehouse:
        """
        Update existing warehouse.

        Args:
            warehouse_id: Warehouse ID
            warehouse_data: Warehouse update data

        Returns:
            Updated warehouse

        Raises:
            EntityNotFoundError: If warehouse not found
            ValidationError: If branch_id is invalid
        """
        # Validate branch exists if being updated
        if hasattr(warehouse_data, 'branch_id') and warehouse_data.branch_id:
            from app.models.branch import Branch
            branch = self.db.query(Branch).filter(
                Branch.id == warehouse_data.branch_id
            ).first()
            if not branch:
                raise ValidationError(
                    "Invalid branch_id",
                    "معرف الفرع غير صالح"
                )

        # Update warehouse
        return self.repo.update(
            warehouse_id,
            warehouse_data.dict(exclude_unset=True)
        )

    def delete_warehouse(self, warehouse_id: int) -> bool:
        """
        Delete warehouse.

        Args:
            warehouse_id: Warehouse ID

        Returns:
            True if deleted

        Raises:
            EntityNotFoundError: If warehouse not found
        """
        return self.repo.delete(warehouse_id)

    def get_warehouses_by_branch(self, branch_id: int) -> List[Warehouse]:
        """
        Get all warehouses for a specific branch.

        Args:
            branch_id: Branch ID

        Returns:
            List of warehouses
        """
        return self.repo.get_all(
            filters={'branch_id': branch_id},
            skip=0,
            limit=1000
        )


# ============================================================================
# Dependency for FastAPI
# ============================================================================

def get_warehouse_service(db: Session) -> WarehouseService:
    """
    Dependency to get WarehouseService instance.

    Usage in routers:
        @router.get("/warehouses")
        def get_warehouses(
            service: WarehouseService = Depends(get_warehouse_service)
        ):
            warehouses = service.get_all_warehouses()
            return warehouses
    """
    return WarehouseService(db)
