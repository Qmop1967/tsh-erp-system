"""
Customer Service

Business logic layer for customer operations using repository pattern.
"""

from typing import List, Optional
from app.application.interfaces.repositories.customer_repository import ICustomerRepository
from app.application.dtos.customer_dto import (
    CustomerCreateDTO,
    CustomerUpdateDTO,
    CustomerResponseDTO,
    CustomerListResponseDTO,
    CustomerSearchDTO,
    CustomerSummaryDTO,
)
from app.models import Customer


class CustomerService:
    """
    Service class for customer business logic.

    This service class handles all customer-related business logic
    using the repository pattern for data access.
    """

    def __init__(self, customer_repository: ICustomerRepository):
        """
        Initialize the service with a customer repository.

        Args:
            customer_repository: Customer repository implementation
        """
        self.repository = customer_repository

    async def get_customer_by_id(self, customer_id: int) -> Optional[CustomerResponseDTO]:
        """
        Get a customer by ID.

        Args:
            customer_id: Customer ID

        Returns:
            Customer response DTO if found, None otherwise
        """
        customer = await self.repository.get_by_id(customer_id)
        if not customer:
            return None
        return CustomerResponseDTO.model_validate(customer)

    async def get_all_customers(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> CustomerListResponseDTO:
        """
        Get all customers with optional filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status

        Returns:
            Customer list response DTO
        """
        filters = {}
        if is_active is not None:
            filters['is_active'] = is_active

        customers = await self.repository.get_all(skip=skip, limit=limit, **filters)
        total = await self.repository.count(**filters)

        return CustomerListResponseDTO(
            items=[CustomerResponseDTO.model_validate(c) for c in customers],
            total=total,
            skip=skip,
            limit=limit
        )

    async def create_customer(self, dto: CustomerCreateDTO) -> CustomerResponseDTO:
        """
        Create a new customer.

        Args:
            dto: Customer creation DTO

        Returns:
            Created customer response DTO

        Raises:
            ValueError: If email or customer code already exists
        """
        # Check for duplicate email
        if dto.email:
            existing = await self.repository.get_by_email(dto.email)
            if existing:
                raise ValueError(f"Customer with email {dto.email} already exists")

        # Check for duplicate customer code
        if dto.customer_code:
            existing = await self.repository.get_by_customer_code(dto.customer_code)
            if existing:
                raise ValueError(f"Customer with code {dto.customer_code} already exists")

        # Create customer entity
        customer = Customer(**dto.model_dump())
        created_customer = await self.repository.create(customer)

        return CustomerResponseDTO.model_validate(created_customer)

    async def update_customer(
        self,
        customer_id: int,
        dto: CustomerUpdateDTO
    ) -> Optional[CustomerResponseDTO]:
        """
        Update an existing customer.

        Args:
            customer_id: Customer ID
            dto: Customer update DTO

        Returns:
            Updated customer response DTO if found, None otherwise

        Raises:
            ValueError: If email or customer code conflicts with another customer
        """
        existing_customer = await self.repository.get_by_id(customer_id)
        if not existing_customer:
            return None

        # Check for duplicate email (if changing)
        if dto.email and dto.email != existing_customer.email:
            email_exists = await self.repository.get_by_email(dto.email)
            if email_exists:
                raise ValueError(f"Customer with email {dto.email} already exists")

        # Update only provided fields
        update_data = dto.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_customer, key, value)

        updated_customer = await self.repository.update(customer_id, existing_customer)
        return CustomerResponseDTO.model_validate(updated_customer)

    async def delete_customer(self, customer_id: int) -> bool:
        """
        Delete a customer (soft delete by setting is_active=False).

        Args:
            customer_id: Customer ID

        Returns:
            True if deleted, False if not found
        """
        customer = await self.repository.get_by_id(customer_id)
        if not customer:
            return False

        # Soft delete
        customer.is_active = False
        await self.repository.update(customer_id, customer)
        return True

    async def search_customers(self, dto: CustomerSearchDTO) -> CustomerListResponseDTO:
        """
        Search customers with filters.

        Args:
            dto: Customer search DTO

        Returns:
            Customer list response DTO
        """
        customers = []
        total = 0

        if dto.query:
            # Text search
            customers = await self.repository.search(
                query=dto.query,
                skip=dto.skip,
                limit=dto.limit,
                is_active=dto.is_active
            )
            # For text search, we need a separate count query
            all_results = await self.repository.search(
                query=dto.query,
                skip=0,
                limit=10000,
                is_active=dto.is_active
            )
            total = len(all_results)
        elif dto.salesperson_id:
            # Salesperson filter
            customers = await self.repository.get_by_salesperson(
                salesperson_id=dto.salesperson_id,
                skip=dto.skip,
                limit=dto.limit,
                is_active=dto.is_active
            )
            total = await self.repository.count_by_salesperson(
                salesperson_id=dto.salesperson_id,
                is_active=dto.is_active
            )
        elif dto.pricelist_id:
            # Pricelist filter
            customers = await self.repository.get_customers_by_pricelist(
                pricelist_id=dto.pricelist_id,
                skip=dto.skip,
                limit=dto.limit
            )
            filters = {'pricelist_id': dto.pricelist_id}
            if dto.is_active is not None:
                filters['is_active'] = dto.is_active
            total = await self.repository.count(**filters)
        elif dto.min_balance is not None or dto.max_balance is not None:
            # Balance range filter
            customers = await self.repository.get_customers_with_balance(
                min_balance=dto.min_balance,
                max_balance=dto.max_balance,
                skip=dto.skip,
                limit=dto.limit
            )
            # For balance filter, get all and count
            all_customers = await self.repository.get_customers_with_balance(
                min_balance=dto.min_balance,
                max_balance=dto.max_balance,
                skip=0,
                limit=10000
            )
            total = len(all_customers)
        else:
            # Default: get all with is_active filter
            filters = {}
            if dto.is_active is not None:
                filters['is_active'] = dto.is_active
            customers = await self.repository.get_all(
                skip=dto.skip,
                limit=dto.limit,
                **filters
            )
            total = await self.repository.count(**filters)

        return CustomerListResponseDTO(
            items=[CustomerResponseDTO.model_validate(c) for c in customers],
            total=total,
            skip=dto.skip,
            limit=dto.limit
        )

    async def get_customer_by_email(self, email: str) -> Optional[CustomerResponseDTO]:
        """
        Get a customer by email.

        Args:
            email: Customer email

        Returns:
            Customer response DTO if found, None otherwise
        """
        customer = await self.repository.get_by_email(email)
        if not customer:
            return None
        return CustomerResponseDTO.model_validate(customer)

    async def get_customer_by_code(self, customer_code: str) -> Optional[CustomerResponseDTO]:
        """
        Get a customer by customer code.

        Args:
            customer_code: Customer code

        Returns:
            Customer response DTO if found, None otherwise
        """
        customer = await self.repository.get_by_customer_code(customer_code)
        if not customer:
            return None
        return CustomerResponseDTO.model_validate(customer)

    async def get_customers_by_salesperson(
        self,
        salesperson_id: int,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> CustomerListResponseDTO:
        """
        Get customers assigned to a salesperson.

        Args:
            salesperson_id: Salesperson ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status

        Returns:
            Customer list response DTO
        """
        customers = await self.repository.get_by_salesperson(
            salesperson_id=salesperson_id,
            skip=skip,
            limit=limit,
            is_active=is_active
        )
        total = await self.repository.count_by_salesperson(
            salesperson_id=salesperson_id,
            is_active=is_active
        )

        return CustomerListResponseDTO(
            items=[CustomerResponseDTO.model_validate(c) for c in customers],
            total=total,
            skip=skip,
            limit=limit
        )

    async def get_active_customers_summary(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[CustomerSummaryDTO]:
        """
        Get summary of active customers.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of customer summary DTOs
        """
        customers = await self.repository.get_active_customers(skip=skip, limit=limit)
        return [CustomerSummaryDTO.model_validate(c) for c in customers]

    async def validate_customer_credit(
        self,
        customer_id: int,
        order_amount: float
    ) -> tuple[bool, str]:
        """
        Validate if customer has enough credit for an order.

        Args:
            customer_id: Customer ID
            order_amount: Order amount to validate

        Returns:
            Tuple of (is_valid, message)
        """
        customer = await self.repository.get_by_id(customer_id)
        if not customer:
            return False, "Customer not found"

        if not customer.is_active:
            return False, "Customer is not active"

        available_credit = customer.credit_limit - customer.balance
        if available_credit < order_amount:
            return False, f"Insufficient credit. Available: {available_credit:.2f}, Required: {order_amount:.2f}"

        return True, "Credit validation passed"

    async def get_customer_stats(self, customer_id: int) -> Optional[dict]:
        """
        Get customer statistics.

        Args:
            customer_id: Customer ID

        Returns:
            Dictionary with customer stats if found, None otherwise
        """
        customer = await self.repository.get_by_id(customer_id)
        if not customer:
            return None

        available_credit = customer.credit_limit - customer.balance
        credit_utilization = (customer.balance / customer.credit_limit * 100) if customer.credit_limit > 0 else 0

        return {
            "customer_id": customer.id,
            "name": customer.name,
            "balance": customer.balance,
            "credit_limit": customer.credit_limit,
            "available_credit": available_credit,
            "credit_utilization": credit_utilization,
            "is_active": customer.is_active,
        }
