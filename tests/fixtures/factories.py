"""
Factory Classes for Test Data Generation
==========================================

Uses factory_boy to generate realistic test data for TSH ERP models.

Example:
    user = UserFactory()
    product = ProductFactory(name="Test Product", price=100)
    order = SalesOrderFactory(customer=customer, items__size=5)
"""

import factory
from factory import fuzzy
from datetime import datetime, timedelta
from decimal import Decimal
import random

from app.db.database import SessionLocal
from app.models import (
    User, Role, Branch, Warehouse,
    Category, Product, Customer, Supplier,
    InventoryItem, StockMovement,
    SalesOrder, SalesItem,
    PurchaseOrder, PurchaseItem,
    SalesInvoice, SalesInvoiceItem,
    POSSession, POSTransaction, POSTransactionItem,
    Employee, Department, Position,
    CashBox, CashTransaction,
)


# ============================================================================
# Base Factory
# ============================================================================

class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Base factory with common configuration"""

    class Meta:
        abstract = True
        sqlalchemy_session = SessionLocal()
        sqlalchemy_session_persistence = "commit"


# ============================================================================
# User & Authentication Factories
# ============================================================================

class RoleFactory(BaseFactory):
    """Factory for Role model"""

    class Meta:
        model = Role

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Iterator(["Admin", "Manager", "Salesperson", "Warehouse Staff", "Accountant"])
    description = factory.LazyAttribute(lambda obj: f"{obj.name} role with full access")
    is_active = True


class BranchFactory(BaseFactory):
    """Factory for Branch model"""

    class Meta:
        model = Branch

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker('city')
    code = factory.Sequence(lambda n: f"BR{n:03d}")
    address = factory.Faker('address')
    phone = factory.LazyAttribute(lambda o: f'+964-{fuzzy.FuzzyInteger(7000, 7999).fuzz()}-{fuzzy.FuzzyInteger(1000000, 9999999).fuzz()}')
    is_active = True
    created_at = factory.LazyFunction(datetime.utcnow)


class UserFactory(BaseFactory):
    """Factory for User model"""

    class Meta:
        model = User

    id = factory.Sequence(lambda n: n + 1)
    email = factory.Faker('email')
    name = factory.Faker('name')
    password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyKjH0UBj3gO"  # "password123" (hashed)
    is_active = True
    role_id = factory.SubFactory(RoleFactory)
    branch_id = factory.SubFactory(BranchFactory)
    created_at = factory.LazyFunction(datetime.utcnow)

    @factory.post_generation
    def role(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.role_id = extracted.id


# ============================================================================
# Warehouse & Inventory Factories
# ============================================================================

class WarehouseFactory(BaseFactory):
    """Factory for Warehouse model"""

    class Meta:
        model = Warehouse

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker('company')
    # code, location, is_active removed - not in Warehouse model
    branch_id = factory.SubFactory(BranchFactory)


class CategoryFactory(BaseFactory):
    """Factory for Category model"""

    class Meta:
        model = Category

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Iterator([
        "Electronics", "Furniture", "Office Supplies", "Hardware",
        "Software", "Accessories", "Components", "Tools"
    ])
    description = factory.LazyAttribute(lambda obj: f"{obj.name} category")
    parent_id = None
    is_active = True


class ProductFactory(BaseFactory):
    """Factory for Product model"""

    class Meta:
        model = Product

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker('catch_phrase')
    sku = factory.Sequence(lambda n: f"SKU{n:06d}")
    barcode = factory.Faker('ean13')
    description = factory.Faker('text', max_nb_chars=200)
    unit_price = fuzzy.FuzzyDecimal(10.0, 1000.0, 2)
    cost_price = factory.LazyAttribute(lambda obj: obj.unit_price * Decimal('0.7'))
    category_id = factory.SubFactory(CategoryFactory)
    unit_of_measure = factory.Iterator(["pcs", "box", "kg", "meter", "liter"])
    reorder_point = fuzzy.FuzzyInteger(10, 50)  # Fixed: was reorder_level
    min_stock_level = fuzzy.FuzzyInteger(5, 20)
    # is_active removed - not in Product model
    created_at = factory.LazyFunction(datetime.utcnow)

    @factory.post_generation
    def set_prices(self, create, extracted, **kwargs):
        """Ensure cost price is less than unit price"""
        if create and self.cost_price >= self.unit_price:
            self.cost_price = self.unit_price * Decimal('0.7')


class InventoryItemFactory(BaseFactory):
    """Factory for InventoryItem model"""

    class Meta:
        model = InventoryItem

    id = factory.Sequence(lambda n: n + 1)
    product_id = factory.SubFactory(ProductFactory)
    warehouse_id = factory.SubFactory(WarehouseFactory)
    quantity_on_hand = fuzzy.FuzzyDecimal(100.0, 1000.0, 3)  # Fixed: was 'quantity'
    quantity_reserved = fuzzy.FuzzyDecimal(0.0, 50.0, 3)  # Fixed: was 'reserved_quantity'
    quantity_ordered = fuzzy.FuzzyDecimal(0.0, 100.0, 3)
    # available_quantity removed - not in model (calculate from on_hand - reserved)
    # last_updated removed - model has created_at, updated_at


# ============================================================================
# Customer & Supplier Factories
# ============================================================================

class CustomerFactory(BaseFactory):
    """Factory for Customer model"""

    class Meta:
        model = Customer

    id = factory.Sequence(lambda n: n + 1)
    customer_code = factory.Sequence(lambda n: f"CUST{n:06d}")  # Required unique field
    name = factory.Faker('company')
    company_name = factory.Faker('company')
    email = factory.Faker('company_email')
    phone = factory.LazyAttribute(lambda o: f'+964-{fuzzy.FuzzyInteger(7000, 7999).fuzz()}-{fuzzy.FuzzyInteger(1000000, 9999999).fuzz()}')
    # mobile removed - not in Customer model
    address = factory.Faker('address')
    city = factory.Faker('city')
    country = "Iraq"
    tax_number = factory.Sequence(lambda n: f"TAX{n:08d}")
    credit_limit = fuzzy.FuzzyDecimal(10000, 100000, 2)
    payment_terms = 30  # Days
    discount_percentage = fuzzy.FuzzyDecimal(0, 10, 2)
    currency = "IQD"
    portal_language = "en"
    # current_balance removed - not in Customer model
    # customer_type removed - not in Customer model
    is_active = True
    # created_at removed - auto-generated by server_default


class SupplierFactory(BaseFactory):
    """Factory for Supplier model"""

    class Meta:
        model = Supplier

    id = factory.Sequence(lambda n: n + 1)
    supplier_code = factory.Sequence(lambda n: f"SUPP{n:06d}")  # Required unique field
    name = factory.Faker('company')
    company_name = factory.Faker('company')
    email = factory.Faker('company_email')
    phone = factory.LazyAttribute(lambda o: f'+964-{fuzzy.FuzzyInteger(7000, 7999).fuzz()}-{fuzzy.FuzzyInteger(1000000, 9999999).fuzz()}')
    address = factory.Faker('address')
    city = factory.Faker('city')
    country = factory.Iterator(["China", "Turkey", "UAE", "Germany", "USA"])
    tax_number = factory.Sequence(lambda n: f"SUPTAX{n:08d}")
    payment_terms = fuzzy.FuzzyChoice([30, 60, 90])  # Integer days, not strings
    is_active = True
    # created_at removed - auto-generated by server_default


# ============================================================================
# Sales Factories
# ============================================================================

class SalesOrderFactory(BaseFactory):
    """Factory for SalesOrder model"""

    class Meta:
        model = SalesOrder

    id = factory.Sequence(lambda n: n + 1)
    order_number = factory.Sequence(lambda n: f"SO{n:08d}")
    customer_id = factory.SubFactory(CustomerFactory)
    branch_id = factory.SubFactory(BranchFactory)
    user_id = factory.SubFactory(UserFactory)
    order_date = factory.LazyFunction(datetime.utcnow)
    delivery_date = factory.LazyAttribute(
        lambda obj: obj.order_date + timedelta(days=random.randint(3, 14))
    )
    status = factory.Iterator(["draft", "pending", "confirmed", "delivered", "cancelled"])
    subtotal = fuzzy.FuzzyDecimal(1000, 50000, 2)
    tax_amount = factory.LazyAttribute(lambda obj: obj.subtotal * Decimal('0.15'))
    discount_amount = fuzzy.FuzzyDecimal(0, 500, 2)
    total_amount = factory.LazyAttribute(
        lambda obj: obj.subtotal + obj.tax_amount - obj.discount_amount
    )
    notes = factory.Faker('sentence')
    created_at = factory.LazyFunction(datetime.utcnow)


class SalesItemFactory(BaseFactory):
    """Factory for SalesItem model"""

    class Meta:
        model = SalesItem

    id = factory.Sequence(lambda n: n + 1)
    sales_order_id = factory.SubFactory(SalesOrderFactory)
    product_id = factory.SubFactory(ProductFactory)
    quantity = fuzzy.FuzzyInteger(1, 100)
    unit_price = fuzzy.FuzzyDecimal(10, 1000, 2)
    discount_percent = fuzzy.FuzzyDecimal(0, 15, 2)
    discount_amount = factory.LazyAttribute(
        lambda obj: (obj.unit_price * obj.quantity * obj.discount_percent) / 100
    )
    tax_percent = Decimal('15.00')
    tax_amount = factory.LazyAttribute(
        lambda obj: ((obj.unit_price * obj.quantity - obj.discount_amount) * obj.tax_percent) / 100
    )
    total_amount = factory.LazyAttribute(
        lambda obj: obj.unit_price * obj.quantity - obj.discount_amount + obj.tax_amount
    )


# ============================================================================
# Purchase Factories
# ============================================================================

class PurchaseOrderFactory(BaseFactory):
    """Factory for PurchaseOrder model"""

    class Meta:
        model = PurchaseOrder

    id = factory.Sequence(lambda n: n + 1)
    order_number = factory.Sequence(lambda n: f"PO{n:08d}")
    supplier_id = factory.SubFactory(SupplierFactory)
    branch_id = factory.SubFactory(BranchFactory)
    user_id = factory.SubFactory(UserFactory)
    order_date = factory.LazyFunction(datetime.utcnow)
    expected_delivery = factory.LazyAttribute(
        lambda obj: obj.order_date + timedelta(days=random.randint(7, 30))
    )
    status = factory.Iterator(["draft", "pending", "approved", "received", "cancelled"])
    subtotal = fuzzy.FuzzyDecimal(5000, 100000, 2)
    tax_amount = factory.LazyAttribute(lambda obj: obj.subtotal * Decimal('0.15'))
    total_amount = factory.LazyAttribute(lambda obj: obj.subtotal + obj.tax_amount)
    notes = factory.Faker('sentence')
    created_at = factory.LazyFunction(datetime.utcnow)


class PurchaseItemFactory(BaseFactory):
    """Factory for PurchaseItem model"""

    class Meta:
        model = PurchaseItem

    id = factory.Sequence(lambda n: n + 1)
    purchase_order_id = factory.SubFactory(PurchaseOrderFactory)
    product_id = factory.SubFactory(ProductFactory)
    quantity = fuzzy.FuzzyInteger(10, 500)
    unit_price = fuzzy.FuzzyDecimal(5, 500, 2)
    tax_percent = Decimal('15.00')
    tax_amount = factory.LazyAttribute(
        lambda obj: (obj.unit_price * obj.quantity * obj.tax_percent) / 100
    )
    total_amount = factory.LazyAttribute(
        lambda obj: obj.unit_price * obj.quantity + obj.tax_amount
    )


# ============================================================================
# Invoice Factories
# ============================================================================

class InvoiceFactory(BaseFactory):
    """Factory for SalesInvoice model"""

    class Meta:
        model = SalesInvoice

    id = factory.Sequence(lambda n: n + 1)
    invoice_number = factory.Sequence(lambda n: f"INV{n:08d}")
    customer_id = factory.SubFactory(CustomerFactory)
    sales_order_id = factory.SubFactory(SalesOrderFactory)
    invoice_date = factory.LazyFunction(datetime.utcnow)
    due_date = factory.LazyAttribute(
        lambda obj: obj.invoice_date + timedelta(days=30)
    )
    status = factory.Iterator(["draft", "sent", "paid", "overdue", "cancelled"])
    subtotal = fuzzy.FuzzyDecimal(1000, 50000, 2)
    tax_amount = factory.LazyAttribute(lambda obj: obj.subtotal * Decimal('0.15'))
    discount_amount = fuzzy.FuzzyDecimal(0, 1000, 2)
    total_amount = factory.LazyAttribute(
        lambda obj: obj.subtotal + obj.tax_amount - obj.discount_amount
    )
    paid_amount = Decimal('0.00')
    balance = factory.LazyAttribute(lambda obj: obj.total_amount - obj.paid_amount)
    notes = factory.Faker('sentence')
    created_at = factory.LazyFunction(datetime.utcnow)


# ============================================================================
# POS Factories
# ============================================================================

class POSSessionFactory(BaseFactory):
    """Factory for POSSession model"""

    class Meta:
        model = POSSession

    id = factory.Sequence(lambda n: n + 1)
    session_number = factory.Sequence(lambda n: f"POS{n:08d}")
    user_id = factory.SubFactory(UserFactory)
    branch_id = factory.SubFactory(BranchFactory)
    start_time = factory.LazyFunction(datetime.utcnow)
    end_time = None
    starting_cash = fuzzy.FuzzyDecimal(1000, 5000, 2)
    closing_cash = Decimal('0.00')
    expected_cash = Decimal('0.00')
    cash_difference = Decimal('0.00')
    status = factory.Iterator(["open", "closed"])
    notes = factory.Faker('sentence')


class POSTransactionFactory(BaseFactory):
    """Factory for POSTransaction model"""

    class Meta:
        model = POSTransaction

    id = factory.Sequence(lambda n: n + 1)
    transaction_number = factory.Sequence(lambda n: f"TX{n:010d}")
    session_id = factory.SubFactory(POSSessionFactory)
    customer_id = factory.SubFactory(CustomerFactory)
    transaction_date = factory.LazyFunction(datetime.utcnow)
    subtotal = fuzzy.FuzzyDecimal(100, 5000, 2)
    tax_amount = factory.LazyAttribute(lambda obj: obj.subtotal * Decimal('0.15'))
    discount_amount = fuzzy.FuzzyDecimal(0, 200, 2)
    total_amount = factory.LazyAttribute(
        lambda obj: obj.subtotal + obj.tax_amount - obj.discount_amount
    )
    payment_method = factory.Iterator(["cash", "card", "mobile", "credit"])
    status = factory.Iterator(["completed", "cancelled", "refunded"])
    notes = factory.Faker('sentence')


# ============================================================================
# HR Factories
# ============================================================================

class DepartmentFactory(BaseFactory):
    """Factory for Department model"""

    class Meta:
        model = Department

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Iterator([
        "Sales", "Operations", "Finance", "HR", "IT",
        "Warehouse", "Logistics", "Customer Service"
    ])
    code = factory.Sequence(lambda n: f"DEPT{n:03d}")
    description = factory.LazyAttribute(lambda obj: f"{obj.name} Department")
    manager_id = None
    is_active = True


class PositionFactory(BaseFactory):
    """Factory for Position model"""

    class Meta:
        model = Position

    id = factory.Sequence(lambda n: n + 1)
    title = factory.Iterator([
        "Sales Manager", "Sales Representative", "Warehouse Manager",
        "Warehouse Staff", "Accountant", "HR Manager", "IT Manager",
        "Operations Manager", "Customer Service Rep"
    ])
    code = factory.Sequence(lambda n: f"POS{n:03d}")
    department_id = factory.SubFactory(DepartmentFactory)
    description = factory.Faker('text', max_nb_chars=100)
    min_salary = fuzzy.FuzzyDecimal(500, 1500, 2)
    max_salary = factory.LazyAttribute(lambda obj: obj.min_salary * Decimal('2'))
    is_active = True


class EmployeeFactory(BaseFactory):
    """Factory for Employee model"""

    class Meta:
        model = Employee

    id = factory.Sequence(lambda n: n + 1)
    employee_id = factory.Sequence(lambda n: f"EMP{n:05d}")
    user_id = factory.SubFactory(UserFactory)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    phone = factory.LazyAttribute(lambda o: f'+964-{fuzzy.FuzzyInteger(7000, 7999).fuzz()}-{fuzzy.FuzzyInteger(1000000, 9999999).fuzz()}')
    date_of_birth = factory.Faker('date_of_birth', minimum_age=22, maximum_age=55)
    hire_date = factory.LazyFunction(datetime.utcnow)
    department_id = factory.SubFactory(DepartmentFactory)
    position_id = factory.SubFactory(PositionFactory)
    salary = fuzzy.FuzzyDecimal(600, 3000, 2)
    status = "active"
    is_active = True


# ============================================================================
# Cash Flow Factories
# ============================================================================

class CashBoxFactory(BaseFactory):
    """Factory for CashBox model"""

    class Meta:
        model = CashBox

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker('word')
    branch_id = factory.SubFactory(BranchFactory)
    user_id = factory.SubFactory(UserFactory)
    opening_balance = fuzzy.FuzzyDecimal(1000, 10000, 2)
    current_balance = factory.LazyAttribute(lambda obj: obj.opening_balance)
    is_active = True
    created_at = factory.LazyFunction(datetime.utcnow)


class CashTransactionFactory(BaseFactory):
    """Factory for CashTransaction model"""

    class Meta:
        model = CashTransaction

    id = factory.Sequence(lambda n: n + 1)
    transaction_number = factory.Sequence(lambda n: f"CT{n:010d}")
    cash_box_id = factory.SubFactory(CashBoxFactory)
    transaction_type = factory.Iterator(["income", "expense", "transfer"])
    amount = fuzzy.FuzzyDecimal(100, 5000, 2)
    description = factory.Faker('sentence')
    reference_number = factory.Sequence(lambda n: f"REF{n:08d}")
    transaction_date = factory.LazyFunction(datetime.utcnow)
    created_by = factory.SubFactory(UserFactory)
    created_at = factory.LazyFunction(datetime.utcnow)


# ============================================================================
# Batch Factories with Relations
# ============================================================================

class SalesOrderWithItemsFactory(SalesOrderFactory):
    """Factory for SalesOrder with related items"""

    @factory.post_generation
    def items(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            # Use provided items
            for item in extracted:
                item.sales_order_id = self.id
        else:
            # Create default items
            items_count = kwargs.get('size', 3)
            for _ in range(items_count):
                SalesItemFactory(sales_order_id=self.id)
