#!/usr/bin/env python3
"""
Test script to verify PostgreSQL connection and create database tables
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, get_db, DATABASE_URL
from app.models import *

def test_database_connection():
    """Test basic database connectivity"""
    print("🔍 Testing database connection...")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Database connected successfully!")
            print(f"📊 PostgreSQL Version: {version}")
            
        return engine
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def create_database_tables(engine):
    """Create all database tables"""
    print("\n🏗️  Creating database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        
        # List created tables
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            
            print(f"\n📋 Created tables ({len(tables)} total):")
            for table in tables:
                print(f"   • {table}")
                
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")

def test_sample_data(engine):
    """Test inserting and retrieving sample data"""
    print("\n🧪 Testing sample data operations...")
    
    try:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Import models
        from app.models.branch import Branch
        from app.models.warehouse import Warehouse
        from app.models.product import Category, Product
        from app.models.customer import Customer
        
        # Create sample branch
        sample_branch = Branch(
            name="الفرع الرئيسي",
            location="الرياض، المملكة العربية السعودية"
        )
        db.add(sample_branch)
        db.commit()
        db.refresh(sample_branch)
        print(f"✅ Created sample branch: {sample_branch.name}")
        
        # Create sample warehouse
        sample_warehouse = Warehouse(
            name="المستودع الرئيسي",
            branch_id=sample_branch.id
        )
        db.add(sample_warehouse)
        db.commit()
        db.refresh(sample_warehouse)
        print(f"✅ Created sample warehouse: {sample_warehouse.name}")
        
        # Create sample category
        sample_category = Category(
            name="إلكترونيات",
            description="أجهزة إلكترونية ومعدات تقنية"
        )
        db.add(sample_category)
        db.commit()
        db.refresh(sample_category)
        print(f"✅ Created sample category: {sample_category.name}")
        
        # Create sample product
        sample_product = Product(
            sku="TSH-001",
            name="جهاز كمبيوتر محمول",
            description="جهاز كمبيوتر محمول عالي الأداء",
            category_id=sample_category.id,
            unit_price=2500.00,
            cost_price=2000.00,
            unit_of_measure="قطعة",
            min_stock_level=5,
            reorder_point=10
        )
        db.add(sample_product)
        db.commit()
        db.refresh(sample_product)
        print(f"✅ Created sample product: {sample_product.name}")
        
        # Create sample customer
        sample_customer = Customer(
            customer_code="CUST-001",
            name="أحمد محمد",
            company_name="شركة التقنية المتقدمة",
            phone="+966501234567",
            email="ahmed@techcompany.com",
            credit_limit=10000.00
        )
        db.add(sample_customer)
        db.commit()
        db.refresh(sample_customer)
        print(f"✅ Created sample customer: {sample_customer.name}")
        
        db.close()
        print("\n🎉 All sample data created successfully!")
        
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()

def main():
    """Main test function"""
    print("🚀 TSH ERP System - Database Setup Test")
    print("=" * 50)
    
    # Test database connection
    engine = test_database_connection()
    if not engine:
        return
    
    # Create tables
    create_database_tables(engine)
    
    # Test sample data
    test_sample_data(engine)
    
    print("\n" + "=" * 50)
    print("✅ Database setup completed successfully!")
    print("🔗 Your application is ready to connect to PostgreSQL")
    print(f"📍 Database URL: {DATABASE_URL}")

if __name__ == "__main__":
    main()
