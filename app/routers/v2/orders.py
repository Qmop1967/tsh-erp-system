"""
Order Router V2

Clean architecture implementation of order endpoints using repository pattern.
"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.services.order_service import OrderService
from app.application.dtos.order_dto import (
    OrderCreateDTO,
    OrderUpdateDTO,
    OrderResponseDTO,
    OrderWithItemsResponseDTO,
    OrderListResponseDTO,
    OrderSearchDTO,
    OrderSummaryDTO,
    OrderStatusUpdateDTO,
    OrderPaymentUpdateDTO,
    OrderStatisticsDTO,
)
from app.core.dependencies import get_order_service

router = APIRouter(prefix="/v2/orders", tags=["orders-v2"])


@router.get("", response_model=OrderListResponseDTO)
async def get_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    status: Optional[str] = Query(None, description="Filter by order status"),
    service: OrderService = Depends(get_order_service)
):
    """
    Get all orders with optional filtering.

    Args:
        skip: Number of records to skip
        limit: Maximum records to return
        status: Filter by order status
        service: Order service dependency

    Returns:
        Order list response
    """
    return await service.get_all_orders(
        skip=skip,
        limit=limit,
        status=status
    )


@router.get("/search", response_model=OrderListResponseDTO)
async def search_orders(
    query: Optional[str] = Query(None, description="Search query"),
    customer_id: Optional[int] = Query(None, description="Filter by customer"),
    status: Optional[str] = Query(None, description="Filter by status"),
    payment_status: Optional[str] = Query(None, description="Filter by payment status"),
    branch_id: Optional[int] = Query(None, description="Filter by branch"),
    salesperson_id: Optional[int] = Query(None, description="Filter by salesperson"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    service: OrderService = Depends(get_order_service)
):
    """
    Search orders with advanced filters.

    Args:
        query: Text search query (order number or customer name)
        customer_id: Filter by customer
        status: Filter by order status
        payment_status: Filter by payment status
        branch_id: Filter by branch
        salesperson_id: Filter by salesperson
        start_date: Start date filter
        end_date: End date filter
        skip: Number of records to skip
        limit: Maximum records to return
        service: Order service dependency

    Returns:
        Order list response
    """
    search_dto = OrderSearchDTO(
        query=query,
        customer_id=customer_id,
        status=status,
        payment_status=payment_status,
        branch_id=branch_id,
        salesperson_id=salesperson_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    return await service.search_orders(search_dto)


@router.get("/pending", response_model=OrderListResponseDTO)
async def get_pending_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    service: OrderService = Depends(get_order_service)
):
    """
    Get pending orders (DRAFT status).

    Args:
        skip: Number of records to skip
        limit: Maximum records to return
        service: Order service dependency

    Returns:
        Order list response
    """
    return await service.get_pending_orders(skip=skip, limit=limit)


@router.get("/overdue", response_model=OrderListResponseDTO)
async def get_overdue_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    service: OrderService = Depends(get_order_service)
):
    """
    Get overdue orders (delivery date passed).

    Args:
        skip: Number of records to skip
        limit: Maximum records to return
        service: Order service dependency

    Returns:
        Order list response
    """
    return await service.get_overdue_orders(skip=skip, limit=limit)


@router.get("/statistics", response_model=OrderStatisticsDTO)
async def get_order_statistics(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    service: OrderService = Depends(get_order_service)
):
    """
    Get order statistics.

    Args:
        start_date: Start date filter (optional)
        end_date: End date filter (optional)
        service: Order service dependency

    Returns:
        Order statistics
    """
    return await service.get_order_statistics(
        start_date=start_date,
        end_date=end_date
    )


@router.get("/{order_id}", response_model=OrderResponseDTO)
async def get_order(
    order_id: int,
    service: OrderService = Depends(get_order_service)
):
    """
    Get an order by ID.

    Args:
        order_id: Order ID
        service: Order service dependency

    Returns:
        Order response

    Raises:
        HTTPException: 404 if order not found
    """
    order = await service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )
    return order


@router.get("/{order_id}/with-items", response_model=OrderWithItemsResponseDTO)
async def get_order_with_items(
    order_id: int,
    service: OrderService = Depends(get_order_service)
):
    """
    Get an order with its items.

    Args:
        order_id: Order ID
        service: Order service dependency

    Returns:
        Order with items response

    Raises:
        HTTPException: 404 if order not found
    """
    order = await service.get_order_with_items(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )
    return order


@router.get("/number/{order_number}", response_model=OrderResponseDTO)
async def get_order_by_number(
    order_number: str,
    service: OrderService = Depends(get_order_service)
):
    """
    Get an order by order number.

    Args:
        order_number: Order number
        service: Order service dependency

    Returns:
        Order response

    Raises:
        HTTPException: 404 if order not found
    """
    order = await service.get_order_by_number(order_number)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with number {order_number} not found"
        )
    return order


@router.get("/customer/{customer_id}", response_model=OrderListResponseDTO)
async def get_orders_by_customer(
    customer_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    status: Optional[str] = Query(None, description="Filter by order status"),
    service: OrderService = Depends(get_order_service)
):
    """
    Get orders for a customer.

    Args:
        customer_id: Customer ID
        skip: Number of records to skip
        limit: Maximum records to return
        status: Filter by order status
        service: Order service dependency

    Returns:
        Order list response
    """
    return await service.get_orders_by_customer(
        customer_id=customer_id,
        skip=skip,
        limit=limit,
        status=status
    )


@router.post("", response_model=OrderWithItemsResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_order(
    dto: OrderCreateDTO,
    service: OrderService = Depends(get_order_service)
):
    """
    Create a new order.

    Args:
        dto: Order creation data
        service: Order service dependency

    Returns:
        Created order with items response

    Raises:
        HTTPException: 400 if validation fails
    """
    try:
        return await service.create_order(dto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{order_id}", response_model=OrderResponseDTO)
async def update_order(
    order_id: int,
    dto: OrderUpdateDTO,
    service: OrderService = Depends(get_order_service)
):
    """
    Update an existing order.

    Args:
        order_id: Order ID
        dto: Order update data
        service: Order service dependency

    Returns:
        Updated order response

    Raises:
        HTTPException: 404 if order not found, 400 if validation fails
    """
    try:
        order = await service.update_order(order_id, dto)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found"
            )
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    service: OrderService = Depends(get_order_service)
):
    """
    Delete an order.

    Args:
        order_id: Order ID
        service: Order service dependency

    Raises:
        HTTPException: 404 if order not found
    """
    deleted = await service.delete_order(order_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )


@router.post("/status/update", response_model=OrderResponseDTO)
async def update_order_status(
    dto: OrderStatusUpdateDTO,
    service: OrderService = Depends(get_order_service)
):
    """
    Update order status.

    Args:
        dto: Order status update data
        service: Order service dependency

    Returns:
        Updated order response

    Raises:
        HTTPException: 404 if order not found, 400 if validation fails
    """
    try:
        order = await service.update_order_status(dto)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {dto.order_id} not found"
            )
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/payment/update", response_model=OrderResponseDTO)
async def update_order_payment(
    dto: OrderPaymentUpdateDTO,
    service: OrderService = Depends(get_order_service)
):
    """
    Update order payment information.

    Args:
        dto: Order payment update data
        service: Order service dependency

    Returns:
        Updated order response

    Raises:
        HTTPException: 404 if order not found, 400 if validation fails
    """
    try:
        order = await service.update_payment(dto)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {dto.order_id} not found"
            )
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
