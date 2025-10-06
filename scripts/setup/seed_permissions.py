#!/usr/bin/env python3
"""
TSH ERP System - Comprehensive Permission Seeding Script
Creates all necessary permissions, roles, and grants admin full access
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.db.database import DATABASE_URL, SessionLocal
from app.models.permissions import Permission, RolePermission, PermissionType, ResourceType
from app.models.role import Role
from app.models.user import User
from datetime import datetime

def create_permissions():
    """Create comprehensive permission system for TSH ERP"""
    print("🔐 Creating comprehensive permission system...")
    
    db = SessionLocal()
    try:
        # Define all permissions for TSH ERP System
        permissions_data = [
            # Admin permissions
            ("admin", "Full system administration access", ResourceType.SETTINGS, PermissionType.APPROVE),
            ("*", "Wildcard - all permissions", ResourceType.SETTINGS, PermissionType.APPROVE),
            
            # Dashboard permissions
            ("dashboard.view", "View dashboard", ResourceType.REPORTS, PermissionType.READ),
            ("dashboard.manage", "Manage dashboard settings", ResourceType.SETTINGS, PermissionType.UPDATE),
            
            # User management permissions
            ("users.view", "View users", ResourceType.USER, PermissionType.READ),
            ("users.create", "Create new users", ResourceType.USER, PermissionType.CREATE),
            ("users.update", "Update user information", ResourceType.USER, PermissionType.UPDATE),
            ("users.delete", "Delete users", ResourceType.USER, PermissionType.DELETE),
            ("users.manage", "Full user management", ResourceType.USER, PermissionType.APPROVE),
            
            # HR permissions
            ("hr.view", "View HR modules", ResourceType.USER, PermissionType.READ),
            ("hr.employees.view", "View employees", ResourceType.USER, PermissionType.READ),
            ("hr.employees.create", "Create employees", ResourceType.USER, PermissionType.CREATE),
            ("hr.employees.update", "Update employees", ResourceType.USER, PermissionType.UPDATE),
            ("hr.employees.delete", "Delete employees", ResourceType.USER, PermissionType.DELETE),
            ("hr.payroll.view", "View payroll", ResourceType.FINANCIAL, PermissionType.READ),
            ("hr.payroll.manage", "Manage payroll", ResourceType.FINANCIAL, PermissionType.UPDATE),
            ("hr.attendance.view", "View attendance", ResourceType.USER, PermissionType.READ),
            ("hr.attendance.manage", "Manage attendance", ResourceType.USER, PermissionType.UPDATE),
            ("hr.performance.view", "View performance", ResourceType.REPORTS, PermissionType.READ),
            ("hr.performance.manage", "Manage performance", ResourceType.REPORTS, PermissionType.UPDATE),
            
            # Branch and Organization permissions
            ("branches.view", "View branches", ResourceType.BRANCH, PermissionType.READ),
            ("branches.create", "Create branches", ResourceType.BRANCH, PermissionType.CREATE),
            ("branches.update", "Update branches", ResourceType.BRANCH, PermissionType.UPDATE),
            ("branches.delete", "Delete branches", ResourceType.BRANCH, PermissionType.DELETE),
            ("warehouses.view", "View warehouses", ResourceType.INVENTORY, PermissionType.READ),
            ("warehouses.create", "Create warehouses", ResourceType.INVENTORY, PermissionType.CREATE),
            ("warehouses.update", "Update warehouses", ResourceType.INVENTORY, PermissionType.UPDATE),
            ("warehouses.delete", "Delete warehouses", ResourceType.INVENTORY, PermissionType.DELETE),
            
            # Inventory permissions
            ("inventory.view", "View inventory", ResourceType.INVENTORY, PermissionType.READ),
            ("inventory.create", "Create inventory items", ResourceType.INVENTORY, PermissionType.CREATE),
            ("inventory.update", "Update inventory", ResourceType.INVENTORY, PermissionType.UPDATE),
            ("inventory.delete", "Delete inventory items", ResourceType.INVENTORY, PermissionType.DELETE),
            ("inventory.adjust", "Adjust inventory quantities", ResourceType.INVENTORY, PermissionType.UPDATE),
            ("inventory.transfer", "Transfer inventory", ResourceType.INVENTORY, PermissionType.UPDATE),
            ("items.view", "View items", ResourceType.PRODUCT, PermissionType.READ),
            ("items.create", "Create items", ResourceType.PRODUCT, PermissionType.CREATE),
            ("items.update", "Update items", ResourceType.PRODUCT, PermissionType.UPDATE),
            ("items.delete", "Delete items", ResourceType.PRODUCT, PermissionType.DELETE),
            ("products.view", "View products", ResourceType.PRODUCT, PermissionType.READ),
            ("products.create", "Create products", ResourceType.PRODUCT, PermissionType.CREATE),
            ("products.update", "Update products", ResourceType.PRODUCT, PermissionType.UPDATE),
            ("products.delete", "Delete products", ResourceType.PRODUCT, PermissionType.DELETE),
            
            # Sales permissions
            ("sales.view", "View sales", ResourceType.SALES, PermissionType.READ),
            ("sales.create", "Create sales orders", ResourceType.SALES, PermissionType.CREATE),
            ("sales.update", "Update sales orders", ResourceType.SALES, PermissionType.UPDATE),
            ("sales.delete", "Delete sales orders", ResourceType.SALES, PermissionType.DELETE),
            ("sales.approve", "Approve sales orders", ResourceType.SALES, PermissionType.APPROVE),
            ("customers.view", "View customers", ResourceType.CUSTOMER, PermissionType.READ),
            ("customers.create", "Create customers", ResourceType.CUSTOMER, PermissionType.CREATE),
            ("customers.update", "Update customers", ResourceType.CUSTOMER, PermissionType.UPDATE),
            ("customers.delete", "Delete customers", ResourceType.CUSTOMER, PermissionType.DELETE),
            
            # Purchase permissions
            ("purchase.view", "View purchases", ResourceType.SALES, PermissionType.READ),
            ("purchase.create", "Create purchase orders", ResourceType.SALES, PermissionType.CREATE),
            ("purchase.update", "Update purchase orders", ResourceType.SALES, PermissionType.UPDATE),
            ("purchase.delete", "Delete purchase orders", ResourceType.SALES, PermissionType.DELETE),
            ("purchase.approve", "Approve purchase orders", ResourceType.SALES, PermissionType.APPROVE),
            ("vendors.view", "View vendors", ResourceType.CUSTOMER, PermissionType.READ),
            ("vendors.create", "Create vendors", ResourceType.CUSTOMER, PermissionType.CREATE),
            ("vendors.update", "Update vendors", ResourceType.CUSTOMER, PermissionType.UPDATE),
            ("vendors.delete", "Delete vendors", ResourceType.CUSTOMER, PermissionType.DELETE),
            
            # Financial permissions
            ("financial.view", "View financial data", ResourceType.FINANCIAL, PermissionType.READ),
            ("financial.create", "Create financial records", ResourceType.FINANCIAL, PermissionType.CREATE),
            ("financial.update", "Update financial records", ResourceType.FINANCIAL, PermissionType.UPDATE),
            ("financial.delete", "Delete financial records", ResourceType.FINANCIAL, PermissionType.DELETE),
            ("financial.approve", "Approve financial transactions", ResourceType.FINANCIAL, PermissionType.APPROVE),
            ("finance.cashboxes.view", "View cash boxes", ResourceType.FINANCIAL, PermissionType.READ),
            ("finance.cashboxes.create", "Create cash boxes", ResourceType.FINANCIAL, PermissionType.CREATE),
            ("finance.cashboxes.deposit", "Deposit to cash boxes", ResourceType.FINANCIAL, PermissionType.UPDATE),
            ("finance.cashboxes.withdraw", "Withdraw from cash boxes", ResourceType.FINANCIAL, PermissionType.UPDATE),
            ("finance.cashboxes.reconcile", "Reconcile cash boxes", ResourceType.FINANCIAL, PermissionType.APPROVE),
            ("finance.transfers.view", "View money transfers", ResourceType.FINANCIAL, PermissionType.READ),
            ("finance.transfers.create", "Create money transfers", ResourceType.FINANCIAL, PermissionType.CREATE),
            ("finance.transfers.approve", "Approve money transfers", ResourceType.FINANCIAL, PermissionType.APPROVE),
            ("finance.transfers.settle", "Settle money transfers", ResourceType.FINANCIAL, PermissionType.UPDATE),
            
            # Accounting permissions
            ("accounting.view", "View accounting", ResourceType.FINANCIAL, PermissionType.READ),
            ("accounting.create", "Create accounting records", ResourceType.FINANCIAL, PermissionType.CREATE),
            ("accounting.update", "Update accounting records", ResourceType.FINANCIAL, PermissionType.UPDATE),
            ("accounting.delete", "Delete accounting records", ResourceType.FINANCIAL, PermissionType.DELETE),
            ("accounting.journal.view", "View journal entries", ResourceType.FINANCIAL, PermissionType.READ),
            ("accounting.journal.post", "Post journal entries", ResourceType.FINANCIAL, PermissionType.CREATE),
            ("accounting.journal.approve", "Approve journal entries", ResourceType.FINANCIAL, PermissionType.APPROVE),
            
            # POS permissions
            ("pos.view", "View POS data", ResourceType.SALES, PermissionType.READ),
            ("pos.operate", "Operate POS terminal", ResourceType.SALES, PermissionType.CREATE),
            ("pos.manage", "Manage POS settings", ResourceType.SALES, PermissionType.UPDATE),
            ("pos.reports", "View POS reports", ResourceType.REPORTS, PermissionType.READ),
            
            # Cash Flow permissions
            ("cashflow.view", "View cash flow", ResourceType.FINANCIAL, PermissionType.READ),
            ("cashflow.manage", "Manage cash flow", ResourceType.FINANCIAL, PermissionType.UPDATE),
            ("cashflow.reports", "View cash flow reports", ResourceType.REPORTS, PermissionType.READ),
            
            # Expense permissions
            ("expenses.view", "View expenses", ResourceType.FINANCIAL, PermissionType.READ),
            ("expenses.create", "Create expenses", ResourceType.FINANCIAL, PermissionType.CREATE),
            ("expenses.update", "Update expenses", ResourceType.FINANCIAL, PermissionType.UPDATE),
            ("expenses.delete", "Delete expenses", ResourceType.FINANCIAL, PermissionType.DELETE),
            ("expenses.approve", "Approve expenses", ResourceType.FINANCIAL, PermissionType.APPROVE),
            
            # Reports permissions
            ("reports.view", "View reports", ResourceType.REPORTS, PermissionType.READ),
            ("reports.create", "Create custom reports", ResourceType.REPORTS, PermissionType.CREATE),
            ("reports.export", "Export reports", ResourceType.REPORTS, PermissionType.EXPORT),
            ("reports.financial", "View financial reports", ResourceType.REPORTS, PermissionType.READ),
            ("reports.inventory", "View inventory reports", ResourceType.REPORTS, PermissionType.READ),
            ("reports.sales", "View sales reports", ResourceType.REPORTS, PermissionType.READ),
            
            # Settings permissions
            ("settings.view", "View settings", ResourceType.SETTINGS, PermissionType.READ),
            ("settings.update", "Update settings", ResourceType.SETTINGS, PermissionType.UPDATE),
            ("settings.system", "Manage system settings", ResourceType.SETTINGS, PermissionType.APPROVE),
            
            # Migration permissions
            ("migration.view", "View migration tools", ResourceType.SETTINGS, PermissionType.READ),
            ("migration.execute", "Execute migrations", ResourceType.SETTINGS, PermissionType.UPDATE),
            ("migration.import", "Import data", ResourceType.SETTINGS, PermissionType.IMPORT),
            ("migration.export", "Export data", ResourceType.SETTINGS, PermissionType.EXPORT),
            
            # Security permissions
            ("security.view", "View security settings", ResourceType.SETTINGS, PermissionType.READ),
            ("security.manage", "Manage security", ResourceType.SETTINGS, PermissionType.UPDATE),
            ("permissions.view", "View permissions", ResourceType.SETTINGS, PermissionType.READ),
            ("permissions.grant", "Grant permissions", ResourceType.SETTINGS, PermissionType.APPROVE),
            ("permissions.revoke", "Revoke permissions", ResourceType.SETTINGS, PermissionType.APPROVE),
            ("roles.view", "View roles", ResourceType.SETTINGS, PermissionType.READ),
            ("roles.create", "Create roles", ResourceType.SETTINGS, PermissionType.CREATE),
            ("roles.update", "Update roles", ResourceType.SETTINGS, PermissionType.UPDATE),
            ("roles.delete", "Delete roles", ResourceType.SETTINGS, PermissionType.DELETE),
            
            # Audit permissions
            ("audit.view", "View audit logs", ResourceType.SETTINGS, PermissionType.READ),
            ("audit.export", "Export audit logs", ResourceType.SETTINGS, PermissionType.EXPORT),
        ]
        
        # Create permissions
        created_count = 0
        for name, description, resource_type, permission_type in permissions_data:
            existing = db.query(Permission).filter(Permission.name == name).first()
            if not existing:
                permission = Permission(
                    name=name,
                    description=description,
                    resource_type=resource_type,
                    permission_type=permission_type,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.add(permission)
                created_count += 1
        
        db.commit()
        print(f"✅ Created {created_count} new permissions")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating permissions: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def setup_admin_role():
    """Grant admin role all permissions"""
    print("👑 Setting up admin role with full permissions...")
    
    db = SessionLocal()
    try:
        # Get or create admin role
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if not admin_role:
            admin_role = Role(
                name="Admin",
                description="System Administrator with full access",
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(admin_role)
            db.commit()
            print("✅ Created Admin role")
        
        # Get all permissions
        all_permissions = db.query(Permission).all()
        
        # Grant all permissions to admin role
        granted_count = 0
        for permission in all_permissions:
            existing = db.query(RolePermission).filter(
                RolePermission.role_id == admin_role.id,
                RolePermission.permission_id == permission.id
            ).first()
            
            if not existing:
                role_permission = RolePermission(
                    role_id=admin_role.id,
                    permission_id=permission.id,
                    granted_by=1,  # System
                    granted_at=datetime.utcnow()
                )
                db.add(role_permission)
                granted_count += 1
        
        db.commit()
        print(f"✅ Granted {granted_count} permissions to Admin role")
        
        return admin_role.id
        
    except Exception as e:
        print(f"❌ Error setting up admin role: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def update_admin_users():
    """Update admin users to have the admin role"""
    print("👤 Updating admin users...")
    
    db = SessionLocal()
    try:
        # Get admin role
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if not admin_role:
            print("❌ Admin role not found")
            return False
        
        # Update users with admin role or admin email
        admin_users = db.query(User).filter(
            (User.email.like("%admin%")) |
            (User.email == "admin@tsh-erp.com") |
            (User.name.like("%admin%"))
        ).all()
        
        updated_count = 0
        for user in admin_users:
            if user.role_id != admin_role.id:
                user.role_id = admin_role.id
                updated_count += 1
        
        db.commit()
        print(f"✅ Updated {updated_count} admin users")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating admin users: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def create_default_roles():
    """Create default roles with appropriate permissions"""
    print("🎭 Creating default roles...")
    
    db = SessionLocal()
    try:
        # Define roles and their permission patterns
        roles_data = [
            ("Manager", "Branch/Department Manager", [
                "dashboard.view", "reports.view", "inventory.view", "sales.view", 
                "customers.view", "users.view", "branches.view", "warehouses.view"
            ]),
            ("Supervisor", "Department Supervisor", [
                "dashboard.view", "inventory.view", "sales.view", "customers.view"
            ]),
            ("Cashier", "POS Operator", [
                "pos.view", "pos.operate", "sales.create", "customers.view"
            ]),
            ("Accountant", "Financial Officer", [
                "accounting.view", "financial.view", "reports.financial", 
                "expenses.view", "cashflow.view"
            ]),
            ("Inventory Manager", "Inventory Specialist", [
                "inventory.*", "items.*", "products.*", "warehouses.view", 
                "reports.inventory"
            ]),
            ("Sales Manager", "Sales Department Head", [
                "sales.*", "customers.*", "pos.view", "reports.sales"
            ]),
            ("HR Manager", "Human Resources Manager", [
                "hr.*", "users.view", "users.create", "users.update"
            ]),
            ("Finance Manager", "Financial Manager", [
                "financial.*", "accounting.*", "cashflow.*", "expenses.*", 
                "reports.financial"
            ]),
            ("Auditor", "System Auditor", [
                "*.view", "reports.*", "audit.view", "audit.export"
            ]),
            ("User", "Standard User", [
                "dashboard.view"
            ])
        ]
        
        created_count = 0
        for role_name, description, permission_patterns in roles_data:
            existing_role = db.query(Role).filter(Role.name == role_name).first()
            if not existing_role:
                new_role = Role(
                    name=role_name,
                    description=description,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.add(new_role)
                db.flush()  # Get the ID
                
                # Grant permissions based on patterns
                all_permissions = db.query(Permission).all()
                for permission in all_permissions:
                    should_grant = False
                    for pattern in permission_patterns:
                        if pattern.endswith(".*"):
                            # Wildcard pattern like "inventory.*"
                            prefix = pattern[:-2]
                            if permission.name.startswith(prefix + "."):
                                should_grant = True
                                break
                        elif pattern == "*.view":
                            # View-only pattern
                            if permission.name.endswith(".view"):
                                should_grant = True
                                break
                        elif pattern == "*":
                            # All permissions
                            should_grant = True
                            break
                        elif pattern == permission.name:
                            # Exact match
                            should_grant = True
                            break
                    
                    if should_grant:
                        role_permission = RolePermission(
                            role_id=new_role.id,
                            permission_id=permission.id,
                            granted_by=1,  # System
                            granted_at=datetime.utcnow()
                        )
                        db.add(role_permission)
                
                created_count += 1
        
        db.commit()
        print(f"✅ Created {created_count} default roles")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating default roles: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Main execution function"""
    print("🚀 TSH ERP System - Permission System Setup")
    print("=" * 50)
    
    # Step 1: Create all permissions
    if not create_permissions():
        print("❌ Failed to create permissions")
        return False
    
    # Step 2: Setup admin role
    admin_role_id = setup_admin_role()
    if not admin_role_id:
        print("❌ Failed to setup admin role")
        return False
    
    # Step 3: Update admin users
    if not update_admin_users():
        print("❌ Failed to update admin users")
        return False
    
    # Step 4: Create default roles
    if not create_default_roles():
        print("❌ Failed to create default roles")
        return False
    
    print("\n🎉 Permission system setup completed successfully!")
    print("\n📋 Summary:")
    print("- ✅ All permissions created")
    print("- ✅ Admin role configured with full access")
    print("- ✅ Admin users updated")
    print("- ✅ Default roles created")
    print("\n🔐 Admin users now have full system access!")
    
    return True

if __name__ == "__main__":
    main()
