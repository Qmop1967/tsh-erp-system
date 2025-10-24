#!/usr/bin/env python3
"""
Seed database with sample data for PRSS
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prss.db import SessionLocal
from prss.models.all_models import (
    User, Product, ReturnRequest, WarrantyPolicy
)
from prss.models.base import UserRole, ReturnStatus
from prss.security.auth import get_password_hash
from datetime import datetime, timedelta


def seed_users(db):
    """Create sample users"""
    print("Creating users...")
    users = [
        User(
            username="admin",
            email="admin@tsh.com",
            full_name="System Administrator",
            role=UserRole.ADMIN,
            hashed_password=get_password_hash("admin123"),
            is_active=True
        ),
        User(
            username="inspector1",
            email="inspector@tsh.com",
            full_name="محمد أحمد - فاحص",
            role=UserRole.INSPECTOR,
            hashed_password=get_password_hash("inspect123"),
            is_active=True
        ),
        User(
            username="technician1",
            email="tech@tsh.com",
            full_name="خالد علي - فني",
            role=UserRole.TECHNICIAN,
            hashed_password=get_password_hash("tech123"),
            is_active=True
        ),
        User(
            username="warranty1",
            email="warranty@tsh.com",
            full_name="سارة محمد - مسؤول ضمان",
            role=UserRole.WARRANTY_OFFICER,
            hashed_password=get_password_hash("warranty123"),
            is_active=True
        ),
        User(
            username="logistics1",
            email="logistics@tsh.com",
            full_name="أحمد حسن - لوجستي",
            role=UserRole.LOGISTICS,
            hashed_password=get_password_hash("logistics123"),
            is_active=True
        ),
    ]

    for user in users:
        existing = db.query(User).filter(User.username == user.username).first()
        if not existing:
            db.add(user)

    db.commit()
    print(f"✓ Created {len(users)} users")


def seed_products(db):
    """Create sample products"""
    print("Creating products...")
    products = [
        Product(
            external_product_id=1001,
            name="لاب توب HP ProBook 450 G10",
            sku="HP-PB450-G10",
            requires_serial=True,
            warranty_months=12
        ),
        Product(
            external_product_id=1002,
            name="طابعة HP LaserJet Pro M404dn",
            sku="HP-LJ-M404",
            requires_serial=True,
            warranty_months=24
        ),
        Product(
            external_product_id=1003,
            name="شاشة Dell 27 inch 4K",
            sku="DELL-MON-27-4K",
            requires_serial=True,
            warranty_months=36
        ),
        Product(
            external_product_id=1004,
            name="ماوس لاسلكي Logitech MX Master 3",
            sku="LOGI-MX3",
            requires_serial=False,
            warranty_months=12
        ),
        Product(
            external_product_id=1005,
            name="كيبورد ميكانيكي Keychron K8",
            sku="KEY-K8-RGB",
            requires_serial=False,
            warranty_months=12
        ),
    ]

    for product in products:
        existing = db.query(Product).filter(
            Product.external_product_id == product.external_product_id
        ).first()
        if not existing:
            db.add(product)

    db.commit()
    print(f"✓ Created {len(products)} products")


def seed_warranty_policies(db):
    """Create sample warranty policies"""
    print("Creating warranty policies...")
    policies = [
        WarrantyPolicy(
            name="Standard 1 Year",
            description="ضمان قياسي لمدة سنة واحدة",
            duration_months=12,
            coverage_details={
                "manufacturing_defects": True,
                "accidental_damage": False,
                "liquid_damage": False,
                "parts": True,
                "labor": True
            },
            terms="يغطي العيوب المصنعية فقط",
            active=True
        ),
        WarrantyPolicy(
            name="Extended 2 Years",
            description="ضمان ممتد لمدة سنتين",
            duration_months=24,
            coverage_details={
                "manufacturing_defects": True,
                "accidental_damage": True,
                "liquid_damage": False,
                "parts": True,
                "labor": True
            },
            terms="يغطي العيوب المصنعية والأضرار العرضية",
            active=True
        ),
        WarrantyPolicy(
            name="Premium 3 Years",
            description="ضمان شامل لمدة ثلاث سنوات",
            duration_months=36,
            coverage_details={
                "manufacturing_defects": True,
                "accidental_damage": True,
                "liquid_damage": True,
                "parts": True,
                "labor": True,
                "onsite_support": True
            },
            terms="تغطية شاملة بما في ذلك الأضرار السائلة",
            active=True
        ),
    ]

    for policy in policies:
        db.add(policy)

    db.commit()
    print(f"✓ Created {len(policies)} warranty policies")


def seed_return_requests(db):
    """Create sample return requests"""
    print("Creating return requests...")

    # Get first product and user
    product = db.query(Product).first()
    user = db.query(User).first()

    if not product or not user:
        print("⚠ No products or users found. Create them first.")
        return

    returns = [
        ReturnRequest(
            customer_id=1001,
            sales_order_id=5001,
            invoice_id=8001,
            product_id=product.id,
            serial_number="SN-TEST-001",
            reason_code="functional_defect",
            reason_description="الجهاز لا يعمل",
            status=ReturnStatus.SUBMITTED,
            priority=1,
            created_by=user.id,
            created_at=datetime.now() - timedelta(days=2)
        ),
        ReturnRequest(
            customer_id=1002,
            sales_order_id=5002,
            product_id=product.id,
            serial_number="SN-TEST-002",
            reason_code="wrong_item",
            reason_description="المنتج خاطئ",
            status=ReturnStatus.RECEIVED,
            priority=0,
            created_by=user.id,
            created_at=datetime.now() - timedelta(days=1)
        ),
        ReturnRequest(
            customer_id=1003,
            sales_order_id=5003,
            product_id=product.id,
            serial_number="SN-TEST-003",
            reason_code="cosmetic_defect",
            reason_description="خدوش في الجهاز",
            status=ReturnStatus.INSPECTING,
            priority=0,
            created_by=user.id,
            created_at=datetime.now() - timedelta(hours=12)
        ),
    ]

    for ret in returns:
        db.add(ret)

    db.commit()
    print(f"✓ Created {len(returns)} return requests")


def main():
    """Main seeding function"""
    print("=" * 50)
    print("PRSS Database Seeding")
    print("=" * 50)

    db = SessionLocal()

    try:
        seed_users(db)
        seed_products(db)
        seed_warranty_policies(db)
        seed_return_requests(db)

        print("\n" + "=" * 50)
        print("✅ Database seeded successfully!")
        print("=" * 50)
        print("\nTest Credentials:")
        print("  Admin:      admin / admin123")
        print("  Inspector:  inspector1 / inspect123")
        print("  Technician: technician1 / tech123")
        print("  Warranty:   warranty1 / warranty123")
        print("  Logistics:  logistics1 / logistics123")
        print("\nYou can now login at: http://localhost:8001/docs")

    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
