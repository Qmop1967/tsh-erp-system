"""
Database Seeders for Test Data
================================

Provides functions to seed test database with realistic data.

Usage:
    from tests.fixtures import seed_test_database, seed_minimal, seed_full

    # Seed full dataset
    seed_test_database()

    # Seed minimal dataset
    seed_minimal()
"""

import sys
from pathlib import Path
from typing import Dict, List
from sqlalchemy.orm import Session

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.db.database import SessionLocal, Base, engine
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
    PositionFactory,
    CashBoxFactory,
    CashTransactionFactory,
)


class DatabaseSeeder:
    """Database seeder class"""

    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        self.created = {
            "roles": [],
            "branches": [],
            "warehouses": [],
            "users": [],
            "categories": [],
            "products": [],
            "inventory_items": [],
            "customers": [],
            "suppliers": [],
            "sales_orders": [],
            "sales_items": [],
            "purchase_orders": [],
            "purchase_items": [],
            "invoices": [],
            "pos_sessions": [],
            "pos_transactions": [],
            "departments": [],
            "positions": [],
            "employees": [],
            "cash_boxes": [],
            "cash_transactions": [],
        }

    def create_roles(self, count: int = 5) -> List:
        """Create roles"""
        print(f"📋 Creating {count} roles...")
        roles = []
        role_names = ["Admin", "Manager", "Salesperson", "Warehouse Staff", "Accountant"]
        for name in role_names[:count]:
            role = RoleFactory(name=name)
            roles.append(role)
        self.created["roles"] = roles
        print(f"✅ Created {len(roles)} roles")
        return roles

    def create_branches(self, count: int = 3) -> List:
        """Create branches"""
        print(f"🏢 Creating {count} branches...")
        branches = BranchFactory.create_batch(count)
        self.created["branches"] = branches
        print(f"✅ Created {len(branches)} branches")
        return branches

    def create_warehouses(self, branches: List, warehouses_per_branch: int = 2) -> List:
        """Create warehouses for branches"""
        print(f"🏭 Creating warehouses ({warehouses_per_branch} per branch)...")
        warehouses = []
        for branch in branches:
            for _ in range(warehouses_per_branch):
                warehouse = WarehouseFactory(branch_id=branch.id)
                warehouses.append(warehouse)
        self.created["warehouses"] = warehouses
        print(f"✅ Created {len(warehouses)} warehouses")
        return warehouses

    def create_users(self, roles: List, branches: List, users_per_role: int = 2) -> List:
        """Create users"""
        print(f"👥 Creating users ({users_per_role} per role)...")
        users = []
        for role in roles:
            for i in range(users_per_role):
                branch = branches[i % len(branches)]
                user = UserFactory(role_id=role.id, branch_id=branch.id)
                users.append(user)
        self.created["users"] = users
        print(f"✅ Created {len(users)} users")
        return users

    def create_categories(self, count: int = 10) -> List:
        """Create product categories"""
        print(f"📁 Creating {count} categories...")
        categories = CategoryFactory.create_batch(count)
        self.created["categories"] = categories
        print(f"✅ Created {len(categories)} categories")
        return categories

    def create_products(self, categories: List, products_per_category: int = 10) -> List:
        """Create products"""
        print(f"📦 Creating products ({products_per_category} per category)...")
        products = []
        for category in categories:
            for _ in range(products_per_category):
                product = ProductFactory(category_id=category.id)
                products.append(product)
        self.created["products"] = products
        print(f"✅ Created {len(products)} products")
        return products

    def create_inventory(self, products: List, warehouses: List) -> List:
        """Create inventory items"""
        print(f"📊 Creating inventory items...")
        inventory_items = []
        for product in products:
            # Create inventory in 1-2 random warehouses
            import random
            selected_warehouses = random.sample(warehouses, min(2, len(warehouses)))
            for warehouse in selected_warehouses:
                inventory_item = InventoryItemFactory(
                    product_id=product.id,
                    warehouse_id=warehouse.id
                )
                inventory_items.append(inventory_item)
        self.created["inventory_items"] = inventory_items
        print(f"✅ Created {len(inventory_items)} inventory items")
        return inventory_items

    def create_customers(self, count: int = 50) -> List:
        """Create customers"""
        print(f"🤝 Creating {count} customers...")
        customers = CustomerFactory.create_batch(count)
        self.created["customers"] = customers
        print(f"✅ Created {len(customers)} customers")
        return customers

    def create_suppliers(self, count: int = 20) -> List:
        """Create suppliers"""
        print(f"🏭 Creating {count} suppliers...")
        suppliers = SupplierFactory.create_batch(count)
        self.created["suppliers"] = suppliers
        print(f"✅ Created {len(suppliers)} suppliers")
        return suppliers

    def create_sales_orders(self, customers: List, branches: List, users: List, count: int = 100) -> List:
        """Create sales orders with items"""
        print(f"💰 Creating {count} sales orders...")
        sales_orders = []
        sales_items = []

        import random
        for _ in range(count):
            customer = random.choice(customers)
            branch = random.choice(branches)
            user = random.choice(users)

            order = SalesOrderFactory(
                customer_id=customer.id,
                branch_id=branch.id,
                user_id=user.id
            )
            sales_orders.append(order)

            # Create 1-5 items per order
            items_count = random.randint(1, 5)
            products = random.sample(self.created["products"], min(items_count, len(self.created["products"])))
            for product in products:
                item = SalesItemFactory(
                    sales_order_id=order.id,
                    product_id=product.id
                )
                sales_items.append(item)

        self.created["sales_orders"] = sales_orders
        self.created["sales_items"] = sales_items
        print(f"✅ Created {len(sales_orders)} sales orders with {len(sales_items)} items")
        return sales_orders

    def create_purchase_orders(self, suppliers: List, branches: List, users: List, count: int = 50) -> List:
        """Create purchase orders with items"""
        print(f"📥 Creating {count} purchase orders...")
        purchase_orders = []
        purchase_items = []

        import random
        for _ in range(count):
            supplier = random.choice(suppliers)
            branch = random.choice(branches)
            user = random.choice(users)

            order = PurchaseOrderFactory(
                supplier_id=supplier.id,
                branch_id=branch.id,
                user_id=user.id
            )
            purchase_orders.append(order)

            # Create 5-10 items per order
            items_count = random.randint(5, 10)
            products = random.sample(self.created["products"], min(items_count, len(self.created["products"])))
            for product in products:
                item = PurchaseItemFactory(
                    purchase_order_id=order.id,
                    product_id=product.id
                )
                purchase_items.append(item)

        self.created["purchase_orders"] = purchase_orders
        self.created["purchase_items"] = purchase_items
        print(f"✅ Created {len(purchase_orders)} purchase orders with {len(purchase_items)} items")
        return purchase_orders

    def create_invoices(self, count: int = 80) -> List:
        """Create invoices"""
        print(f"🧾 Creating {count} invoices...")
        import random
        invoices = []

        # Get confirmed sales orders
        confirmed_orders = [o for o in self.created["sales_orders"] if o.status in ["confirmed", "delivered"]]
        selected_orders = random.sample(confirmed_orders, min(count, len(confirmed_orders)))

        for order in selected_orders:
            invoice = InvoiceFactory(
                customer_id=order.customer_id,
                sales_order_id=order.id,
                subtotal=order.subtotal,
                tax_amount=order.tax_amount,
                discount_amount=order.discount_amount,
                total_amount=order.total_amount
            )
            invoices.append(invoice)

        self.created["invoices"] = invoices
        print(f"✅ Created {len(invoices)} invoices")
        return invoices

    def create_pos_data(self, users: List, branches: List, count: int = 20) -> List:
        """Create POS sessions and transactions"""
        print(f"🛒 Creating {count} POS sessions...")
        import random
        pos_sessions = []
        pos_transactions = []

        for _ in range(count):
            user = random.choice(users)
            branch = random.choice(branches)

            session = POSSessionFactory(
                user_id=user.id,
                branch_id=branch.id
            )
            pos_sessions.append(session)

            # Create 5-20 transactions per session
            transactions_count = random.randint(5, 20)
            for _ in range(transactions_count):
                customer = random.choice(self.created["customers"]) if random.random() > 0.3 else None
                transaction = POSTransactionFactory(
                    session_id=session.id,
                    customer_id=customer.id if customer else None
                )
                pos_transactions.append(transaction)

        self.created["pos_sessions"] = pos_sessions
        self.created["pos_transactions"] = pos_transactions
        print(f"✅ Created {len(pos_sessions)} POS sessions with {len(pos_transactions)} transactions")
        return pos_sessions

    def create_hr_data(self, branches: List, count: int = 20) -> List:
        """Create HR data (departments, positions, employees)"""
        print(f"👔 Creating HR data...")

        # Create departments
        departments = DepartmentFactory.create_batch(8)
        self.created["departments"] = departments

        # Create positions
        positions = []
        for dept in departments:
            dept_positions = PositionFactory.create_batch(2, department_id=dept.id)
            positions.extend(dept_positions)
        self.created["positions"] = positions

        # Create employees
        import random
        employees = []
        for _ in range(count):
            dept = random.choice(departments)
            position = random.choice([p for p in positions if p.department_id == dept.id])

            # Create user for employee
            branch = random.choice(branches)
            user = UserFactory(branch_id=branch.id, role_id=self.created["roles"][2].id)  # Salesperson role

            employee = EmployeeFactory(
                user_id=user.id,
                department_id=dept.id,
                position_id=position.id
            )
            employees.append(employee)

        self.created["employees"] = employees
        print(f"✅ Created {len(departments)} departments, {len(positions)} positions, {len(employees)} employees")
        return employees

    def create_cash_flow_data(self, branches: List, users: List, count: int = 30) -> List:
        """Create cash flow data"""
        print(f"💵 Creating cash flow data...")
        import random

        # Create cash boxes
        cash_boxes = []
        for branch in branches:
            box = CashBoxFactory(
                branch_id=branch.id,
                user_id=random.choice(users).id
            )
            cash_boxes.append(box)
        self.created["cash_boxes"] = cash_boxes

        # Create cash transactions
        cash_transactions = []
        for _ in range(count):
            box = random.choice(cash_boxes)
            transaction = CashTransactionFactory(
                cash_box_id=box.id,
                created_by=random.choice(users).id
            )
            cash_transactions.append(transaction)

        self.created["cash_transactions"] = cash_transactions
        print(f"✅ Created {len(cash_boxes)} cash boxes with {len(cash_transactions)} transactions")
        return cash_boxes

    def get_summary(self) -> Dict:
        """Get seeding summary"""
        return {
            key: len(value) for key, value in self.created.items()
        }


