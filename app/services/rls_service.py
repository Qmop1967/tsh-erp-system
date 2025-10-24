"""
Row-Level Security (RLS) Service
Provides automatic query filtering based on user data scope
"""

from typing import Optional, List, Any
from sqlalchemy.orm import Query, Session
from sqlalchemy import and_, or_
import json
from datetime import datetime

from app.models.user import User
from app.models.data_scope import UserDataScope, DataScopeType, DataAccessLog, user_customers, user_warehouses, user_branches


class RLSService:
    """
    Row-Level Security Service
    Automatically filters queries based on user's data scope
    """

    @staticmethod
    def get_user_scope(db: Session, user: User) -> Optional[UserDataScope]:
        """Get user's data scope configuration"""
        return db.query(UserDataScope).filter(
            UserDataScope.user_id == user.id
        ).first()

    @staticmethod
    def get_assigned_customer_ids(db: Session, user: User) -> List[int]:
        """Get list of customer IDs assigned to user"""
        result = db.execute(
            f"SELECT customer_id FROM user_customers WHERE user_id = {user.id}"
        )
        return [row[0] for row in result]

    @staticmethod
    def get_assigned_warehouse_ids(db: Session, user: User) -> List[int]:
        """Get list of warehouse IDs assigned to user"""
        result = db.execute(
            f"SELECT warehouse_id FROM user_warehouses WHERE user_id = {user.id}"
        )
        return [row[0] for row in result]

    @staticmethod
    def get_assigned_branch_ids(db: Session, user: User) -> List[int]:
        """Get list of branch IDs assigned to user"""
        result = db.execute(
            f"SELECT branch_id FROM user_branches WHERE user_id = {user.id}"
        )
        return [row[0] for row in result]

    @staticmethod
    def apply_customer_filter(query: Query, db: Session, user: User, model_class: Any,
                             customer_field: str = "customer_id") -> Query:
        """
        Apply customer-based RLS filter to query

        Args:
            query: SQLAlchemy query object
            db: Database session
            user: Current user
            model_class: Model class being queried
            customer_field: Name of customer foreign key field

        Returns:
            Filtered query
        """
        scope = RLSService.get_user_scope(db, user)

        # Admin has full access
        if scope and scope.scope_type == DataScopeType.ALL:
            return query

        # Apply customer filter if configured
        if scope and scope.auto_filter_customers:
            assigned_customers = RLSService.get_assigned_customer_ids(db, user)
            if assigned_customers:
                customer_col = getattr(model_class, customer_field)
                query = query.filter(customer_col.in_(assigned_customers))
            else:
                # No customers assigned = no data access
                query = query.filter(False)

        return query

    @staticmethod
    def apply_warehouse_filter(query: Query, db: Session, user: User, model_class: Any,
                               warehouse_field: str = "warehouse_id") -> Query:
        """Apply warehouse-based RLS filter to query"""
        scope = RLSService.get_user_scope(db, user)

        if scope and scope.scope_type == DataScopeType.ALL:
            return query

        if scope and scope.auto_filter_warehouses:
            assigned_warehouses = RLSService.get_assigned_warehouse_ids(db, user)
            if assigned_warehouses:
                warehouse_col = getattr(model_class, warehouse_field)
                query = query.filter(warehouse_col.in_(assigned_warehouses))
            else:
                query = query.filter(False)

        return query

    @staticmethod
    def apply_branch_filter(query: Query, db: Session, user: User, model_class: Any,
                           branch_field: str = "branch_id") -> Query:
        """Apply branch-based RLS filter to query"""
        scope = RLSService.get_user_scope(db, user)

        if scope and scope.scope_type == DataScopeType.ALL:
            return query

        if scope and scope.auto_filter_branches:
            assigned_branches = RLSService.get_assigned_branch_ids(db, user)
            if assigned_branches:
                branch_col = getattr(model_class, branch_field)
                query = query.filter(branch_col.in_(assigned_branches))
            else:
                # Default to user's primary branch
                branch_col = getattr(model_class, branch_field)
                query = query.filter(branch_col == user.branch_id)

        return query

    @staticmethod
    def apply_sales_filter(query: Query, db: Session, user: User, model_class: Any) -> Query:
        """
        Apply sales-based RLS filter
        Filters sales orders/invoices by assigned customers
        """
        scope = RLSService.get_user_scope(db, user)

        if scope and scope.scope_type == DataScopeType.ALL:
            return query

        if scope and scope.auto_filter_sales:
            assigned_customers = RLSService.get_assigned_customer_ids(db, user)
            if assigned_customers:
                query = query.filter(model_class.customer_id.in_(assigned_customers))
            else:
                query = query.filter(False)

        return query

    @staticmethod
    def apply_transaction_filter(query: Query, db: Session, user: User, model_class: Any) -> Query:
        """
        Apply financial transaction RLS filter
        Filters transactions by assigned customers
        """
        scope = RLSService.get_user_scope(db, user)

        if scope and scope.scope_type == DataScopeType.ALL:
            return query

        if scope and scope.auto_filter_transactions:
            assigned_customers = RLSService.get_assigned_customer_ids(db, user)
            if assigned_customers:
                # Assuming transactions have customer_id field
                if hasattr(model_class, 'customer_id'):
                    query = query.filter(model_class.customer_id.in_(assigned_customers))
            else:
                query = query.filter(False)

        return query

    @staticmethod
    def can_access_customer(db: Session, user: User, customer_id: int) -> bool:
        """Check if user can access specific customer"""
        scope = RLSService.get_user_scope(db, user)

        # Admin has full access
        if scope and scope.scope_type == DataScopeType.ALL:
            return True

        # Check if customer is assigned
        if scope and scope.auto_filter_customers:
            assigned_customers = RLSService.get_assigned_customer_ids(db, user)
            return customer_id in assigned_customers

        return True  # Default allow if no filter configured

    @staticmethod
    def can_access_warehouse(db: Session, user: User, warehouse_id: int) -> bool:
        """Check if user can access specific warehouse"""
        scope = RLSService.get_user_scope(db, user)

        if scope and scope.scope_type == DataScopeType.ALL:
            return True

        if scope and scope.auto_filter_warehouses:
            assigned_warehouses = RLSService.get_assigned_warehouse_ids(db, user)
            return warehouse_id in assigned_warehouses

        return True

    @staticmethod
    def log_access_attempt(
        db: Session,
        user: User,
        resource_type: str,
        resource_id: Optional[int],
        action: str,
        granted: bool,
        denial_reason: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """Log data access attempt for audit trail"""
        log_entry = DataAccessLog(
            user_id=user.id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            access_granted=granted,
            denial_reason=denial_reason,
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()

    @staticmethod
    def create_default_scope_for_field_sales(db: Session, user: User, created_by_id: int):
        """
        Create default data scope for field sales representative
        - Auto-filter customers (only assigned customers)
        - Auto-filter warehouses (only assigned warehouses)
        - Auto-filter sales (only sales for assigned customers)
        - Auto-filter transactions (only transactions for assigned customers)
        """
        scope = UserDataScope(
            user_id=user.id,
            scope_type=DataScopeType.CUSTOMER,
            auto_filter_customers=True,
            auto_filter_warehouses=True,
            auto_filter_branches=False,
            auto_filter_sales=True,
            auto_filter_inventory=True,
            auto_filter_transactions=True,
            include_subordinates=False,
            created_by=created_by_id
        )
        db.add(scope)
        db.commit()
        db.refresh(scope)
        return scope

    @staticmethod
    def create_default_scope_for_finance(db: Session, user: User, created_by_id: int):
        """
        Create default data scope for finance staff
        - Auto-filter transactions (only linked customer transactions)
        - Full access to financial data for assigned customers
        """
        scope = UserDataScope(
            user_id=user.id,
            scope_type=DataScopeType.CUSTOMER,
            auto_filter_customers=True,
            auto_filter_warehouses=False,
            auto_filter_branches=False,
            auto_filter_sales=True,
            auto_filter_inventory=False,
            auto_filter_transactions=True,
            include_subordinates=False,
            created_by=created_by_id
        )
        db.add(scope)
        db.commit()
        db.refresh(scope)
        return scope

    @staticmethod
    def create_admin_scope(db: Session, user: User, created_by_id: int):
        """
        Create full access scope for admin users
        """
        scope = UserDataScope(
            user_id=user.id,
            scope_type=DataScopeType.ALL,
            auto_filter_customers=False,
            auto_filter_warehouses=False,
            auto_filter_branches=False,
            auto_filter_sales=False,
            auto_filter_inventory=False,
            auto_filter_transactions=False,
            include_subordinates=True,
            created_by=created_by_id
        )
        db.add(scope)
        db.commit()
        db.refresh(scope)
        return scope
