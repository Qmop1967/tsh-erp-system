"""
Product Router V2

Clean architecture implementation of product endpoints using repository pattern.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.services.product_service import ProductService
from app.application.dtos.product_dto import (
    ProductCreateDTO,
    ProductUpdateDTO,
    ProductResponseDTO,
    ProductListResponseDTO,
    ProductSearchDTO,
    ProductSummaryDTO,
    StockUpdateDTO,
    ProductStockStatusDTO,
)
from app.core.dependencies import get_product_service

router = APIRouter(prefix="/v2/products", tags=["products-v2"])


@router.get("", response_model=ProductListResponseDTO)
async def get_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    service: ProductService = Depends(get_product_service)
):
    """
    Get all products with optional filtering.

    Args:
        skip: Number of records to skip
        limit: Maximum records to return
        is_active: Filter by active status
        service: Product service dependency

    Returns:
        Product list response
    """
    return await service.get_all_products(
        skip=skip,
        limit=limit,
        is_active=is_active
    )


@router.get("/search", response_model=ProductListResponseDTO)
async def search_products(
    query: Optional[str] = Query(None, description="Search query"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    supplier_id: Optional[int] = Query(None, description="Filter by supplier"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    low_stock: Optional[bool] = Query(None, description="Filter low stock products"),
    out_of_stock: Optional[bool] = Query(None, description="Filter out of stock products"),
    is_featured: Optional[bool] = Query(None, description="Filter featured products"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    service: ProductService = Depends(get_product_service)
):
    """
    Search products with advanced filters.

    Args:
        query: Text search query (searches name, SKU, barcode, description)
        is_active: Filter by active status
        category_id: Filter by category
        supplier_id: Filter by supplier
        min_price: Minimum price
        max_price: Maximum price
        low_stock: Filter low stock products
        out_of_stock: Filter out of stock products
        is_featured: Filter featured products
        skip: Number of records to skip
        limit: Maximum records to return
        service: Product service dependency

    Returns:
        Product list response
    """
    search_dto = ProductSearchDTO(
        query=query,
        is_active=is_active,
        category_id=category_id,
        supplier_id=supplier_id,
        min_price=min_price,
        max_price=max_price,
        low_stock=low_stock,
        out_of_stock=out_of_stock,
        is_featured=is_featured,
        skip=skip,
        limit=limit
    )
    return await service.search_products(search_dto)


@router.get("/active/summary", response_model=List[ProductSummaryDTO])
async def get_active_products_summary(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    service: ProductService = Depends(get_product_service)
):
    """
    Get summary of active products.

    Args:
        skip: Number of records to skip
        limit: Maximum records to return
        service: Product service dependency

    Returns:
        List of product summaries
    """
    return await service.get_active_products_summary(skip=skip, limit=limit)


@router.get("/featured", response_model=ProductListResponseDTO)
async def get_featured_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    service: ProductService = Depends(get_product_service)
):
    """
    Get featured products (for e-commerce).

    Args:
        skip: Number of records to skip
        limit: Maximum records to return
        service: Product service dependency

    Returns:
        Product list response
    """
    return await service.get_featured_products(skip=skip, limit=limit)


@router.get("/low-stock", response_model=List[ProductStockStatusDTO])
async def get_low_stock_products(
    threshold: Optional[int] = Query(None, ge=0, description="Stock threshold"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    service: ProductService = Depends(get_product_service)
):
    """
    Get products with low stock levels.

    Args:
        threshold: Stock threshold (uses reorder_level if not provided)
        skip: Number of records to skip
        limit: Maximum records to return
        service: Product service dependency

    Returns:
        List of low stock products with status
    """
    return await service.get_low_stock_products(
        threshold=threshold,
        skip=skip,
        limit=limit
    )


@router.get("/out-of-stock", response_model=List[ProductStockStatusDTO])
async def get_out_of_stock_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    service: ProductService = Depends(get_product_service)
):
    """
    Get out of stock products.

    Args:
        skip: Number of records to skip
        limit: Maximum records to return
        service: Product service dependency

    Returns:
        List of out of stock products with status
    """
    return await service.get_out_of_stock_products(skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductResponseDTO)
async def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    """
    Get a product by ID.

    Args:
        product_id: Product ID
        service: Product service dependency

    Returns:
        Product response

    Raises:
        HTTPException: 404 if product not found
    """
    product = await service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return product


@router.get("/{product_id}/stock-status", response_model=ProductStockStatusDTO)
async def get_product_stock_status(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    """
    Get product stock status.

    Args:
        product_id: Product ID
        service: Product service dependency

    Returns:
        Product stock status

    Raises:
        HTTPException: 404 if product not found
    """
    stock_status = await service.get_product_stock_status(product_id)
    if not stock_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return stock_status


@router.get("/sku/{sku}", response_model=ProductResponseDTO)
async def get_product_by_sku(
    sku: str,
    service: ProductService = Depends(get_product_service)
):
    """
    Get a product by SKU.

    Args:
        sku: Product SKU
        service: Product service dependency

    Returns:
        Product response

    Raises:
        HTTPException: 404 if product not found
    """
    product = await service.get_product_by_sku(sku)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU {sku} not found"
        )
    return product


@router.get("/barcode/{barcode}", response_model=ProductResponseDTO)
async def get_product_by_barcode(
    barcode: str,
    service: ProductService = Depends(get_product_service)
):
    """
    Get a product by barcode.

    Args:
        barcode: Product barcode
        service: Product service dependency

    Returns:
        Product response

    Raises:
        HTTPException: 404 if product not found
    """
    product = await service.get_product_by_barcode(barcode)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with barcode {barcode} not found"
        )
    return product


@router.get("/category/{category_id}", response_model=ProductListResponseDTO)
async def get_products_by_category(
    category_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    service: ProductService = Depends(get_product_service)
):
    """
    Get products in a category.

    Args:
        category_id: Category ID
        skip: Number of records to skip
        limit: Maximum records to return
        is_active: Filter by active status
        service: Product service dependency

    Returns:
        Product list response
    """
    return await service.get_products_by_category(
        category_id=category_id,
        skip=skip,
        limit=limit,
        is_active=is_active
    )


@router.post("", response_model=ProductResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_product(
    dto: ProductCreateDTO,
    service: ProductService = Depends(get_product_service)
):
    """
    Create a new product.

    Args:
        dto: Product creation data
        service: Product service dependency

    Returns:
        Created product response

    Raises:
        HTTPException: 400 if validation fails or duplicate exists
    """
    try:
        return await service.create_product(dto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{product_id}", response_model=ProductResponseDTO)
async def update_product(
    product_id: int,
    dto: ProductUpdateDTO,
    service: ProductService = Depends(get_product_service)
):
    """
    Update an existing product.

    Args:
        product_id: Product ID
        dto: Product update data
        service: Product service dependency

    Returns:
        Updated product response

    Raises:
        HTTPException: 404 if product not found, 400 if validation fails
    """
    try:
        product = await service.update_product(product_id, dto)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        return product
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    """
    Delete a product (soft delete).

    Args:
        product_id: Product ID
        service: Product service dependency

    Raises:
        HTTPException: 404 if product not found
    """
    deleted = await service.delete_product(product_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )


@router.post("/stock/update", response_model=ProductResponseDTO)
async def update_product_stock(
    dto: StockUpdateDTO,
    service: ProductService = Depends(get_product_service)
):
    """
    Update product stock quantity.

    Args:
        dto: Stock update data
        service: Product service dependency

    Returns:
        Updated product response

    Raises:
        HTTPException: 404 if product not found, 400 if validation fails
    """
    try:
        product = await service.update_stock(dto)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {dto.product_id} not found"
            )
        return product
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
