#!/usr/bin/env python3
"""
TSH ERP System Data Setup Script
This script sets up the initial data for the TSH ERP system including:
- Branches
- Warehouses  
- Roles
- Travel Salespersons as Users
"""

import sys
import os
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal, engine
from app.models.branch import Branch
from app.models.warehouse import Warehouse
from app.models.role import Role
from app.models.user import User

# Create all tables
from app.models import branch, warehouse, role, user
branch.Base.metadata.create_all(bind=engine)
warehouse.Base.metadata.create_all(bind=engine)
role.Base.metadata.create_all(bind=engine)
user.Base.metadata.create_all(bind=engine)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def setup_tsh_data():
    """Set up initial TSH ERP system data"""
    db: Session = SessionLocal()
    
    try:
        print("🚀 Setting up TSH ERP System...")
        
        # 1. Create Roles
        print("\n📋 Creating Roles...")
        roles_data = [
            {"name": "Admin"},
            {"name": "Manager"},
            {"name": "Travel Salesperson"},
            {"name": "Warehouse Staff"},
            {"name": "Accountant"}
        ]
        
        roles = {}
        for role_data in roles_data:
            # Check if role already exists
            existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing_role:
                role = Role(**role_data)
                db.add(role)
                db.commit()
                db.refresh(role)
                roles[role_data["name"]] = role
                print(f"  ✅ Created role: {role_data['name']}")
            else:
                roles[role_data["name"]] = existing_role
                print(f"  ℹ️  Role already exists: {role_data['name']}")
        
        # 2. Create Branches
        print("\n🏢 Creating Branches...")
        branches_data = [
            {
                "name": "Main Wholesale Branch",
                "location": "Main Wholesale Location, Baghdad, Iraq"
            },
            {
                "name": "TSH Dora Branch", 
                "location": "Dora District, Baghdad, Iraq"
            }
        ]
        
        branches = {}
        for branch_data in branches_data:
            # Check if branch already exists
            existing_branch = db.query(Branch).filter(Branch.name == branch_data["name"]).first()
            if not existing_branch:
                branch = Branch(**branch_data)
                db.add(branch)
                db.commit()
                db.refresh(branch)
                branches[branch_data["name"]] = branch
                print(f"  ✅ Created branch: {branch_data['name']}")
            else:
                branches[branch_data["name"]] = existing_branch
                print(f"  ℹ️  Branch already exists: {branch_data['name']}")
        
        # 3. Create Warehouses
        print("\n🏭 Creating Warehouses...")
        warehouses_data = [
            {
                "name": "Main Wholesale Warehouse",
                "branch_id": branches["Main Wholesale Branch"].id
            },
            {
                "name": "TSH Dora Storage",
                "branch_id": branches["TSH Dora Branch"].id
            }
        ]
        
        warehouses = {}
        for warehouse_data in warehouses_data:
            # Check if warehouse already exists
            existing_warehouse = db.query(Warehouse).filter(Warehouse.name == warehouse_data["name"]).first()
            if not existing_warehouse:
                warehouse = Warehouse(**warehouse_data)
                db.add(warehouse)
                db.commit()
                db.refresh(warehouse)
                warehouses[warehouse_data["name"]] = warehouse
                print(f"  ✅ Created warehouse: {warehouse_data['name']}")
            else:
                warehouses[warehouse_data["name"]] = existing_warehouse
                print(f"  ℹ️  Warehouse already exists: {warehouse_data['name']}")
        
        # 4. Create Travel Salespersons
        print("\n👥 Creating Travel Salespersons...")
        salespersons_data = [
            {
                "name": "Ahmed Kareem",
                "email": "ahmed.kareem@tsh.com",
                "password": "ahmed2025!",
                "role_id": roles["Travel Salesperson"].id,
                "branch_id": branches["Main Wholesale Branch"].id
            },
            {
                "name": "Ayad Fadel", 
                "email": "ayad.fadel@tsh.com",
                "password": "ayad2025!",
                "role_id": roles["Travel Salesperson"].id,
                "branch_id": branches["Main Wholesale Branch"].id
            },
            {
                "name": "Haider Adnan",
                "email": "haider.adnan@tsh.com", 
                "password": "haider2025!",
                "role_id": roles["Travel Salesperson"].id,
                "branch_id": branches["TSH Dora Branch"].id
            },
            {
                "name": "Ayoob Myser",
                "email": "ayoob.myser@tsh.com",
                "password": "ayoob2025!",
                "role_id": roles["Travel Salesperson"].id,
                "branch_id": branches["TSH Dora Branch"].id
            },
            {
                "name": "Hussien Hgran",
                "email": "hussien.hgran@tsh.com",
                "password": "hussien2025!",
                "role_id": roles["Travel Salesperson"].id,
                "branch_id": branches["Main Wholesale Branch"].id
            }
        ]
        
        users = {}
        for user_data in salespersons_data:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing_user:
                # Hash the password
                user_data_copy = user_data.copy()
                user_data_copy["password"] = hash_password(user_data["password"])
                
                user = User(**user_data_copy)
                db.add(user)
                db.commit()
                db.refresh(user)
                users[user_data["name"]] = user
                print(f"  ✅ Created user: {user_data['name']} - {user_data['email']}")
                print(f"      Password: {user_data['password']}")
            else:
                users[user_data["name"]] = existing_user
                print(f"  ℹ️  User already exists: {user_data['name']}")
        
        # 5. Create Admin User
        print("\n👑 Creating Admin User...")
        admin_data = {
            "name": "TSH Admin",
            "email": "admin@tsh.com",
            "password": "admin2025!",
            "role_id": roles["Admin"].id,
            "branch_id": branches["Main Wholesale Branch"].id
        }
        
        existing_admin = db.query(User).filter(User.email == admin_data["email"]).first()
        if not existing_admin:
            admin_data["password"] = hash_password(admin_data["password"])
            admin = User(**admin_data)
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"  ✅ Created admin: {admin.name} - {admin.email}")
            print(f"      Password: admin2025!")
        else:
            print(f"  ℹ️  Admin user already exists: {existing_admin.name}")
        
        print("\n🎉 TSH ERP System setup completed successfully!")
        print("\n📊 Summary:")
        print(f"  • Branches: {len(branches)}")
        print(f"  • Warehouses: {len(warehouses)}")
        print(f"  • Roles: {len(roles)}")
        print(f"  • Travel Salespersons: {len(users)}")
        print("  • Admin User: 1")
        
        print("\n🔐 Login Credentials:")
        print("Admin:")
        print("  Email: admin@tsh.com")
        print("  Password: admin2025!")
        print("\nTravel Salespersons:")
        for user_data in salespersons_data:
            print(f"  {user_data['name']}: {user_data['email']} / {user_data['password']}")
        
    except Exception as e:
        print(f"❌ Error setting up TSH data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    setup_tsh_data()
