"""
Customer Repository Interface

Defines the contract for customer repository implementations.
"""

from abc import abstractmethod
from typing import List, Optional
from app.application.interfaces.repositories.base_repository import IBaseRepository
from app.models import Customer


class ICustomerRepository(IBaseRepository[Customer, int]):
    """
    Customer repository interface for data access operations.

    This interface extends the base repository with customer-specific
    operations for searching, filtering, and managing customer data.
    """

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Customer]:
        """
        Get a customer by email address.

        Args:
            email: Customer email address

        Returns:
            Customer if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_phone(self, phone: str) -> Optional[Customer]:
        """
        Get a customer by phone number.

        Args:
            phone: Customer phone number

        Returns:
            Customer if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_customer_code(self, customer_code: str) -> Optional[Customer]:
        """
        Get a customer by customer code.

        Args:
            customer_code: Unique customer code

        Returns:
            Customer if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_salesperson(
        self,
        salesperson_id: int,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[Customer]:
        """
        Get customers assigned to a specific salesperson.

        Args:
            salesperson_id: Salesperson ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status (optional)

        Returns:
            List of customers
        """
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[Customer]:
        """
        Search customers by name, email, phone, or customer code.

        Args:
            query: Search query string
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status (optional)

        Returns:
            List of matching customers
        """
        pass

    @abstractmethod
    async def get_active_customers(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Customer]:
        """
        Get all active customers.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of active customers
        """
        pass

    @abstractmethod
    async def get_customers_with_balance(
        self,
        min_balance: Optional[float] = None,
        max_balance: Optional[float] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Customer]:
        """
        Get customers filtered by balance range.

        Args:
            min_balance: Minimum balance (optional)
            max_balance: Maximum balance (optional)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of customers within balance range
        """
        pass

    @abstractmethod
    async def get_customers_by_pricelist(
        self,
        pricelist_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Customer]:
        """
        Get customers assigned to a specific pricelist.

        Args:
            pricelist_id: Pricelist ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of customers
        """
        pass

    @abstractmethod
    async def get_by_zoho_contact_id(self, zoho_contact_id: str) -> Optional[Customer]:
        """
        Get a customer by Zoho contact ID.

        Args:
            zoho_contact_id: Zoho contact ID

        Returns:
            Customer if found, None otherwise
        """
        pass

    @abstractmethod
    async def count_by_salesperson(
        self,
        salesperson_id: int,
        is_active: Optional[bool] = None
    ) -> int:
        """
        Count customers assigned to a salesperson.

        Args:
            salesperson_id: Salesperson ID
            is_active: Filter by active status (optional)

        Returns:
            Number of customers
        """
        pass
