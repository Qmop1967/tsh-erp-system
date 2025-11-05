"""
Order Repository Interface

Defines the contract for order repository implementations.
"""

from abc import abstractmethod
from typing import List, Optional
from datetime import date
from app.application.interfaces.repositories.base_repository import IBaseRepository
from app.models import SalesOrder


class IOrderRepository(IBaseRepository[SalesOrder, int]):
    """
    Order repository interface for data access operations.

    This interface extends the base repository with order-specific
    operations for searching, filtering, and managing order data.
    """

    @abstractmethod
    async def get_by_order_number(self, order_number: str) -> Optional[SalesOrder]:
        """
        Get an order by order number.

        Args:
            order_number: Order number

        Returns:
            Order if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_customer(
        self,
        customer_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[SalesOrder]:
        """
        Get orders for a specific customer.

        Args:
            customer_id: Customer ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by order status (optional)

        Returns:
            List of orders
        """
        pass

    @abstractmethod
    async def get_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[SalesOrder]:
        """
        Get orders by status.

        Args:
            status: Order status (DRAFT, CONFIRMED, SHIPPED, DELIVERED, CANCELLED)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of orders
        """
        pass

    @abstractmethod
    async def get_by_payment_status(
        self,
        payment_status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[SalesOrder]:
        """
        Get orders by payment status.

        Args:
            payment_status: Payment status (PENDING, PARTIAL, PAID, OVERDUE)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of orders
        """
        pass

    @abstractmethod
    async def get_by_date_range(
        self,
        start_date: date,
        end_date: date,
        skip: int = 0,
        limit: int = 100
    ) -> List[SalesOrder]:
        """
        Get orders within a date range.

        Args:
            start_date: Start date
            end_date: End date
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of orders
        """
        pass

    @abstractmethod
    async def get_by_branch(
        self,
        branch_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[SalesOrder]:
        """
        Get orders for a specific branch.

        Args:
            branch_id: Branch ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of orders
        """
        pass

    @abstractmethod
    async def get_by_salesperson(
        self,
        salesperson_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[SalesOrder]:
        """
        Get orders created by a specific salesperson.

        Args:
            salesperson_id: Salesperson (user) ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of orders
        """
        pass

    @abstractmethod
    async def get_pending_orders(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[SalesOrder]:
        """
        Get pending orders (not confirmed yet).

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of pending orders
        """
        pass

    @abstractmethod
    async def get_overdue_orders(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[SalesOrder]:
        """
        Get overdue orders (expected delivery date passed).

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of overdue orders
        """
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[SalesOrder]:
        """
        Search orders by order number or customer name.

        Args:
            query: Search query string
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching orders
        """
        pass

    @abstractmethod
    async def count_by_status(self, status: str) -> int:
        """
        Count orders by status.

        Args:
            status: Order status

        Returns:
            Number of orders
        """
        pass

    @abstractmethod
    async def count_by_customer(
        self,
        customer_id: int,
        status: Optional[str] = None
    ) -> int:
        """
        Count orders for a customer.

        Args:
            customer_id: Customer ID
            status: Filter by status (optional)

        Returns:
            Number of orders
        """
        pass

    @abstractmethod
    async def get_total_sales_amount(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        customer_id: Optional[int] = None
    ) -> float:
        """
        Get total sales amount with optional filters.

        Args:
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            customer_id: Customer filter (optional)

        Returns:
            Total sales amount
        """
        pass

    @abstractmethod
    async def update_order_status(
        self,
        order_id: int,
        status: str
    ) -> Optional[SalesOrder]:
        """
        Update order status.

        Args:
            order_id: Order ID
            status: New status

        Returns:
            Updated order if found, None otherwise
        """
        pass

    @abstractmethod
    async def update_payment_status(
        self,
        order_id: int,
        payment_status: str,
        paid_amount: Optional[float] = None
    ) -> Optional[SalesOrder]:
        """
        Update payment status and paid amount.

        Args:
            order_id: Order ID
            payment_status: New payment status
            paid_amount: Amount paid (optional)

        Returns:
            Updated order if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_with_items(self, order_id: int) -> Optional[SalesOrder]:
        """
        Get order with its items eagerly loaded.

        Args:
            order_id: Order ID

        Returns:
            Order with items if found, None otherwise
        """
        pass
