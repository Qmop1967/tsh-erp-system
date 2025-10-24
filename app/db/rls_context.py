"""
Row-Level Security (RLS) Context Manager
=========================================

This module provides the critical bridge between FastAPI application context
and PostgreSQL RLS policies using session variables.

Based on: PostgreSQL Best Practices for Fine-Grained Authorization
Pattern: Session Variable Bridge (current_setting() integration)

Usage:
------
from app.db.rls_context import set_rls_context

# In FastAPI dependency or middleware
@app.middleware("http")
async def rls_middleware(request: Request, call_next):
    if hasattr(request.state, "user"):
        with SessionLocal() as db:
            set_rls_context(db, request.state.user)
    return await call_next(request)
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class RLSContext:
    """
    Context manager for PostgreSQL Row-Level Security session variables.

    This is the implementation of the "Session Variable Bridge" pattern
    that connects stateful application authentication to stateless database policies.
    """

    def __init__(
        self,
        db: Session,
        user_id: int,
        role_name: Optional[str] = None,
        tenant_id: Optional[int] = None,
        branch_id: Optional[int] = None,
        warehouse_id: Optional[int] = None,
    ):
        """
        Initialize RLS context with user information.

        Args:
            db: SQLAlchemy database session
            user_id: Current authenticated user's ID
            role_name: User's role (e.g., 'sales_rep', 'manager', 'admin')
            tenant_id: Tenant ID for multi-tenancy
            branch_id: User's assigned branch ID
            warehouse_id: User's assigned warehouse ID
        """
        self.db = db
        self.user_id = user_id
        self.role_name = role_name
        self.tenant_id = tenant_id
        self.branch_id = branch_id
        self.warehouse_id = warehouse_id
        self._original_values = {}

    def __enter__(self):
        """Set all session variables when entering context."""
        try:
            # Set user ID (REQUIRED - used by all RLS policies)
            self._set_config("app.current_user_id", str(self.user_id))
            logger.debug(f"🔐 RLS Context: Set user_id={self.user_id}")

            # Set optional context variables
            if self.role_name:
                self._set_config("app.current_user_role", self.role_name)
                logger.debug(f"🔐 RLS Context: Set role={self.role_name}")

            if self.tenant_id:
                self._set_config("app.current_tenant_id", str(self.tenant_id))
                logger.debug(f"🔐 RLS Context: Set tenant_id={self.tenant_id}")

            if self.branch_id:
                self._set_config("app.current_branch_id", str(self.branch_id))
                logger.debug(f"🔐 RLS Context: Set branch_id={self.branch_id}")

            if self.warehouse_id:
                self._set_config("app.current_warehouse_id", str(self.warehouse_id))
                logger.debug(f"🔐 RLS Context: Set warehouse_id={self.warehouse_id}")

            # Commit the session variable changes
            self.db.commit()

            return self

        except Exception as e:
            logger.error(f"❌ RLS Context: Failed to set session variables: {e}")
            self.db.rollback()
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up session variables when exiting context."""
        try:
            # Reset all session variables
            self._set_config("app.current_user_id", None)
            self._set_config("app.current_user_role", None)
            self._set_config("app.current_tenant_id", None)
            self._set_config("app.current_branch_id", None)
            self._set_config("app.current_warehouse_id", None)

            self.db.commit()
            logger.debug("🔓 RLS Context: Cleared session variables")

        except Exception as e:
            logger.error(f"❌ RLS Context: Failed to clear session variables: {e}")
            self.db.rollback()

    def _set_config(self, key: str, value: Optional[str]):
        """
        Set a PostgreSQL session variable using set_config().

        Args:
            key: Configuration parameter name (e.g., 'app.current_user_id')
            value: Value to set (None to unset)
        """
        if value is None:
            # Unset the variable
            sql = text("SELECT set_config(:key, NULL, false)")
        else:
            # Set the variable
            sql = text("SELECT set_config(:key, :value, false)")

        self.db.execute(sql, {"key": key, "value": value})


