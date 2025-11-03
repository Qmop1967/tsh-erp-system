"""
Mobile BFF Router
Optimized API endpoints for Flutter mobile apps
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.bff.mobile.schemas import (
    MobileHomeResponse,
    MobileProductDetail,
    MobileSearchResponse,
    MobileCategoryProductsResponse,
    MobileCheckoutResponse
)
from app.bff.mobile.aggregators import (
    HomeAggregator,
    ProductAggregator,
    CheckoutAggregator
)

router = APIRouter()


# ============================================================================
# Home Screen
# ============================================================================

@router.get(
    "/home",
    response_model=MobileHomeResponse,
    summary="Get home screen data",
    description="""
    Get complete home screen data in ONE call.

    Returns:
    - Featured products
    - Best sellers
    - New arrivals
    - Active promotions
    - Customer info (if authenticated)
    - Cart summary (if authenticated)

    This replaces 6+ separate API calls with a single optimized endpoint.
    """
)
async def get_home(
    customer_id: Optional[int] = Query(None, description="Customer ID for personalization"),
    branch_id: Optional[int] = Query(None, description="Branch ID for location filtering"),
    db: AsyncSession = Depends(get_db)
):
    """Get complete home screen data"""
    aggregator = HomeAggregator(db)
    return await aggregator.get_home_data(customer_id=customer_id, branch_id=branch_id)


# ============================================================================
# Product Endpoints
# ============================================================================

@router.get(
    "/products/{product_id}",
    response_model=MobileProductDetail,
    summary="Get product details",
    description="""
    Get complete product details with reviews.

    Returns:
    - Product info
    - Images
    - Stock status
    - Average rating
    - Review count
    - Specifications
    """
)
async def get_product(
    product_id: int,
    customer_id: Optional[int] = Query(None, description="Customer ID for personalization"),
    db: AsyncSession = Depends(get_db)
):
    """Get product details"""
    aggregator = ProductAggregator(db)
    product = await aggregator.get_product_detail(product_id=product_id, customer_id=customer_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.get(
    "/products/search",
    response_model=MobileSearchResponse,
    summary="Search products",
    description="""
    Search products with filters and pagination.

    Filters:
    - Query text (name, description, SKU)
    - Category
    - Branch
    - Price range
    """
)
async def search_products(
    q: str = Query(..., description="Search query", min_length=1),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    branch_id: Optional[int] = Query(None, description="Filter by branch"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    db: AsyncSession = Depends(get_db)
):
    """Search products"""
    aggregator = ProductAggregator(db)
    return await aggregator.search_products(
        query=q,
        page=page,
        page_size=page_size,
        branch_id=branch_id,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price
    )


@router.get(
    "/categories/{category_id}/products",
    response_model=MobileCategoryProductsResponse,
    summary="Get category products",
    description="""
    Get category with its products.

    Returns:
    - Category info
    - Products in category
    - Pagination
    """
)
async def get_category_products(
    category_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    branch_id: Optional[int] = Query(None, description="Filter by branch"),
    db: AsyncSession = Depends(get_db)
):
    """Get category with products"""
    aggregator = ProductAggregator(db)
    category = await aggregator.get_category_products(
        category_id=category_id,
        page=page,
        page_size=page_size,
        branch_id=branch_id
    )

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category


@router.get(
    "/products/{product_id}/related",
    response_model=list[MobileProductDetail],
    summary="Get related products",
    description="Get related products (same category)"
)
async def get_related_products(
    product_id: int,
    limit: int = Query(10, ge=1, le=20, description="Maximum results"),
    db: AsyncSession = Depends(get_db)
):
    """Get related products"""
    aggregator = ProductAggregator(db)
    return await aggregator.get_related_products(product_id=product_id, limit=limit)


# ============================================================================
# Checkout
# ============================================================================

@router.get(
    "/checkout",
    response_model=MobileCheckoutResponse,
    summary="Get checkout data",
    description="""
    Get complete checkout data in ONE call.

    Returns:
    - Cart with items
    - Customer addresses
    - Payment methods
    - Delivery options
    - Active promotions
    - Price summary

    This replaces 5+ separate API calls with a single optimized endpoint.
    """
)
async def get_checkout(
    customer_id: int = Query(..., description="Customer ID"),
    branch_id: Optional[int] = Query(None, description="Branch ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get complete checkout data"""
    aggregator = CheckoutAggregator(db)
    checkout = await aggregator.get_checkout_data(customer_id=customer_id, branch_id=branch_id)

    if not checkout:
        raise HTTPException(status_code=404, detail="Checkout data not available")

    return checkout


# ============================================================================
# Health Check
# ============================================================================

@router.get(
    "/health",
    summary="Health check",
    description="Check if mobile BFF is healthy"
)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "mobile-bff",
        "version": "1.0.0"
    }
