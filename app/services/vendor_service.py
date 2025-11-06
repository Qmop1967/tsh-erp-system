"""
Vendor Service - Business Logic for Vendor Management

Created for Phase 5 P2 migration using Phase 4 patterns:
- Instance methods with BaseRepository
- Custom exceptions instead of HTTPException
- Pagination and search support

Author: Claude Code (Senior Software Engineer AI)
Date: January 7, 2025
Phase: 5 P2 - Vendors Router Migration
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import Depends

from app.models.migration import MigrationVendor
from app.schemas.migration import VendorCreate, VendorUpdate
from app.repositories import BaseRepository
from app.exceptions import EntityNotFoundError


class VendorService:
    """
    Service for vendor management.

    Handles all business logic for migration vendors,
    replacing direct database operations in the router.
    """

    def __init__(self, db: Session):
        """
        Initialize vendor service.

        Args:
            db: Database session
        """
        self.db = db
        self.vendor_repo = BaseRepository(MigrationVendor, db)

    # ========================================================================
    # Vendor CRUD Operations
    # ========================================================================

    def get_all_vendors(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> Tuple[List[MigrationVendor], int]:
        """
        Get all vendors with optional search.

        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            search: Search term for name_en, name_ar, code, email

        Returns:
            Tuple of (vendors list, total count)
        """
        # Apply search if provided
        if search:
            vendors = self.vendor_repo.search(
                search_term=search,
                search_fields=['name_en', 'name_ar', 'code', 'email'],
                skip=skip,
                limit=limit
            )
            # Get count for search results
            total = len(self.vendor_repo.search(
                search_term=search,
                search_fields=['name_en', 'name_ar', 'code', 'email'],
                skip=0,
                limit=10000
            ))
        else:
            vendors = self.vendor_repo.get_all(
                skip=skip,
                limit=limit
            )
            total = self.vendor_repo.get_count()

        return vendors, total

    def get_vendor_by_id(self, vendor_id: int) -> MigrationVendor:
        """
        Get vendor by ID.

        Args:
            vendor_id: Vendor ID

        Returns:
            MigrationVendor instance

        Raises:
            EntityNotFoundError: If vendor not found
        """
        vendor = self.vendor_repo.get(vendor_id)
        if not vendor:
            raise EntityNotFoundError("Vendor", vendor_id)
        return vendor

    def create_vendor(self, vendor_data: VendorCreate) -> MigrationVendor:
        """
        Create new vendor.

        Args:
            vendor_data: Vendor creation data

        Returns:
            Created vendor
        """
        return self.vendor_repo.create(vendor_data.dict())

    def update_vendor(
        self,
        vendor_id: int,
        vendor_data: VendorUpdate
    ) -> MigrationVendor:
        """
        Update existing vendor.

        Args:
            vendor_id: Vendor ID
            vendor_data: Vendor update data

        Returns:
            Updated vendor

        Raises:
            EntityNotFoundError: If vendor not found
        """
        # Verify vendor exists
        self.get_vendor_by_id(vendor_id)

        # Update vendor
        update_dict = vendor_data.dict(exclude_unset=True)
        return self.vendor_repo.update(vendor_id, update_dict)

    def delete_vendor(self, vendor_id: int) -> bool:
        """
        Hard delete vendor.

        Args:
            vendor_id: Vendor ID

        Returns:
            True if deleted

        Raises:
            EntityNotFoundError: If vendor not found
        """
        return self.vendor_repo.delete(vendor_id)


# ============================================================================
# Dependency for FastAPI
# ============================================================================

from app.db.database import get_db


def get_vendor_service(db: Session = Depends(get_db)) -> VendorService:
    """
    Dependency to get VendorService instance.

    Usage in routers:
        @router.get("/vendors")
        def get_vendors(
            service: VendorService = Depends(get_vendor_service)
        ):
            vendors, total = service.get_all_vendors()
            return vendors
    """
    return VendorService(db)