def set_rls_context(
    db: Session,
    user_id: int,
    role_name: Optional[str] = None,
    tenant_id: Optional[int] = None,
    branch_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
) -> None:
    """
    Convenience function to set RLS context without using context manager.

    This should be called at the START of every database session/transaction
    to ensure RLS policies are evaluated with the correct user context.

    Args:
        db: SQLAlchemy database session
        user_id: Current authenticated user's ID
        role_name: User's role name
        tenant_id: Tenant ID for multi-tenancy
        branch_id: User's assigned branch ID
        warehouse_id: User's assigned warehouse ID

    Example:
        from app.db.rls_context import set_rls_context

        # In a FastAPI dependency
        def get_current_user_db(db: Session, current_user: User):
            set_rls_context(
                db,
                user_id=current_user.id,
                role_name=current_user.role.name,
                tenant_id=current_user.tenant_id,
                branch_id=current_user.branch_id
            )
            return db
    """
    try:
        # Set user ID (REQUIRED)
        db.execute(
            text("SELECT set_config('app.current_user_id', :user_id, false)"),
            {"user_id": str(user_id)},
        )

        # Set optional context variables
        if role_name:
            db.execute(
                text("SELECT set_config('app.current_user_role', :role, false)"),
                {"role": role_name},
            )

        if tenant_id:
            db.execute(
                text("SELECT set_config('app.current_tenant_id', :tenant_id, false)"),
                {"tenant_id": str(tenant_id)},
            )

        if branch_id:
            db.execute(
                text("SELECT set_config('app.current_branch_id', :branch_id, false)"),
                {"branch_id": str(branch_id)},
            )

        if warehouse_id:
            db.execute(
                text(
                    "SELECT set_config('app.current_warehouse_id', :warehouse_id, false)"
                ),
                {"warehouse_id": str(warehouse_id)},
            )

        db.commit()

        logger.info(
            f"✅ RLS Context Set: user_id={user_id}, role={role_name}, "
            f"tenant={tenant_id}, branch={branch_id}, warehouse={warehouse_id}"
        )

    except Exception as e:
        logger.error(f"❌ Failed to set RLS context: {e}")
        db.rollback()
        raise


def get_current_user_from_rls(db: Session) -> Optional[int]:
    """
    Retrieve the current user ID from the RLS session variable.

    This can be useful for debugging or verification purposes.

    Args:
        db: SQLAlchemy database session

    Returns:
        Current user ID or None if not set
    """
    try:
        result = db.execute(
            text("SELECT current_setting('app.current_user_id', true)")
        ).scalar()

        if result:
            return int(result)
        return None

    except Exception as e:
        logger.warning(f"⚠️  Could not get current user from RLS context: {e}")
        return None


def verify_rls_enabled(db: Session) -> dict:
    """
    Verify that RLS is properly enabled on critical tables.

    Returns a dict with table names and their RLS status.

    Args:
        db: SQLAlchemy database session

    Returns:
        Dictionary mapping table names to RLS status
    """
    query = text(
        """
        SELECT tablename, rowsecurity
        FROM pg_tables
        WHERE schemaname = 'public'
          AND tablename IN ('users', 'customers', 'sales_orders', 'cash_transactions', 'expenses')
        ORDER BY tablename
    """
    )

    result = db.execute(query).fetchall()

    return {row[0]: row[1] for row in result}


def list_active_policies(db: Session) -> list[dict]:
    """
    List all active RLS policies in the database.

    Useful for auditing and debugging.

    Args:
        db: SQLAlchemy database session

    Returns:
        List of dictionaries containing policy information
    """
    query = text(
        """
        SELECT
            schemaname,
            tablename,
            policyname,
            permissive,
            roles,
            cmd,
            qual::text as using_clause,
            with_check::text as with_check_clause
        FROM pg_policies
        WHERE schemaname = 'public'
        ORDER BY tablename, policyname
    """
    )

    result = db.execute(query).fetchall()

    policies = []
    for row in result:
        policies.append(
            {
                "schema": row[0],
                "table": row[1],
                "policy_name": row[2],
                "permissive": row[3],
                "roles": row[4],
                "command": row[5],
                "using": row[6],
                "with_check": row[7],
            }
        )

    return policies
