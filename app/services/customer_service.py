"""
Customer Service - Business Logic for Customer and Supplier Management

Refactored to use Phase 4 patterns:
- Instance methods instead of static methods
- BaseRepository for CRUD operations
- Custom exceptions instead of HTTPException
- Pagination and search support
- Combined customer queries support

Author: Claude Code (Senior Software Engineer AI)
Date: January 7, 2025
Phase: 5 P1 - Customers Router Migration
"""

from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import Depends
from datetime import datetime
import re

from app.models.customer import Customer, Supplier
from app.schemas.customer import CustomerCreate, CustomerUpdate, SupplierCreate, SupplierUpdate
from app.repositories import BaseRepository
from app.exceptions import (
    EntityNotFoundError,
    DuplicateEntityError,
    ValidationError
)


class CustomerService:
    """
    Service for customer management.

    Handles all business logic for customers, replacing direct
    database operations in the router.
    """

    def __init__(self, db: Session):
        """
        Initialize customer service.

        Args:
            db: Database session
        """
        self.db = db
        self.customer_repo = BaseRepository(Customer, db)

    # ========================================================================
    # Customer Code Generation
    # ========================================================================

    def generate_customer_code(self, prefix: str = "CUST") -> str:
        """
        Generate next customer code in format: CUST-YYYY-NNNN

        Args:
            prefix: Code prefix (default: "CUST")

        Returns:
            Generated customer code (e.g., "CUST-2025-0001")

        Examples:
            - CUST-2025-0001
            - CUST-2025-0002
        """
        current_year = datetime.now().year
        year_prefix = f"{prefix}-{current_year}-"

        # Get the latest customer code for current year
        latest_customer = self.db.query(Customer).filter(
            Customer.customer_code.like(f"{year_prefix}%")
        ).order_by(Customer.customer_code.desc()).first()

        if latest_customer:
            # Extract the sequence number from the latest code
            match = re.search(r'-(\d{4})$', latest_customer.customer_code)
            if match:
                last_sequence = int(match.group(1))
                next_sequence = last_sequence + 1
            else:
                next_sequence = 1
        else:
            next_sequence = 1

        # Format: CUST-YYYY-NNNN (4-digit sequence number)
        return f"{year_prefix}{next_sequence:04d}"

    # ========================================================================
    # Customer CRUD Operations
    # ========================================================================

    def get_all_customers(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        active_only: bool = True
    ) -> Tuple[List[Customer], int]:
        """
        Get all customers with optional filters.

        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            search: Search term for name, code, company_name
            active_only: Filter by active status

        Returns:
            Tuple of (customers list, total count)
        """
        # Build filters
        filters = {}
        if active_only:
            filters['is_active'] = True

        # Apply search if provided
        if search:
            customers = self.customer_repo.search(
                search_term=search,
                search_fields=['name', 'customer_code', 'company_name', 'phone'],
                skip=skip,
                limit=limit
            )
            # Get count for search results
            total = len(self.customer_repo.search(
                search_term=search,
                search_fields=['name', 'customer_code', 'company_name', 'phone'],
                skip=0,
                limit=10000
            ))
        else:
            customers = self.customer_repo.get_all(
                skip=skip,
                limit=limit,
                filters=filters
            )
            total = self.customer_repo.get_count(filters=filters)

        return customers, total

    def get_combined_customers(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        active_only: bool = True
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get combined customers (regular + migration customers).

        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            search: Search term
            active_only: Filter by active status

        Returns:
            Tuple of (combined customer list as dicts, total count)
        """
        from app.models.migration import MigrationCustomer
        from app.models.user import User

        # Get regular customers
        regular_customers, regular_total = self.get_all_customers(
            skip=skip,
            limit=limit,
            search=search,
            active_only=active_only
        )

        # Get migrated customers
        migrated_query = self.db.query(MigrationCustomer)

        if active_only:
            migrated_query = migrated_query.filter(MigrationCustomer.is_active == True)

        if search:
            search_filter = f"%{search}%"
            migrated_query = migrated_query.filter(
                or_(
                    MigrationCustomer.name_en.ilike(search_filter),
                    MigrationCustomer.name_ar.ilike(search_filter),
                    MigrationCustomer.code.ilike(search_filter)
                )
            )

        migrated_customers = migrated_query.offset(0).limit(limit).all()
        migrated_total = migrated_query.count()

        # Combine results
        result = []

        # Add regular customers
        for customer in regular_customers:
            # Get salesperson info if assigned
            salesperson_name = None
            if customer.salesperson_id:
                salesperson = self.db.query(User).filter(User.id == customer.salesperson_id).first()
                if salesperson:
                    salesperson_name = salesperson.name

            result.append({
                "id": customer.id,
                "code": customer.customer_code,
                "name": customer.name,
                "company_name": customer.company_name,
                "email": customer.email,
                "phone": customer.phone,
                "address": customer.address,
                "city": customer.city,
                "country": customer.country,
                "currency": customer.currency,
                "portal_language": customer.portal_language,
                "salesperson_id": customer.salesperson_id,
                "salesperson_name": salesperson_name,
                "tax_number": customer.tax_number,
                "credit_limit": float(customer.credit_limit) if customer.credit_limit else 0,
                "is_active": customer.is_active,
                "source": "regular",
                "created_at": customer.created_at.isoformat() if customer.created_at else None
            })

        # Add migrated customers
        for mcustomer in migrated_customers:
            result.append({
                "id": f"M{mcustomer.id}",
                "code": mcustomer.code,
                "name": mcustomer.name_en or mcustomer.name_ar,
                "name_ar": mcustomer.name_ar,
                "company_name": mcustomer.company_name,
                "email": mcustomer.email,
                "phone": mcustomer.phone,
                "address": mcustomer.billing_address,
                "city": mcustomer.billing_city,
                "country": mcustomer.billing_country,
                "currency": mcustomer.currency_code,
                "is_active": mcustomer.is_active,
                "source": "migration",
                "zoho_id": mcustomer.zoho_contact_id,
                "created_at": mcustomer.created_at.isoformat() if mcustomer.created_at else None
            })

        total = regular_total + migrated_total
        return result, total

    def get_customer_by_id(self, customer_id: int) -> Customer:
        """
        Get customer by ID.

        Args:
            customer_id: Customer ID

        Returns:
            Customer instance

        Raises:
            EntityNotFoundError: If customer not found
        """
        customer = self.customer_repo.get(customer_id)
        if not customer:
            raise EntityNotFoundError("Customer", customer_id)
        return customer

    def create_customer(self, customer_data: CustomerCreate) -> Customer:
        """
        Create new customer.

        Args:
            customer_data: Customer creation data

        Returns:
            Created customer

        Raises:
            DuplicateEntityError: If customer code already exists
        """
        # Auto-generate customer code if not provided or empty
        if not customer_data.customer_code or customer_data.customer_code.strip() == "":
            customer_data.customer_code = self.generate_customer_code()

        # Validate unique customer code
        if self.customer_repo.exists({'customer_code': customer_data.customer_code}):
            raise DuplicateEntityError("Customer", "customer_code", customer_data.customer_code)

        # Create customer
        return self.customer_repo.create(customer_data.dict())

    def update_customer(
        self,
        customer_id: int,
        customer_data: CustomerUpdate
    ) -> Customer:
        """
        Update existing customer.

        Args:
            customer_id: Customer ID
            customer_data: Customer update data

        Returns:
            Updated customer

        Raises:
            EntityNotFoundError: If customer not found
            DuplicateEntityError: If new customer code conflicts
        """
        # Verify customer exists
        existing_customer = self.get_customer_by_id(customer_id)

        update_dict = customer_data.dict(exclude_unset=True)

        # Validate unique customer code if being updated
        if 'customer_code' in update_dict:
            if update_dict['customer_code'] != existing_customer.customer_code:
                if self.customer_repo.exists({'customer_code': update_dict['customer_code']}):
                    raise DuplicateEntityError("Customer", "customer_code", update_dict['customer_code'])

        # Update customer
        return self.customer_repo.update(customer_id, update_dict)

    def delete_customer(self, customer_id: int) -> bool:
        """
        Soft delete customer (set is_active=False).

        Args:
            customer_id: Customer ID

        Returns:
            True if deactivated

        Raises:
            EntityNotFoundError: If customer not found
        """
        # Use soft delete
        self.customer_repo.soft_delete(customer_id)
        return True

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def get_salespersons(self) -> List[Dict[str, Any]]:
        """
        Get all active salespersons for customer assignment.

        Returns:
            List of salesperson dictionaries with id, name, employee_code
        """
        from app.models.user import User

        salespersons = self.db.query(User).filter(
            User.is_salesperson == True,
            User.is_active == True
        ).all()

        return [
            {
                "id": sp.id,
                "name": sp.name,
                "employee_code": sp.employee_code
            }
            for sp in salespersons
        ]


class SupplierService:
    """
    Service for supplier management.

    Handles all business logic for suppliers, replacing direct
    database operations in the router.
    """

    def __init__(self, db: Session):
        """
        Initialize supplier service.

        Args:
            db: Database session
        """
        self.db = db
        self.supplier_repo = BaseRepository(Supplier, db)

    # ========================================================================
    # Supplier CRUD Operations
    # ========================================================================

    def get_all_suppliers(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        active_only: bool = True
    ) -> Tuple[List[Supplier], int]:
        """
        Get all suppliers with optional filters.

        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            search: Search term for name, code, company_name
            active_only: Filter by active status

        Returns:
            Tuple of (suppliers list, total count)
        """
        # Build filters
        filters = {}
        if active_only:
            filters['is_active'] = True

        # Apply search if provided
        if search:
            suppliers = self.supplier_repo.search(
                search_term=search,
                search_fields=['name', 'supplier_code', 'company_name'],
                skip=skip,
                limit=limit
            )
            total = len(self.supplier_repo.search(
                search_term=search,
                search_fields=['name', 'supplier_code', 'company_name'],
                skip=0,
                limit=10000
            ))
        else:
            suppliers = self.supplier_repo.get_all(
                skip=skip,
                limit=limit,
                filters=filters
            )
            total = self.supplier_repo.get_count(filters=filters)

        return suppliers, total

    def get_supplier_by_id(self, supplier_id: int) -> Supplier:
        """
        Get supplier by ID.

        Args:
            supplier_id: Supplier ID

        Returns:
            Supplier instance

        Raises:
            EntityNotFoundError: If supplier not found
        """
        supplier = self.supplier_repo.get(supplier_id)
        if not supplier:
            raise EntityNotFoundError("Supplier", supplier_id)
        return supplier

    def create_supplier(self, supplier_data: SupplierCreate) -> Supplier:
        """
        Create new supplier.

        Args:
            supplier_data: Supplier creation data

        Returns:
            Created supplier

        Raises:
            DuplicateEntityError: If supplier code already exists
        """
        # Validate unique supplier code
        if self.supplier_repo.exists({'supplier_code': supplier_data.supplier_code}):
            raise DuplicateEntityError("Supplier", "supplier_code", supplier_data.supplier_code)

        # Create supplier
        return self.supplier_repo.create(supplier_data.dict())

    def update_supplier(
        self,
        supplier_id: int,
        supplier_data: SupplierUpdate
    ) -> Supplier:
        """
        Update existing supplier.

        Args:
            supplier_id: Supplier ID
            supplier_data: Supplier update data

        Returns:
            Updated supplier

        Raises:
            EntityNotFoundError: If supplier not found
            DuplicateEntityError: If new supplier code conflicts
        """
        # Verify supplier exists
        existing_supplier = self.get_supplier_by_id(supplier_id)

        update_dict = supplier_data.dict(exclude_unset=True)

        # Validate unique supplier code if being updated
        if 'supplier_code' in update_dict:
            if update_dict['supplier_code'] != existing_supplier.supplier_code:
                if self.supplier_repo.exists({'supplier_code': update_dict['supplier_code']}):
                    raise DuplicateEntityError("Supplier", "supplier_code", update_dict['supplier_code'])

        # Update supplier
        return self.supplier_repo.update(supplier_id, update_dict)

    def delete_supplier(self, supplier_id: int) -> bool:
        """
        Soft delete supplier (set is_active=False).

        Args:
            supplier_id: Supplier ID

        Returns:
            True if deactivated

        Raises:
            EntityNotFoundError: If supplier not found
        """
        # Use soft delete
        self.supplier_repo.soft_delete(supplier_id)
        return True


# ============================================================================
# Dependencies for FastAPI
# ============================================================================

from app.db.database import get_db


def get_customer_service(db: Session = Depends(get_db)) -> CustomerService:
    """
    Dependency to get CustomerService instance.

    Usage in routers:
        @router.get("/customers")
        def get_customers(
            service: CustomerService = Depends(get_customer_service)
        ):
            customers, total = service.get_all_customers()
            return customers
    """
    return CustomerService(db)


def get_supplier_service(db: Session = Depends(get_db)) -> SupplierService:
    """
    Dependency to get SupplierService instance.

    Usage in routers:
        @router.get("/suppliers")
        def get_suppliers(
            service: SupplierService = Depends(get_supplier_service)
        ):
            suppliers, total = service.get_all_suppliers()
            return suppliers
    """
    return SupplierService(db)
