#!/usr/bin/env python3
"""
Create demo roles for TSH ERP System
إنشاء أدوار تجريبية لنظام TSH ERP
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.role import Role
from datetime import datetime

def create_demo_roles():
    """Create demo roles"""
    db = next(get_db())
    
    try:
        roles_data = [
            "Admin",
            "Manager", 
            "Employee",
            "Travel Salesperson",
            "Partner Salesman", 
            "Retailerman",
            "Accountant",
            "HR Specialist"
        ]
        
        created_count = 0
        
        for role_name in roles_data:
            # Check if role already exists
            existing_role = db.query(Role).filter(Role.name == role_name).first()
            if existing_role:
                print(f"⚠️  Role '{role_name}' already exists, skipping...")
                continue
            
            try:
                new_role = Role(
                    name=role_name
                )
                
                db.add(new_role)
                db.commit()
                db.refresh(new_role)
                
                print(f"✅ Created role: {role_name}")
                created_count += 1
                
            except Exception as e:
                print(f"❌ Error creating role {role_name}: {str(e)}")
                db.rollback()
                continue
        
        print(f"\n🎉 Successfully created {created_count} demo roles!")
        print(f"📈 Total roles: {db.query(Role).count()}")
        
        # Show all roles
        print("\n📋 Available Roles:")
        for role in db.query(Role).all():
            print(f"  • {role.name}")
        
    except Exception as e:
        print(f"❌ Error creating demo roles: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Creating Demo Roles for TSH ERP System...")
    create_demo_roles()
    print("✨ Demo role creation completed!") 