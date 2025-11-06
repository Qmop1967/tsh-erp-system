"""
Branch Service - Business Logic for Branch Management

Moves database operations from router to service layer.
Uses BaseRepository for CRUD operations.

Author: Claude Code (Senior Software Engineer AI)
Date: January 7, 2025
Phase: 4 - Service Layer Consolidation
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import Depends

from app.models.branch import Branch
from app.schemas.branch import BranchCreate, BranchUpdate
from app.repositories import BaseRepository
from app.exceptions import EntityNotFoundError, DuplicateEntityError


class BranchService:
    """
    Service for branch management.

    Handles all business logic for branches, replacing direct
    database operations in the router.
    """

    def __init__(self, db: Session):
        """
        Initialize branch service.

        Args:
            db: Database session
        """
        self.db = db
        self.repo = BaseRepository(Branch, db)

    def get_all_branches(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Branch], int]:
        """
        Get all branches with optional filters.

        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            is_active: Filter by active status
            search: Search term for name or code

        Returns:
            Tuple of (branches list, total count)
        """
        # Build filters
        filters = {}
        if is_active is not None:
            filters['is_active'] = is_active

        # Apply search if provided
        if search:
            branches = self.repo.search(
                search_term=search,
                search_fields=['name', 'code', 'city'],
                skip=skip,
                limit=limit
            )
            # Get count for search results
            total = len(self.repo.search(
                search_term=search,
                search_fields=['name', 'code', 'city'],
                skip=0,
                limit=10000  # Large number to get all for count
            ))
        else:
            branches = self.repo.get_all(
                skip=skip,
                limit=limit,
                filters=filters
            )
            total = self.repo.get_count(filters=filters)

        return branches, total

    def get_branch_by_id(self, branch_id: int) -> Branch:
        """
        Get branch by ID.

        Args:
            branch_id: Branch ID

        Returns:
            Branch instance

        Raises:
            EntityNotFoundError: If branch not found
        """
        return self.repo.get_or_404(
            branch_id,
            detail="Branch not found"
        )

    def create_branch(self, branch_data: BranchCreate) -> Branch:
        """
        Create new branch.

        Args:
            branch_data: Branch creation data

        Returns:
            Created branch

        Raises:
            DuplicateEntityError: If branch code already exists
        """
        # Validate unique code
        if hasattr(branch_data, 'code') and branch_data.code:
            self.repo.validate_unique(
                field='code',
                value=branch_data.code,
                error_message="Branch code already exists"
            )

        # Create branch
        return self.repo.create(branch_data.dict())

    def update_branch(
        self,
        branch_id: int,
        branch_data: BranchUpdate
    ) -> Branch:
        """
        Update existing branch.

        Args:
            branch_id: Branch ID
            branch_data: Branch update data

        Returns:
            Updated branch

        Raises:
            EntityNotFoundError: If branch not found
            DuplicateEntityError: If new code conflicts with existing
        """
        # Validate unique code if being updated
        if hasattr(branch_data, 'code') and branch_data.code:
            self.repo.validate_unique(
                field='code',
                value=branch_data.code,
                exclude_id=branch_id,
                error_message="Branch code already exists"
            )

        # Update branch
        return self.repo.update(
            branch_id,
            branch_data.dict(exclude_unset=True)
        )

    def delete_branch(self, branch_id: int) -> bool:
        """
        Delete branch (hard delete).

        Args:
            branch_id: Branch ID

        Returns:
            True if deleted

        Raises:
            EntityNotFoundError: If branch not found
        """
        return self.repo.delete(branch_id)

    def deactivate_branch(self, branch_id: int) -> Branch:
        """
        Soft delete branch (set is_active=False).

        Args:
            branch_id: Branch ID

        Returns:
            Deactivated branch

        Raises:
            EntityNotFoundError: If branch not found
        """
        return self.repo.soft_delete(branch_id)

    def activate_branch(self, branch_id: int) -> Branch:
        """
        Activate a deactivated branch.

        Args:
            branch_id: Branch ID

        Returns:
            Activated branch

        Raises:
            EntityNotFoundError: If branch not found
        """
        return self.repo.update(branch_id, {'is_active': True})

    def get_active_branches(self) -> List[Branch]:
        """
        Get all active branches (no pagination).

        Returns:
            List of active branches
        """
        return self.repo.get_all(
            filters={'is_active': True},
            skip=0,
            limit=1000  # Large limit for dropdown/select use cases
        )

    def branch_exists(self, code: str) -> bool:
        """
        Check if branch with given code exists.

        Args:
            code: Branch code

        Returns:
            True if exists
        """
        return self.repo.exists({'code': code})


# ============================================================================
# Dependency for FastAPI
# ============================================================================

from app.db.database import get_db


def get_branch_service(db: Session = Depends(get_db)) -> BranchService:
    """
    Dependency to get BranchService instance.

    Usage in routers:
        @router.get("/branches")
        def get_branches(
            service: BranchService = Depends(get_branch_service)
        ):
            branches = service.get_all_branches()
            return branches
    """
    return BranchService(db)


# ============================================================================
# Usage Example
# ============================================================================

"""
BEFORE (in router, ~50 lines):

    @router.get("/branches")
    def get_branches(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: Session = Depends(get_db)
    ):
        branches = db.query(Branch).offset(skip).limit(limit).all()
        return branches

    @router.post("/branches")
    def create_branch(
        branch: BranchCreate,
        db: Session = Depends(get_db)
    ):
        db_branch = Branch(**branch.dict())
        db.add(db_branch)
        db.commit()
        db.refresh(db_branch)
        return db_branch

    @router.put("/branches/{branch_id}")
    def update_branch(
        branch_id: int,
        branch: BranchUpdate,
        db: Session = Depends(get_db)
    ):
        db_branch = db.query(Branch).filter(Branch.id == branch_id).first()
        if not db_branch:
            raise HTTPException(status_code=404, detail="Branch not found")

        for field, value in branch.dict(exclude_unset=True).items():
            setattr(db_branch, field, value)

        db.commit()
        db.refresh(db_branch)
        return db_branch


AFTER (in router, ~20 lines):

    @router.get("/branches", response_model=PaginatedResponse[BranchResponse])
    def get_branches(
        params: PaginationParams = Depends(),
        service: BranchService = Depends(get_branch_service)
    ):
        branches, total = service.get_all_branches(
            skip=params.skip,
            limit=params.limit
        )
        return PaginatedResponse.create(branches, total, params.skip, params.limit)

    @router.post("/branches", response_model=BranchResponse)
    def create_branch(
        branch: BranchCreate,
        service: BranchService = Depends(get_branch_service)
    ):
        return service.create_branch(branch)

    @router.put("/branches/{branch_id}", response_model=BranchResponse)
    def update_branch(
        branch_id: int,
        branch: BranchUpdate,
        service: BranchService = Depends(get_branch_service)
    ):
        return service.update_branch(branch_id, branch)


BENEFITS:
✅ Business logic separated from routing
✅ Easier to test (mock service, not database)
✅ Reusable across multiple routers/endpoints
✅ Consistent error handling
✅ Type-safe operations
"""
