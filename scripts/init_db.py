#!/usr/bin/env python3
"""
Initialize TSH ERP Database
===========================
Creates all database tables from SQLAlchemy models.

مبدئ قاعدة بيانات TSH ERP
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.db.database import engine, Base

# Import ALL models so they register with Base.metadata
from app.models import (
    branch, warehouse, role, user, tenant,
    product, customer, customer_address, cart, review, promotion,
    inventory, item, warehouse as warehouse_models,
    sales, invoice, purchase, expense, accounting, money_transfer, cashflow,
    pos, hr, pricing, notification, zoho_sync,
    security, advanced_security, data_scope, permissions,
    after_sales, whatsapp, ai_assistant, migration
)

def init_database():
    """
    Initialize database by creating all tables
    """
    print("=" * 70)
    print("🗄️  TSH ERP Database Initialization")
    print("=" * 70)

    try:
        print("\n📦 Creating all database tables...")

        # Create all tables defined in all imported models
        Base.metadata.create_all(bind=engine)

        print("✅ All tables created successfully!")

        # List all created tables
        print("\n📋 Created tables:")
        for table in Base.metadata.sorted_tables:
            print(f"   - {table.name}")

        print("\n" + "=" * 70)
        print("✅ Database initialization completed successfully!")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\n❌ Error initializing database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
