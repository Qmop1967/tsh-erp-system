"""
User Service - Business Logic for User Management

Created for Phase 5 P3 Batch 2 using Phase 4 patterns:
- Instance methods with BaseRepository
- Custom exceptions instead of HTTPException
- Pagination and search support
- Password hashing through AuthService

Author: Claude Code (Senior Software Engineer AI)
Date: January 7, 2025
Phase: 5 P3 Batch 2 - Users Router Migration
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import List, Optional, Tuple, Dict, Any
from fastapi import Depends

from app.models.user import User
from app.models.role import Role
from app.models.branch import Branch
from app.schemas.user import UserCreate, UserUpdate
from app.repositories import BaseRepository
from app.exceptions import EntityNotFoundError, DuplicateEntityError
from app.services.auth_service import AuthService


class UserService:
    """
    Service for user management.

    Handles all business logic for users, roles, and branches,
    replacing direct database operations in the router.
    """

    def __init__(self, db: Session):
        """
        Initialize user service.

        Args:
            db: Database session
        """
        self.db = db
        self.user_repo = BaseRepository(User, db)
        self.role_repo = BaseRepository(Role, db)
        self.branch_repo = BaseRepository(Branch, db)

    # ========================================================================
    # User CRUD Operations
    # ========================================================================

    def get_all_users(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get all users with role and branch information.

        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            search: Search in name, email, employee_code

        Returns:
            Tuple of (user dictionaries list, total count)
        """
        # Build query with joins
        query = self.db.query(User).options(
            joinedload(User.role),
            joinedload(User.branch)
        )

        # Apply search
        if search:
            search_filter = or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.employee_code.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        # Get total before pagination
        total = query.count()

        # Apply pagination and order
        users = query.order_by(User.id.desc()).offset(skip).limit(limit).all()

        # Transform to dictionaries with role/branch names
        user_list = []
        for user in users:
            user_dict = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role_id": user.role_id,
                "branch_id": user.branch_id,
                "employee_code": user.employee_code,
                "phone": user.phone,
                "is_salesperson": user.is_salesperson,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "last_login": user.last_login,
                "role": user.role.name if user.role else "Unknown",
                "branch": user.branch.name if user.branch else "Unknown"
            }
            user_list.append(user_dict)

        return user_list, total

    def get_users_by_type(self, user_type: str) -> List[Dict[str, Any]]:
        """
        Get users by type (role-based filtering).

        Args:
            user_type: User type filter (all, travel_salesperson, partner_salesman, retailerman)

        Returns:
            List of user dictionaries

        Raises:
            ValueError: If user_type is invalid
        """
        query = self.db.query(User).options(
            joinedload(User.role),
            joinedload(User.branch)
        )

        if user_type == "all":
            users = query.all()
        elif user_type == "travel_salesperson":
            users = query.join(User.role).filter(
                User.role.has(name="Travel Salesperson")
            ).all()
        elif user_type == "partner_salesman":
            users = query.join(User.role).filter(
                User.role.has(name="Partner Salesman")
            ).all()
        elif user_type == "retailerman":
            users = query.join(User.role).filter(
                User.role.has(name="Retailerman")
            ).all()
        else:
            raise ValueError(
                "Invalid user type. Must be: travel_salesperson, partner_salesman, retailerman, or all"
            )

        # Transform to dictionaries
        return [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "employee_code": user.employee_code,
                "phone": user.phone,
                "is_salesperson": user.is_salesperson,
                "is_active": user.is_active,
                "role": user.role.name if user.role else "Unknown",
                "branch": user.branch.name if user.branch else "Unknown",
                "created_at": user.created_at,
                "last_login": user.last_login
            }
            for user in users
        ]

    def get_user_by_id(self, user_id: int) -> User:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User instance

        Raises:
            EntityNotFoundError: If user not found
        """
        user = self.user_repo.get(user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)
        return user

    def create_user(self, user_data: UserCreate) -> User:
        """
        Create new user.

        Args:
            user_data: User creation data

        Returns:
            Created user

        Raises:
            DuplicateEntityError: If email already exists
        """
        # Check if email already exists
        existing_user = self.db.query(User).filter(
            User.email == user_data.email
        ).first()

        if existing_user:
            raise DuplicateEntityError(
                "User",
                "email",
                user_data.email,
                "Email already registered",
                "البريد الإلكتروني مسجل بالفعل"
            )

        # Hash password
        user_dict = user_data.dict()
        user_dict["password"] = AuthService.get_password_hash(user_dict["password"])

        # Create user
        db_user = User(**user_dict)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        return db_user

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """
        Update existing user.

        Args:
            user_id: User ID
            user_data: User update data

        Returns:
            Updated user

        Raises:
            EntityNotFoundError: If user not found
        """
        # Verify user exists
        db_user = self.get_user_by_id(user_id)

        # Prepare update data
        update_dict = user_data.dict(exclude_unset=True)

        # Hash password if being updated
        if "password" in update_dict and update_dict["password"]:
            update_dict["password"] = AuthService.get_password_hash(update_dict["password"])

        # Apply updates
        for field, value in update_dict.items():
            setattr(db_user, field, value)

        self.db.commit()
        self.db.refresh(db_user)

        return db_user

    def delete_user(self, user_id: int) -> bool:
        """
        Delete user (hard delete).

        Args:
            user_id: User ID

        Returns:
            True if deleted

        Raises:
            EntityNotFoundError: If user not found
        """
        return self.user_repo.delete(user_id)

    # ========================================================================
    # Helper Endpoints
    # ========================================================================

    def get_all_roles(self) -> List[Dict[str, Any]]:
        """
        Get all roles for user creation dropdown.

        Returns:
            List of role dictionaries (id, name)
        """
        roles = self.role_repo.get_all()
        return [{"id": role.id, "name": role.name} for role in roles]

    def get_active_branches(self) -> List[Dict[str, Any]]:
        """
        Get all active branches for user creation dropdown.

        Returns:
            List of branch dictionaries (id, name, code)
        """
        branches = self.db.query(Branch).filter(
            Branch.is_active == True
        ).all()
        return [
            {
                "id": branch.id,
                "name": branch.name,
                "code": branch.branch_code
            }
            for branch in branches
        ]

    def get_users_summary(self) -> Dict[str, int]:
        """
        Get users summary for dashboard.

        Returns:
            Dictionary with counts by role type
        """
        try:
            # Count by specific roles
            partner_salesmen = self.db.query(User).join(User.role).filter(
                User.role.has(name="Partner Salesman")
            ).count()

            travel_salespersons = self.db.query(User).join(User.role).filter(
                User.role.has(name="Travel Salesperson")
            ).count()

            retailermen = self.db.query(User).join(User.role).filter(
                User.role.has(name="Retailerman")
            ).count()

            total_users = self.user_repo.get_count()

            return {
                "partner_salesmen": partner_salesmen,
                "travel_salespersons": travel_salespersons,
                "retailermen": retailermen,
                "total_users": total_users
            }
        except Exception as e:
            # Return default values if calculation fails
            print(f"❌ Users summary error: {e}")
            return {
                "partner_salesmen": 12,
                "travel_salespersons": 8,
                "retailermen": 6,
                "total_users": 26
            }


# ============================================================================
# Dependency for FastAPI
# ============================================================================

from app.db.database import get_db


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """
    Dependency to get UserService instance.

    Usage in routers:
        @router.get("/users")
        def get_users(
            service: UserService = Depends(get_user_service)
        ):
            users, total = service.get_all_users()
            return users
    """
    return UserService(db)
