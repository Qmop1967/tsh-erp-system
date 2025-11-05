"""
Customer Router V2

Clean architecture implementation of customer endpoints using repository pattern.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.services.customer_service import CustomerService
from app.application.dtos.customer_dto import (
    CustomerCreateDTO,
    CustomerUpdateDTO,
    CustomerResponseDTO,
    CustomerListResponseDTO,
    CustomerSearchDTO,
    CustomerSummaryDTO,
)
from app.core.dependencies import get_customer_service

router = APIRouter(prefix="/v2/customers", tags=["customers-v2"])


@router.get("", response_model=CustomerListResponseDTO)
async def get_customers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    service: CustomerService = Depends(get_customer_service)
):
    """
    Get all customers with optional filtering.

    Args:
        skip: Number of records to skip
        limit: Maximum records to return
        is_active: Filter by active status
        service: Customer service dependency

    Returns:
        Customer list response
    """
    return await service.get_all_customers(
        skip=skip,
        limit=limit,
        is_active=is_active
    )


@router.get("/search", response_model=CustomerListResponseDTO)
async def search_customers(
    query: Optional[str] = Query(None, description="Search query"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    salesperson_id: Optional[int] = Query(None, description="Filter by salesperson"),
    pricelist_id: Optional[int] = Query(None, description="Filter by pricelist"),
    min_balance: Optional[float] = Query(None, ge=0, description="Minimum balance"),
    max_balance: Optional[float] = Query(None, ge=0, description="Maximum balance"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    service: CustomerService = Depends(get_customer_service)
):
    """
    Search customers with advanced filters.

    Args:
        query: Text search query (searches name, email, phone, code)
        is_active: Filter by active status
        salesperson_id: Filter by salesperson
        pricelist_id: Filter by pricelist
        min_balance: Minimum balance
        max_balance: Maximum balance
        skip: Number of records to skip
        limit: Maximum records to return
        service: Customer service dependency

    Returns:
        Customer list response
    """
    search_dto = CustomerSearchDTO(
        query=query,
        is_active=is_active,
        salesperson_id=salesperson_id,
        pricelist_id=pricelist_id,
        min_balance=min_balance,
        max_balance=max_balance,
        skip=skip,
        limit=limit
    )
    return await service.search_customers(search_dto)


@router.get("/active/summary", response_model=List[CustomerSummaryDTO])
async def get_active_customers_summary(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    service: CustomerService = Depends(get_customer_service)
):
    """
    Get summary of active customers.

    Args:
        skip: Number of records to skip
        limit: Maximum records to return
        service: Customer service dependency

    Returns:
        List of customer summaries
    """
    return await service.get_active_customers_summary(skip=skip, limit=limit)


@router.get("/{customer_id}", response_model=CustomerResponseDTO)
async def get_customer(
    customer_id: int,
    service: CustomerService = Depends(get_customer_service)
):
    """
    Get a customer by ID.

    Args:
        customer_id: Customer ID
        service: Customer service dependency

    Returns:
        Customer response

    Raises:
        HTTPException: 404 if customer not found
    """
    customer = await service.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    return customer


@router.get("/{customer_id}/stats")
async def get_customer_stats(
    customer_id: int,
    service: CustomerService = Depends(get_customer_service)
):
    """
    Get customer statistics.

    Args:
        customer_id: Customer ID
        service: Customer service dependency

    Returns:
        Customer statistics

    Raises:
        HTTPException: 404 if customer not found
    """
    stats = await service.get_customer_stats(customer_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    return stats


@router.get("/email/{email}", response_model=CustomerResponseDTO)
async def get_customer_by_email(
    email: str,
    service: CustomerService = Depends(get_customer_service)
):
    """
    Get a customer by email.

    Args:
        email: Customer email
        service: Customer service dependency

    Returns:
        Customer response

    Raises:
        HTTPException: 404 if customer not found
    """
    customer = await service.get_customer_by_email(email)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with email {email} not found"
        )
    return customer


@router.get("/code/{customer_code}", response_model=CustomerResponseDTO)
async def get_customer_by_code(
    customer_code: str,
    service: CustomerService = Depends(get_customer_service)
):
    """
    Get a customer by customer code.

    Args:
        customer_code: Customer code
        service: Customer service dependency

    Returns:
        Customer response

    Raises:
        HTTPException: 404 if customer not found
    """
    customer = await service.get_customer_by_code(customer_code)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with code {customer_code} not found"
        )
    return customer


@router.post("", response_model=CustomerResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_customer(
    dto: CustomerCreateDTO,
    service: CustomerService = Depends(get_customer_service)
):
    """
    Create a new customer.

    Args:
        dto: Customer creation data
        service: Customer service dependency

    Returns:
        Created customer response

    Raises:
        HTTPException: 400 if validation fails or duplicate exists
    """
    try:
        return await service.create_customer(dto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{customer_id}", response_model=CustomerResponseDTO)
async def update_customer(
    customer_id: int,
    dto: CustomerUpdateDTO,
    service: CustomerService = Depends(get_customer_service)
):
    """
    Update an existing customer.

    Args:
        customer_id: Customer ID
        dto: Customer update data
        service: Customer service dependency

    Returns:
        Updated customer response

    Raises:
        HTTPException: 404 if customer not found, 400 if validation fails
    """
    try:
        customer = await service.update_customer(customer_id, dto)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found"
            )
        return customer
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    service: CustomerService = Depends(get_customer_service)
):
    """
    Delete a customer (soft delete).

    Args:
        customer_id: Customer ID
        service: Customer service dependency

    Raises:
        HTTPException: 404 if customer not found
    """
    deleted = await service.delete_customer(customer_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )


@router.post("/{customer_id}/validate-credit")
async def validate_customer_credit(
    customer_id: int,
    order_amount: float = Query(..., ge=0, description="Order amount to validate"),
    service: CustomerService = Depends(get_customer_service)
):
    """
    Validate if customer has enough credit for an order.

    Args:
        customer_id: Customer ID
        order_amount: Order amount to validate
        service: Customer service dependency

    Returns:
        Validation result

    Raises:
        HTTPException: 400 if validation fails
    """
    is_valid, message = await service.validate_customer_credit(customer_id, order_amount)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    return {
        "valid": True,
        "message": message
    }


@router.get("/salesperson/{salesperson_id}", response_model=CustomerListResponseDTO)
async def get_customers_by_salesperson(
    salesperson_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    service: CustomerService = Depends(get_customer_service)
):
    """
    Get customers assigned to a salesperson.

    Args:
        salesperson_id: Salesperson ID
        skip: Number of records to skip
        limit: Maximum records to return
        is_active: Filter by active status
        service: Customer service dependency

    Returns:
        Customer list response
    """
    return await service.get_customers_by_salesperson(
        salesperson_id=salesperson_id,
        skip=skip,
        limit=limit,
        is_active=is_active
    )
