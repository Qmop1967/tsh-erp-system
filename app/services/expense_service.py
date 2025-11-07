"""
Expense Service - Business Logic for Expense Management

Created for Phase 5 P3 Batch 1 using Phase 4 patterns:
- Instance methods with BaseRepository
- Custom exceptions instead of HTTPException
- Pagination and search support

Author: Claude Code (Senior Software Engineer AI)
Date: January 7, 2025
Phase: 5 P3 Batch 1 - Expenses Router Migration
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from typing import List, Optional, Tuple
from fastapi import Depends

from app.models.expense import (
    Expense, ExpenseItem, ExpenseAttachment,
    ExpenseStatusEnum, ExpenseCategoryEnum, ExpensePaymentMethodEnum
)
from app.repositories import BaseRepository
from app.exceptions import EntityNotFoundError


class ExpenseService:
    """
    Service for expense management.

    Handles all business logic for expenses, items, and attachments,
    replacing direct database operations in the router.
    """

    def __init__(self, db: Session):
        """
        Initialize expense service.

        Args:
            db: Database session
        """
        self.db = db
        self.expense_repo = BaseRepository(Expense, db)
        self.expense_item_repo = BaseRepository(ExpenseItem, db)
        self.expense_attachment_repo = BaseRepository(ExpenseAttachment, db)

    # ========================================================================
    # Expense CRUD Operations
    # ========================================================================

    def get_all_expenses(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ExpenseStatusEnum] = None,
        category: Optional[ExpenseCategoryEnum] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Expense], int]:
        """
        Get all expenses with optional filters.

        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            status: Filter by status
            category: Filter by category
            search: Search in title, description, expense_number

        Returns:
            Tuple of (expenses list, total count)
        """
        query = self.db.query(Expense).order_by(desc(Expense.expense_date))

        # Apply filters
        if status:
            query = query.filter(Expense.status == status)

        if category:
            query = query.filter(Expense.category == category)

        # Apply search
        if search:
            search_filter = or_(
                Expense.title.ilike(f"%{search}%"),
                Expense.description.ilike(f"%{search}%"),
                Expense.expense_number.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        # Get total count before pagination
        total = query.count()

        # Apply pagination
        expenses = query.offset(skip).limit(limit).all()

        return expenses, total

    def get_expense_by_id(self, expense_id: int) -> Expense:
        """
        Get expense by ID with all items and attachments.

        Args:
            expense_id: Expense ID

        Returns:
            Expense instance

        Raises:
            EntityNotFoundError: If expense not found
        """
        expense = self.expense_repo.get(expense_id)
        if not expense:
            raise EntityNotFoundError("Expense", expense_id)
        return expense

    # ========================================================================
    # Enum List Operations
    # ========================================================================

    def get_expense_categories(self) -> List[dict]:
        """
        Get all available expense categories.

        Returns:
            List of category dictionaries with value and label
        """
        return [
            {
                "value": category.value,
                "label": category.value.replace("_", " ").title()
            }
            for category in ExpenseCategoryEnum
        ]

    def get_expense_statuses(self) -> List[dict]:
        """
        Get all available expense statuses.

        Returns:
            List of status dictionaries with value and label
        """
        return [
            {
                "value": status.value,
                "label": status.value.replace("_", " ").title()
            }
            for status in ExpenseStatusEnum
        ]

    def get_payment_methods(self) -> List[dict]:
        """
        Get all available payment methods.

        Returns:
            List of payment method dictionaries with value and label
        """
        return [
            {
                "value": method.value,
                "label": method.value.replace("_", " ").title()
            }
            for method in ExpensePaymentMethodEnum
        ]


# ============================================================================
# Dependency for FastAPI
# ============================================================================

from app.db.database import get_db


def get_expense_service(db: Session = Depends(get_db)) -> ExpenseService:
    """
    Dependency to get ExpenseService instance.

    Usage in routers:
        @router.get("/expenses")
        def get_expenses(
            service: ExpenseService = Depends(get_expense_service)
        ):
            expenses, total = service.get_all_expenses()
            return expenses
    """
    return ExpenseService(db)