# ============================================================================
# Seeder Functions
# ============================================================================

def seed_minimal(db: Session = None) -> Dict:
    """
    Seed minimal test data (fast, for quick tests)

    Creates:
    - 3 roles
    - 2 branches
    - 4 warehouses
    - 6 users
    - 5 categories
    - 20 products
    - 10 customers
    - 5 suppliers
    """
    print("\n" + "=" * 60)
    print("🌱 SEEDING MINIMAL TEST DATA")
    print("=" * 60)

    seeder = DatabaseSeeder(db)

    # Core data
    roles = seeder.create_roles(count=3)
    branches = seeder.create_branches(count=2)
    warehouses = seeder.create_warehouses(branches, warehouses_per_branch=2)
    users = seeder.create_users(roles, branches, users_per_role=2)

    # Product data
    categories = seeder.create_categories(count=5)
    products = seeder.create_products(categories, products_per_category=4)
    seeder.create_inventory(products, warehouses)

    # Customer/Supplier data
    seeder.create_customers(count=10)
    seeder.create_suppliers(count=5)

    summary = seeder.get_summary()
    print("\n" + "=" * 60)
    print("✅ MINIMAL SEEDING COMPLETE")
    print("=" * 60)
    for key, count in summary.items():
        if count > 0:
            print(f"  {key}: {count}")
    print("=" * 60 + "\n")

    return summary


