"""
Pagination Utilities for TSH ERP System

Eliminates 38+ duplicate pagination parameter definitions.

Author: Claude Code (Senior Software Engineer AI)
Date: January 7, 2025
Phase: 4 - Query Utilities
"""

from typing import Generic, TypeVar, List, Optional
from fastapi import Query
from pydantic import BaseModel, Field

T = TypeVar('T')


class PaginationParams:
    """
    Reusable pagination parameters for FastAPI endpoints.

    Replaces 38+ occurrences of:
        skip: int = Query(0, ge=0)
        limit: int = Query(100, ge=1, le=1000)

    Usage:
        @router.get("/items")
        def get_items(
            pagination: PaginationParams = Depends()
        ):
            items = repo.get_all(
                skip=pagination.skip,
                limit=pagination.limit
            )
    """

    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(100, ge=1, le=1000, description="Maximum records to return")
    ):
        self.skip = skip
        self.limit = limit

    @property
    def page(self) -> int:
        """Calculate page number (1-indexed)."""
        return (self.skip // self.limit) + 1

    @property
    def offset(self) -> int:
        """Alias for skip (for clarity)."""
        return self.skip


class SearchParams(PaginationParams):
    """
    Pagination with search functionality.

    Usage:
        @router.get("/items")
        def get_items(
            params: SearchParams = Depends()
        ):
            if params.search:
                items = repo.search(params.search, ['name', 'sku'])
            else:
                items = repo.get_all(skip=params.skip, limit=params.limit)
    """

    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
        search: Optional[str] = Query(None, description="Search term")
    ):
        super().__init__(skip, limit)
        self.search = search


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Standard paginated response format.

    Provides consistent pagination metadata across all endpoints.

    Usage:
        items = repo.get_all(skip=0, limit=10)
        total = repo.get_count()

        return PaginatedResponse(
            items=items,
            total=total,
            page=1,
            page_size=10,
            pages=calculate_pages(total, 10)
        )
    """

    items: List[T] = Field(..., description="List of items in current page")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")

    class Config:
        from_attributes = True

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        skip: int,
        limit: int
    ) -> "PaginatedResponse[T]":
        """
        Factory method to create paginated response.

        Args:
            items: List of items for current page
            total: Total count of items
            skip: Number of skipped records
            limit: Page size

        Returns:
            PaginatedResponse instance
        """
        pages = (total + limit - 1) // limit  # Ceiling division
        page = (skip // limit) + 1

        return cls(
            items=items,
            total=total,
            page=page,
            page_size=limit,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1
        )


class FilterParams:
    """
    Common filter parameters for list endpoints.

    Usage:
        @router.get("/products")
        def get_products(
            filters: FilterParams = Depends(),
            pagination: PaginationParams = Depends()
        ):
            query = repo.query()
            if filters.is_active is not None:
                query = query.filter(Product.is_active == filters.is_active)
    """

    def __init__(
        self,
        is_active: Optional[bool] = Query(None, description="Filter by active status"),
        created_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
        created_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)")
    ):
        self.is_active = is_active
        self.created_from = created_from
        self.created_to = created_to


def calculate_pages(total: int, page_size: int) -> int:
    """
    Calculate total number of pages.

    Args:
        total: Total number of items
        page_size: Items per page

    Returns:
        Number of pages
    """
    if total == 0:
        return 0
    return (total + page_size - 1) // page_size


def calculate_skip(page: int, page_size: int) -> int:
    """
    Calculate skip value from page number.

    Args:
        page: Page number (1-indexed)
        page_size: Items per page

    Returns:
        Number of items to skip
    """
    return (page - 1) * page_size


# ============================================================================
# Usage Examples
# ============================================================================

"""
BEFORE (duplicated 38+ times):

    @router.get("/products")
    def get_products(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        search: str = Query(None),
        is_active: bool = Query(None),
        db: Session = Depends(get_db)
    ):
        query = db.query(Product)

        if is_active is not None:
            query = query.filter(Product.is_active == is_active)

        if search:
            query = query.filter(Product.name.ilike(f"%{search}%"))

        products = query.offset(skip).limit(limit).all()
        total = query.count()

        return {
            "items": products,
            "total": total,
            "page": skip // limit + 1,
            "pages": (total + limit - 1) // limit
        }


AFTER (centralized, clean):

    @router.get("/products", response_model=PaginatedResponse[ProductResponse])
    def get_products(
        params: SearchParams = Depends(),
        filters: FilterParams = Depends(),
        service: ProductService = Depends(get_product_service)
    ):
        items, total = service.get_products(
            search=params.search,
            is_active=filters.is_active,
            skip=params.skip,
            limit=params.limit
        )

        return PaginatedResponse.create(
            items=items,
            total=total,
            skip=params.skip,
            limit=params.limit
        )


BENEFITS:
✅ -38 duplicate parameter definitions
✅ Consistent pagination across all endpoints
✅ Type-safe parameters
✅ Auto-generated OpenAPI docs
✅ Reusable filter logic
✅ Standard response format
"""
