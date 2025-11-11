"""
Test Data Fixtures and Factories
===================================

This package provides factory-based test data generation for TSH ERP tests.

Usage:
    from tests.fixtures import UserFactory, ProductFactory

    user = UserFactory()
    product = ProductFactory()
"""

from .factories import (
    UserFactory,
    RoleFactory,
    BranchFactory,
    WarehouseFactory,
    CategoryFactory,
    ProductFactory,
    CustomerFactory,
    SupplierFactory,
    InventoryItemFactory,
    SalesOrderFactory,
    SalesItemFactory,
    PurchaseOrderFactory,
    PurchaseItemFactory,
    InvoiceFactory,
    POSSessionFactory,
    POSTransactionFactory,
    EmployeeFactory,
    DepartmentFactory,
)

from .seeders import seed_test_database, seed_minimal, seed_full

__all__ = [
    # Factories
    "UserFactory",
    "RoleFactory",
    "BranchFactory",
    "WarehouseFactory",
    "CategoryFactory",
    "ProductFactory",
    "CustomerFactory",
    "SupplierFactory",
    "InventoryItemFactory",
    "SalesOrderFactory",
    "SalesItemFactory",
    "PurchaseOrderFactory",
    "PurchaseItemFactory",
    "InvoiceFactory",
    "POSSessionFactory",
    "POSTransactionFactory",
    "EmployeeFactory",
    "DepartmentFactory",
    # Seeders
    "seed_test_database",
    "seed_minimal",
    "seed_full",
]