def seed_full(db: Session = None) -> Dict:
    """
    Seed full test data (comprehensive, for integration tests)

    Creates:
    - 5 roles
    - 5 branches
    - 10 warehouses
    - 20 users
    - 10 categories
    - 100 products
    - 200 inventory items
    - 50 customers
    - 20 suppliers
    - 100 sales orders
    - 50 purchase orders
    - 80 invoices
    - 20 POS sessions
    - 20 employees
    - 30 cash transactions
    """
    print("\n" + "=" * 60)
    print("🌱 SEEDING FULL TEST DATA")
    print("=" * 60)

    seeder = DatabaseSeeder(db)

    # Core data
    roles = seeder.create_roles(count=5)
    branches = seeder.create_branches(count=5)
    warehouses = seeder.create_warehouses(branches, warehouses_per_branch=2)
    users = seeder.create_users(roles, branches, users_per_role=4)

    # Product data
    categories = seeder.create_categories(count=10)
    products = seeder.create_products(categories, products_per_category=10)
    seeder.create_inventory(products, warehouses)

    # Customer/Supplier data
    customers = seeder.create_customers(count=50)
    suppliers = seeder.create_suppliers(count=20)

    # Transactions
    seeder.create_sales_orders(customers, branches, users, count=100)
    seeder.create_purchase_orders(suppliers, branches, users, count=50)
    seeder.create_invoices(count=80)
    seeder.create_pos_data(users, branches, count=20)

    # HR and Cash Flow
    seeder.create_hr_data(branches, count=20)
    seeder.create_cash_flow_data(branches, users, count=30)

    summary = seeder.get_summary()
    print("\n" + "=" * 60)
    print("✅ FULL SEEDING COMPLETE")
    print("=" * 60)
    for key, count in summary.items():
        if count > 0:
            print(f"  {key}: {count}")
    print("=" * 60 + "\n")

    return summary


def seed_test_database(dataset: str = "full", db: Session = None) -> Dict:
    """
    Main seeding function

    Args:
        dataset: Type of dataset to seed ("minimal" or "full")
        db: Database session (optional)

    Returns:
        Dictionary with seeding summary
    """
    if dataset == "minimal":
        return seed_minimal(db)
    else:
        return seed_full(db)


# ============================================================================
# CLI Entry Point
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed TSH ERP test database")
    parser.add_argument(
        "--dataset",
        choices=["minimal", "full"],
        default="full",
        help="Dataset size to seed (default: full)"
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Recreate all tables before seeding"
    )

    args = parser.parse_args()

    if args.recreate:
        print("⚠️  Recreating all database tables...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("✅ Tables recreated")

    seed_test_database(dataset=args.dataset)
