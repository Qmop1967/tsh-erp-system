#!/usr/bin/env python3
"""
TSH ERP System - Create Salesperson Role and User
Creates the Salesperson role with appropriate permissions and a test salesperson user
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.branch import Branch
from app.models.permissions import Permission, RolePermission
from app.services.auth_service import AuthService
from datetime import datetime

def create_salesperson_role(db):
    """Create or get Salesperson role with appropriate permissions"""
    print("🎭 Creating/updating Salesperson role...")
    
    try:
        # Get or create Salesperson role
        salesperson_role = db.query(Role).filter(Role.name == "Salesperson").first()
        
        if not salesperson_role:
            salesperson_role = Role(
                name="Salesperson",
                description="Field sales representative with customer and sales management access",
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(salesperson_role)
            db.flush()
            print("✅ Created Salesperson role")
        else:
            print("- Salesperson role already exists")
        
        # Define salesperson permissions
        salesperson_permissions = [
            # Dashboard
            "dashboard.view",
            
            # Sales
            "sales.view",
            "sales.create",
            "sales.update",
            
            # Customers
            "customers.view",
            "customers.create",
            "customers.update",
            
            # Inventory (read-only)
            "inventory.view",
            "items.view",
            "products.view",
            
            # Financial (limited)
            "finance.transfers.view",
            "finance.transfers.create",
            "finance.cashboxes.view",
            "finance.cashboxes.deposit",
            
            # POS
            "pos.view",
            "pos.operate",
            
            # Reports (limited)
            "reports.view",
            "reports.sales",
        ]
        
        # Grant permissions to role
        granted_count = 0
        for perm_name in salesperson_permissions:
            # Check if permission exists
            permission = db.query(Permission).filter(Permission.name == perm_name).first()
            
            if not permission:
                print(f"⚠️  Permission '{perm_name}' not found - skipping")
                continue
            
            # Check if already granted
            existing = db.query(RolePermission).filter(
                RolePermission.role_id == salesperson_role.id,
                RolePermission.permission_id == permission.id
            ).first()
            
            if not existing:
                role_perm = RolePermission(
                    role_id=salesperson_role.id,
                    permission_id=permission.id,
                    granted_by=1,  # System
                    granted_at=datetime.utcnow()
                )
                db.add(role_perm)
                granted_count += 1
        
        db.commit()
        print(f"✅ Granted {granted_count} new permissions to Salesperson role")
        
        return salesperson_role
        
    except Exception as e:
        print(f"❌ Error creating Salesperson role: {e}")
        db.rollback()
        return None

def create_salesperson_user(db, salesperson_role, branch):
    """Create test salesperson user"""
    print("\n👤 Creating salesperson user...")
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == "frati@tsh.sale").first()
        
        if existing_user:
            print("- User already exists: frati@tsh.sale")
            # Update role if needed
            if existing_user.role_id != salesperson_role.id:
                existing_user.role_id = salesperson_role.id
                existing_user.is_salesperson = True
                db.commit()
                print("✅ Updated existing user's role to Salesperson")
            return existing_user
        
        # Create new salesperson user
        salesperson_user = User(
            name="Frati Al-Frati",
            email="frati@tsh.sale",
            password=AuthService.get_password_hash("frati123"),
            role_id=salesperson_role.id,
            branch_id=branch.id,
            employee_code="SAL002",
            phone="+964-770-123-4567",
            is_salesperson=True,
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow()
        )
        
        db.add(salesperson_user)
        db.commit()
        
        print("✅ Created salesperson user:")
        print(f"   Email: frati@tsh.sale")
        print(f"   Password: frati123")
        print(f"   Name: Frati Al-Frati")
        print(f"   Employee Code: SAL002")
        
        return salesperson_user
        
    except Exception as e:
        print(f"❌ Error creating salesperson user: {e}")
        db.rollback()
        return None

def verify_setup(db, user):
    """Verify the salesperson setup"""
    print("\n🔍 Verifying setup...")
    
    try:
        # Reload user with relationships
        from sqlalchemy.orm import joinedload
        user = db.query(User).options(
            joinedload(User.role).joinedload(Role.role_permissions)
        ).filter(User.id == user.id).first()
        
        if not user:
            print("❌ User not found")
            return False
        
        print(f"✅ User: {user.name} ({user.email})")
        print(f"✅ Role: {user.role.name if user.role else 'None'}")
        print(f"✅ Active: {user.is_active}")
        print(f"✅ Salesperson: {user.is_salesperson}")
        print(f"✅ Branch: {user.branch.name if user.branch else 'None'}")
        
        # Count permissions
        if user.role:
            perm_count = len(user.role.role_permissions)
            print(f"✅ Permissions: {perm_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying setup: {e}")
        return False

def main():
    """Main execution function"""
    print("🚀 TSH ERP System - Salesperson Setup")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Step 1: Get main branch
        print("\n1. Finding main branch...")
        main_branch = db.query(Branch).filter(Branch.branch_code == "MAIN").first()
        
        if not main_branch:
            # Try to get any active branch
            main_branch = db.query(Branch).filter(Branch.is_active == True).first()
        
        if not main_branch:
            print("❌ No active branch found. Please run init_user_system.py first.")
            return False
        
        print(f"✅ Using branch: {main_branch.name} ({main_branch.branch_code})")
        
        # Step 2: Create/update Salesperson role
        print("\n2. Setting up Salesperson role...")
        salesperson_role = create_salesperson_role(db)
        
        if not salesperson_role:
            print("❌ Failed to setup Salesperson role")
            return False
        
        # Step 3: Create salesperson user
        print("\n3. Creating salesperson user...")
        salesperson_user = create_salesperson_user(db, salesperson_role, main_branch)
        
        if not salesperson_user:
            print("❌ Failed to create salesperson user")
            return False
        
        # Step 4: Verify setup
        print("\n4. Verifying setup...")
        if not verify_setup(db, salesperson_user):
            print("❌ Setup verification failed")
            return False
        
        # Summary
        print("\n" + "=" * 60)
        print("🎉 Salesperson setup completed successfully!")
        print("\n📱 Mobile App Login Credentials:")
        print("   Email: frati@tsh.sale")
        print("   Password: frati123")
        print("\n🌐 Web App Login:")
        print("   URL: http://localhost:5173")
        print("   Email: frati@tsh.sale")
        print("   Password: frati123")
        print("\n📊 User Details:")
        print(f"   Name: {salesperson_user.name}")
        print(f"   Role: {salesperson_user.role.name}")
        print(f"   Branch: {main_branch.name}")
        print(f"   Employee Code: {salesperson_user.employee_code}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error in main execution: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
