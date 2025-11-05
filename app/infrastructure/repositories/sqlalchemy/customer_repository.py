"""
Customer Repository SQLAlchemy Implementation

Concrete implementation of the customer repository using SQLAlchemy.
"""

from typing import List, Optional
from sqlalchemy import select, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.interfaces.repositories.customer_repository import ICustomerRepository
from app.models import Customer


class CustomerRepository(ICustomerRepository):
    """
    SQLAlchemy implementation of the customer repository.

    This class provides concrete implementations of all customer
    data access operations using SQLAlchemy ORM.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.

        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    async def get_by_id(self, id: int) -> Optional[Customer]:
        """Get a customer by ID."""
        result = await self.db.execute(
            select(Customer).where(Customer.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[Customer]:
        """Get all customers with optional pagination and filtering."""
        query = select(Customer)

        # Apply filters
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(Customer, key):
                    conditions.append(getattr(Customer, key) == value)
            if conditions:
                query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, entity: Customer) -> Customer:
        """Create a new customer."""
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update(self, id: int, entity: Customer) -> Optional[Customer]:
        """Update an existing customer."""
        existing = await self.get_by_id(id)
        if not existing:
            return None

        # Update fields
        for key, value in entity.__dict__.items():
            if not key.startswith('_') and key != 'id':
                setattr(existing, key, value)

        await self.db.commit()
        await self.db.refresh(existing)
        return existing

    async def delete(self, id: int) -> bool:
        """Delete a customer."""
        customer = await self.get_by_id(id)
        if not customer:
            return False

        await self.db.delete(customer)
        await self.db.commit()
        return True

    async def exists(self, id: int) -> bool:
        """Check if a customer exists."""
        result = await self.db.execute(
            select(Customer.id).where(Customer.id == id)
        )
        return result.scalar_one_or_none() is not None

    async def count(self, **filters) -> int:
        """Count customers with optional filtering."""
        query = select(func.count(Customer.id))

        # Apply filters
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(Customer, key):
                    conditions.append(getattr(Customer, key) == value)
            if conditions:
                query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        return result.scalar_one()

    async def find_one(self, **filters) -> Optional[Customer]:
        """Find a single customer by filters."""
        query = select(Customer)

        conditions = []
        for key, value in filters.items():
            if hasattr(Customer, key):
                conditions.append(getattr(Customer, key) == value)

        if conditions:
            query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def find_many(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[Customer]:
        """Find multiple customers by filters."""
        return await self.get_all(skip=skip, limit=limit, **filters)

    # Customer-specific methods

    async def get_by_email(self, email: str) -> Optional[Customer]:
        """Get a customer by email address."""
        result = await self.db.execute(
            select(Customer).where(Customer.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> Optional[Customer]:
        """Get a customer by phone number."""
        result = await self.db.execute(
            select(Customer).where(Customer.phone == phone)
        )
        return result.scalar_one_or_none()

    async def get_by_customer_code(self, customer_code: str) -> Optional[Customer]:
        """Get a customer by customer code."""
        result = await self.db.execute(
            select(Customer).where(Customer.customer_code == customer_code)
        )
        return result.scalar_one_or_none()

    async def get_by_salesperson(
        self,
        salesperson_id: int,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[Customer]:
        """Get customers assigned to a specific salesperson."""
        query = select(Customer).where(Customer.salesperson_id == salesperson_id)

        if is_active is not None:
            query = query.where(Customer.is_active == is_active)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[Customer]:
        """Search customers by name, email, phone, or customer code."""
        search_pattern = f"%{query}%"

        sql_query = select(Customer).where(
            or_(
                Customer.name.ilike(search_pattern),
                Customer.email.ilike(search_pattern),
                Customer.phone.ilike(search_pattern),
                Customer.customer_code.ilike(search_pattern)
            )
        )

        if is_active is not None:
            sql_query = sql_query.where(Customer.is_active == is_active)

        sql_query = sql_query.offset(skip).limit(limit)
        result = await self.db.execute(sql_query)
        return list(result.scalars().all())

    async def get_active_customers(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Customer]:
        """Get all active customers."""
        query = select(Customer).where(Customer.is_active == True)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_customers_with_balance(
        self,
        min_balance: Optional[float] = None,
        max_balance: Optional[float] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Customer]:
        """Get customers filtered by balance range."""
        query = select(Customer)

        conditions = []
        if min_balance is not None:
            conditions.append(Customer.balance >= min_balance)
        if max_balance is not None:
            conditions.append(Customer.balance <= max_balance)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_customers_by_pricelist(
        self,
        pricelist_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Customer]:
        """Get customers assigned to a specific pricelist."""
        query = select(Customer).where(Customer.pricelist_id == pricelist_id)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_zoho_contact_id(self, zoho_contact_id: str) -> Optional[Customer]:
        """Get a customer by Zoho contact ID."""
        result = await self.db.execute(
            select(Customer).where(Customer.zoho_contact_id == zoho_contact_id)
        )
        return result.scalar_one_or_none()

    async def count_by_salesperson(
        self,
        salesperson_id: int,
        is_active: Optional[bool] = None
    ) -> int:
        """Count customers assigned to a salesperson."""
        query = select(func.count(Customer.id)).where(
            Customer.salesperson_id == salesperson_id
        )

        if is_active is not None:
            query = query.where(Customer.is_active == is_active)

        result = await self.db.execute(query)
        return result.scalar_one()
