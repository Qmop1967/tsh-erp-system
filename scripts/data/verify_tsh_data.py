#!/usr/bin/env python3
"""
TSH ERP System Data Verification Script
This script verifies and displays all the created data in the TSH ERP system
"""

import sys
import os
from sqlalchemy.orm import Session

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.branch import Branch
from app.models.warehouse import Warehouse
from app.models.role import Role
from app.models.user import User

def verify_tsh_data():
    """Verify and display all TSH ERP system data"""
    db: Session = SessionLocal()
    
    try:
        print("📋 TSH ERP System Data Verification")
        print("=" * 50)
        
        # 1. Verify Branches
        print("\n🏢 BRANCHES:")
        branches = db.query(Branch).all()
        for branch in branches:
            print(f"  ID: {branch.id} | Name: {branch.name}")
            print(f"       Location: {branch.location}")
            
            # Show warehouses for this branch
            warehouses_count = len(branch.warehouses)
            users_count = len(branch.users)
            print(f"       Warehouses: {warehouses_count} | Users: {users_count}")
            print()
        
        # 2. Verify Warehouses
        print("\n🏭 WAREHOUSES:")
        warehouses = db.query(Warehouse).all()
        for warehouse in warehouses:
            branch_name = warehouse.branch.name if warehouse.branch else "No Branch"
            print(f"  ID: {warehouse.id} | Name: {warehouse.name}")
            print(f"       Branch: {branch_name}")
            print()
        
        # 3. Verify Roles
        print("\n📋 ROLES:")
        roles = db.query(Role).all()
        for role in roles:
            users_count = len(role.users)
            print(f"  ID: {role.id} | Name: {role.name} | Users: {users_count}")
        
        # 4. Verify Users
        print("\n👥 USERS:")
        users = db.query(User).all()
        for user in users:
            role_name = user.role.name if user.role else "No Role"
            branch_name = user.branch.name if user.branch else "No Branch"
            print(f"  ID: {user.id} | Name: {user.name}")
            print(f"       Email: {user.email}")
            print(f"       Role: {role_name}")
            print(f"       Branch: {branch_name}")
            print()
        
        # 5. Summary Statistics
        print("\n📊 SUMMARY STATISTICS:")
        print(f"  Total Branches: {len(branches)}")
        print(f"  Total Warehouses: {len(warehouses)}")
        print(f"  Total Roles: {len(roles)}")
        print(f"  Total Users: {len(users)}")
        
        # 6. Travel Salespersons by Branch
        print("\n🚗 TRAVEL SALESPERSONS BY BRANCH:")
        travel_salesperson_role = db.query(Role).filter(Role.name == "Travel Salesperson").first()
        if travel_salesperson_role:
            salespersons = db.query(User).filter(User.role_id == travel_salesperson_role.id).all()
            
            # Group by branch
            branch_salespersons = {}
            for sp in salespersons:
                branch_name = sp.branch.name if sp.branch else "No Branch"
                if branch_name not in branch_salespersons:
                    branch_salespersons[branch_name] = []
                branch_salespersons[branch_name].append(sp)
            
            for branch_name, sps in branch_salespersons.items():
                print(f"\n  {branch_name}:")
                for sp in sps:
                    print(f"    • {sp.name} ({sp.email})")
        
        print("\n✅ Verification completed successfully!")
        
    except Exception as e:
        print(f"❌ Error verifying TSH data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    verify_tsh_data()
