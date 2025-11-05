"""
Router Registry
===============

Central registry for all FastAPI routers to replace manual router imports
in main.py. Provides automatic router discovery and registration.

Usage in main.py:
    from app.core.router_registry import register_all_routers
    register_all_routers(app)
"""
from typing import Dict, List, Optional
from fastapi import APIRouter, FastAPI
import logging

logger = logging.getLogger(__name__)


class RouterRegistry:
    """Registry for managing FastAPI routers"""

    def __init__(self):
        self._routers: Dict[str, RouterConfig] = {}
        self._registered = False

    def register(
        self,
        router: APIRouter,
        prefix: str = "",
        tags: Optional[List[str]] = None,
        dependencies: Optional[List] = None,
        priority: int = 100,
        enabled: bool = True,
    ):
        """
        Register a router with configuration.

        Args:
            router: The FastAPI router to register
            prefix: URL prefix for all routes (e.g., "/api/v1/users")
            tags: OpenAPI tags for grouping endpoints
            dependencies: List of FastAPI dependencies
            priority: Registration priority (lower = earlier, 0-1000)
            enabled: Whether router should be registered
        """
        if not enabled:
            logger.debug(f"Router {prefix} is disabled, skipping registration")
            return

        config = RouterConfig(
            router=router,
            prefix=prefix,
            tags=tags or [],
            dependencies=dependencies or [],
            priority=priority,
        )

        self._routers[prefix] = config
        logger.info(f"Registered router: {prefix} (priority: {priority})")

    def register_all(self, app: FastAPI):
        """Register all routers with the FastAPI app"""
        if self._registered:
            logger.warning("Routers already registered, skipping")
            return

        # Sort by priority (lower priority = registered first)
        sorted_routers = sorted(
            self._routers.items(),
            key=lambda x: x[1].priority
        )

        registered_count = 0
        for prefix, config in sorted_routers:
            try:
                app.include_router(
                    config.router,
                    prefix=config.prefix,
                    tags=config.tags,
                    dependencies=config.dependencies,
                )
                registered_count += 1
                logger.info(f"✓ Registered: {prefix}")
            except Exception as e:
                logger.error(f"✗ Failed to register {prefix}: {e}")
                raise

        self._registered = True
        logger.info(f"Successfully registered {registered_count} routers")

    def get_registered_routers(self) -> List[str]:
        """Get list of registered router prefixes"""
        return list(self._routers.keys())

    def clear(self):
        """Clear all registered routers (mainly for testing)"""
        self._routers.clear()
        self._registered = False


class RouterConfig:
    """Configuration for a registered router"""

    def __init__(
        self,
        router: APIRouter,
        prefix: str,
        tags: List[str],
        dependencies: List,
        priority: int,
    ):
        self.router = router
        self.prefix = prefix
        self.tags = tags
        self.dependencies = dependencies
        self.priority = priority


# Global registry instance
registry = RouterRegistry()


def register_all_routers(app: FastAPI):
    """
    Register all routers with the FastAPI application.

    This function imports and registers all routers from the app/routers directory.
    Call this once from main.py after creating the FastAPI app.

    Example:
        from app.core.router_registry import register_all_routers
        app = FastAPI()
        register_all_routers(app)
    """
    # Import all routers (this triggers their registration via @router decorators)
    from app.routers import (
        branches_router,
        customers_router,
        sales_router,
        inventory_router,
        accounting_router,
        pos_router,
        cashflow_router,
    )
    from app.routers.products import router as products_router
    from app.routers.auth import router as auth_router
    from app.routers.users import router as users_router
    from app.routers.pricelists import router as pricelists_router
    from app.routers.price_list_items import router as price_list_items_router
    from app.routers.tds_sync_queue import router as tds_sync_queue_router
    from app.routers.tds_sync_log import router as tds_sync_log_router
    from app.routers.tds_entity_mapping import router as tds_entity_mapping_router

    # Register all routers with proper prefixes and tags
    # Priority 0: Health & System (highest priority)
    # Priority 50: Authentication & Users
    # Priority 100: Business entities (default)
    # Priority 200: Admin & sync

    # Authentication & Users (Priority 50)
    registry.register(
        auth_router,
        prefix="/auth",
        tags=["Authentication"],
        priority=50,
    )
    registry.register(
        users_router,
        prefix="/users",
        tags=["Users"],
        priority=50,
    )

    # Business Entities (Priority 100)
    registry.register(
        branches_router,
        prefix="/branches",
        tags=["Branches"],
        priority=100,
    )
    registry.register(
        customers_router,
        prefix="/customers",
        tags=["Customers"],
        priority=100,
    )
    registry.register(
        products_router,
        prefix="/products",
        tags=["Products"],
        priority=100,
    )
    registry.register(
        pricelists_router,
        prefix="/pricelists",
        tags=["Price Lists"],
        priority=100,
    )
    registry.register(
        price_list_items_router,
        prefix="/price-list-items",
        tags=["Price List Items"],
        priority=100,
    )

    # Business Operations (Priority 150)
    registry.register(
        sales_router,
        prefix="/sales",
        tags=["Sales"],
        priority=150,
    )
    registry.register(
        inventory_router,
        prefix="/inventory",
        tags=["Inventory"],
        priority=150,
    )
    registry.register(
        accounting_router,
        prefix="/accounting",
        tags=["Accounting"],
        priority=150,
    )
    registry.register(
        pos_router,
        prefix="/pos",
        tags=["Point of Sale"],
        priority=150,
    )
    registry.register(
        cashflow_router,
        prefix="/cashflow",
        tags=["Cash Flow"],
        priority=150,
    )

    # Admin & Sync Operations (Priority 200)
    registry.register(
        tds_sync_queue_router,
        prefix="/tds/sync-queue",
        tags=["TDS Sync"],
        priority=200,
    )
    registry.register(
        tds_sync_log_router,
        prefix="/tds/sync-log",
        tags=["TDS Sync"],
        priority=200,
    )
    registry.register(
        tds_entity_mapping_router,
        prefix="/tds/entity-mapping",
        tags=["TDS Sync"],
        priority=200,
    )

    # Register all routers with the app
    registry.register_all(app)
    logger.info(f"Router registry initialized with {len(registry.get_registered_routers())} routers")


def get_registry() -> RouterRegistry:
    """Get the global router registry instance"""
    return registry
