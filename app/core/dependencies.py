"""
Dependency Injection

FastAPI dependencies for clean architecture implementation.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.db.database import get_db
from app.infrastructure.repositories.sqlalchemy.customer_repository import CustomerRepository
from app.infrastructure.repositories.sqlalchemy.product_repository import ProductRepository
from app.infrastructure.repositories.sqlalchemy.order_repository import OrderRepository
from app.infrastructure.repositories.sqlalchemy.inventory_repository import (
    InventoryRepository,
    StockMovementRepository
)
from app.application.interfaces.repositories.customer_repository import ICustomerRepository
from app.application.interfaces.repositories.product_repository import IProductRepository
from app.application.interfaces.repositories.order_repository import IOrderRepository
from app.application.interfaces.repositories.inventory_repository import (
    IInventoryRepository,
    IStockMovementRepository
)
from app.application.services.customer_service import CustomerService
from app.application.services.product_service import ProductService
from app.application.services.order_service import OrderService
from app.application.services.inventory_service import InventoryService


# Repository Dependencies

async def get_customer_repository(
    db: AsyncSession = Depends(get_db)
) -> ICustomerRepository:
    """
    Get customer repository dependency.

    Args:
        db: Database session

    Returns:
        Customer repository implementation
    """
    return CustomerRepository(db)


async def get_product_repository(
    db: AsyncSession = Depends(get_db)
) -> IProductRepository:
    """
    Get product repository dependency.

    Args:
        db: Database session

    Returns:
        Product repository implementation
    """
    return ProductRepository(db)


async def get_order_repository(
    db: AsyncSession = Depends(get_db)
) -> IOrderRepository:
    """
    Get order repository dependency.

    Args:
        db: Database session

    Returns:
        Order repository implementation
    """
    return OrderRepository(db)


# Service Dependencies

async def get_customer_service(
    customer_repository: ICustomerRepository = Depends(get_customer_repository)
) -> CustomerService:
    """
    Get customer service dependency.

    Args:
        customer_repository: Customer repository

    Returns:
        Customer service instance
    """
    return CustomerService(customer_repository)


async def get_product_service(
    product_repository: IProductRepository = Depends(get_product_repository)
) -> ProductService:
    """
    Get product service dependency.

    Args:
        product_repository: Product repository

    Returns:
        Product service instance
    """
    return ProductService(product_repository)


async def get_order_service(
    order_repository: IOrderRepository = Depends(get_order_repository)
) -> OrderService:
    """
    Get order service dependency.

    Args:
        order_repository: Order repository

    Returns:
        Order service instance
    """
    return OrderService(order_repository)


async def get_inventory_repository(
    db: AsyncSession = Depends(get_db)
) -> IInventoryRepository:
    """
    Get inventory repository dependency.

    Args:
        db: Database session

    Returns:
        Inventory repository implementation
    """
    return InventoryRepository(db)


async def get_stock_movement_repository(
    db: AsyncSession = Depends(get_db)
) -> IStockMovementRepository:
    """
    Get stock movement repository dependency.

    Args:
        db: Database session

    Returns:
        Stock movement repository implementation
    """
    return StockMovementRepository(db)


async def get_inventory_service(
    inventory_repository: IInventoryRepository = Depends(get_inventory_repository),
    stock_movement_repository: IStockMovementRepository = Depends(get_stock_movement_repository)
) -> InventoryService:
    """
    Get inventory service dependency.

    Args:
        inventory_repository: Inventory repository
        stock_movement_repository: Stock movement repository

    Returns:
        Inventory service instance
    """
    return InventoryService(inventory_repository, stock_movement_repository)
