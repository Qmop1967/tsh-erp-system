"""
Initialize Admin User and Permissions
تهيئة مستخدم المدير الأعلى والصلاحيات
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.branch import Branch
from app.models.tenant import Tenant, TenantSettings
from app.models.permissions import Permission, ResourceType, PermissionType, RolePermission
from app.services.auth_service import AuthService
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_default_tenant(db: Session) -> Tenant:
    """Create default tenant for the system"""
    tenant = db.query(Tenant).filter(Tenant.code == "TSH").first()
    if not tenant:
        tenant = Tenant(
            name="TSH Trading & Services",
            code="TSH",
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        logger.info(f"✅ Created default tenant: {tenant.name}")
        
        # Create tenant settings
        settings_data = [
            {"tenant_id": tenant.id, "category": "general", "key": "default_currency", "value": "IQD"},
            {"tenant_id": tenant.id, "category": "general", "key": "default_language", "value": "ar"},
            {"tenant_id": tenant.id, "category": "general", "key": "timezone", "value": "Asia/Baghdad"}
        ]
        for setting_data in settings_data:
            setting = TenantSettings(**setting_data)
            db.add(setting)
        db.commit()
        logger.info("✅ Created tenant settings")
    
    return tenant


def create_default_branch(db: Session) -> Branch:
    """Create default branch for the system"""
    branch = db.query(Branch).filter(Branch.branch_code == "HQ001").first()
    if not branch:
        branch = Branch(
            branch_code="HQ001",
            name="Headquarters - Main Office",
            name_en="Headquarters - Main Office",
            name_ar="المقر الرئيسي - المكتب الرئيسي",
            location="Baghdad, Iraq",
            address_en="Baghdad, Iraq",
            address_ar="بغداد، العراق",
            branch_type="MAIN",
            phone="+964-XXX-XXXX",
            email="hq@tsh.sale",
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(branch)
        db.commit()
        db.refresh(branch)
        logger.info(f"✅ Created default branch: {branch.name}")
    
    return branch


def create_admin_role(db: Session) -> Role:
    """Create Admin role with full permissions"""
    role = db.query(Role).filter(Role.name == "Admin").first()
    if not role:
        role = Role(
            name="Admin",
            description="System Administrator with full access",
            created_at=datetime.utcnow()
        )
        db.add(role)
        db.commit()
        db.refresh(role)
        logger.info(f"✅ Created Admin role")
    
    return role


def create_additional_roles(db: Session):
    """Create additional roles for different user types"""
    roles_data = [
        {
            "name": "Manager",
            "description": "Branch Manager with management access"
        },
        {
            "name": "Salesperson",
            "description": "Sales representative with mobile access"
        },
        {
            "name": "Cashier",
            "description": "POS cashier with limited access"
        },
        {
            "name": "Inventory",
            "description": "Inventory manager with warehouse access"
        },
        {
            "name": "Accountant",
            "description": "Accounting staff with financial access"
        },
        {
            "name": "HR",
            "description": "Human Resources staff"
        },
        {
            "name": "Viewer",
            "description": "Read-only access for reporting"
        }
    ]
    
    for role_data in roles_data:
        existing = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing:
            role = Role(**role_data, created_at=datetime.utcnow())
            db.add(role)
            logger.info(f"✅ Created role: {role_data['name']}")
    
    db.commit()


def create_permissions(db: Session):
    """Create all system permissions"""
    
    # Define all resources and their permissions using valid enum values
    resources = [
        # User Management
        {"name": "user_create", "resource": "USER", "type": "CREATE", "description": "Create new users"},
        {"name": "user_read", "resource": "USER", "type": "READ", "description": "View users"},
        {"name": "user_update", "resource": "USER", "type": "UPDATE", "description": "Update user details"},
        {"name": "user_delete", "resource": "USER", "type": "DELETE", "description": "Delete users"},
        {"name": "user_approve", "resource": "USER", "type": "APPROVE", "description": "Approve user actions"},
        
        # Branch Management
        {"name": "branch_create", "resource": "BRANCH", "type": "CREATE", "description": "Create branches"},
        {"name": "branch_read", "resource": "BRANCH", "type": "READ", "description": "View branches"},
        {"name": "branch_update", "resource": "BRANCH", "type": "UPDATE", "description": "Update branches"},
        {"name": "branch_delete", "resource": "BRANCH", "type": "DELETE", "description": "Delete branches"},
        
        # Product Management
        {"name": "product_create", "resource": "PRODUCT", "type": "CREATE", "description": "Create products"},
        {"name": "product_read", "resource": "PRODUCT", "type": "READ", "description": "View products"},
        {"name": "product_update", "resource": "PRODUCT", "type": "UPDATE", "description": "Update products"},
        {"name": "product_delete", "resource": "PRODUCT", "type": "DELETE", "description": "Delete products"},
        {"name": "product_export", "resource": "PRODUCT", "type": "EXPORT", "description": "Export product data"},
        {"name": "product_import", "resource": "PRODUCT", "type": "IMPORT", "description": "Import product data"},
        
        # Inventory
        {"name": "inventory_create", "resource": "INVENTORY", "type": "CREATE", "description": "Add inventory items"},
        {"name": "inventory_read", "resource": "INVENTORY", "type": "READ", "description": "View inventory"},
        {"name": "inventory_update", "resource": "INVENTORY", "type": "UPDATE", "description": "Update inventory"},
        {"name": "inventory_delete", "resource": "INVENTORY", "type": "DELETE", "description": "Delete inventory items"},
        {"name": "inventory_export", "resource": "INVENTORY", "type": "EXPORT", "description": "Export inventory data"},
        {"name": "inventory_import", "resource": "INVENTORY", "type": "IMPORT", "description": "Import inventory data"},
        
        # Sales
        {"name": "sales_create", "resource": "SALES", "type": "CREATE", "description": "Create sales orders"},
        {"name": "sales_read", "resource": "SALES", "type": "READ", "description": "View sales"},
        {"name": "sales_update", "resource": "SALES", "type": "UPDATE", "description": "Update sales orders"},
        {"name": "sales_delete", "resource": "SALES", "type": "DELETE", "description": "Delete sales orders"},
        {"name": "sales_approve", "resource": "SALES", "type": "APPROVE", "description": "Approve sales orders"},
        {"name": "sales_export", "resource": "SALES", "type": "EXPORT", "description": "Export sales data"},
        
        # Customer Management
        {"name": "customer_create", "resource": "CUSTOMER", "type": "CREATE", "description": "Create customers"},
        {"name": "customer_read", "resource": "CUSTOMER", "type": "READ", "description": "View customers"},
        {"name": "customer_update", "resource": "CUSTOMER", "type": "UPDATE", "description": "Update customers"},
        {"name": "customer_delete", "resource": "CUSTOMER", "type": "DELETE", "description": "Delete customers"},
        {"name": "customer_export", "resource": "CUSTOMER", "type": "EXPORT", "description": "Export customer data"},
        {"name": "customer_import", "resource": "CUSTOMER", "type": "IMPORT", "description": "Import customer data"},
        
        # Financial/Accounting
        {"name": "financial_create", "resource": "FINANCIAL", "type": "CREATE", "description": "Create financial entries"},
        {"name": "financial_read", "resource": "FINANCIAL", "type": "READ", "description": "View financial data"},
        {"name": "financial_update", "resource": "FINANCIAL", "type": "UPDATE", "description": "Update financial entries"},
        {"name": "financial_delete", "resource": "FINANCIAL", "type": "DELETE", "description": "Delete financial entries"},
        {"name": "financial_approve", "resource": "FINANCIAL", "type": "APPROVE", "description": "Approve financial transactions"},
        {"name": "financial_export", "resource": "FINANCIAL", "type": "EXPORT", "description": "Export financial data"},
        
        # Reports
        {"name": "reports_read", "resource": "REPORTS", "type": "READ", "description": "View reports"},
        {"name": "reports_export", "resource": "REPORTS", "type": "EXPORT", "description": "Export reports"},
        
        # Settings
        {"name": "settings_read", "resource": "SETTINGS", "type": "READ", "description": "View system settings"},
        {"name": "settings_update", "resource": "SETTINGS", "type": "UPDATE", "description": "Update system settings"},
    ]
    
    for perm_data in resources:
        existing = db.query(Permission).filter(
            Permission.name == perm_data["name"]
        ).first()
        
        if not existing:
            permission = Permission(
                name=perm_data["name"],
                resource_type=perm_data["resource"],
                permission_type=perm_data["type"],
                description=perm_data["description"]
            )
            db.add(permission)
    
    db.commit()
    logger.info("✅ Created all system permissions")


def assign_admin_permissions(db: Session, admin_role: Role):
    """Assign all permissions to Admin role"""
    all_permissions = db.query(Permission).all()
    
    for permission in all_permissions:
        existing = db.query(RolePermission).filter(
            RolePermission.role_id == admin_role.id,
            RolePermission.permission_id == permission.id
        ).first()
        
        if not existing:
            role_permission = RolePermission(
                role_id=admin_role.id,
                permission_id=permission.id
            )
            db.add(role_permission)
    
    db.commit()
    logger.info(f"✅ Assigned all permissions to Admin role")


def create_admin_user(db: Session, admin_role: Role, branch: Branch, tenant: Tenant) -> User:
    """Create the admin/owner user"""
    admin_email = "admin@tsh.sale"
    admin_user = db.query(User).filter(User.email == admin_email).first()
    
    if not admin_user:
        # Create admin user with hashed password
        hashed_password = AuthService.hash_password("admin123")
        
        admin_user = User(
            name="System Administrator",
            email=admin_email,
            password=hashed_password,
            role_id=admin_role.id,
            branch_id=branch.id,
            tenant_id=tenant.id,
            employee_code="ADMIN001",
            phone="+964-XXX-XXXX",
            is_active=True,
            is_verified=True,
            is_salesperson=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        logger.info(f"✅ Created admin user: {admin_user.email}")
        logger.info(f"   📧 Email: {admin_email}")
        logger.info(f"   🔑 Password: admin123")
        logger.info(f"   ⚠️  IMPORTANT: Please change this password after first login!")
    else:
        logger.info(f"ℹ️  Admin user already exists: {admin_user.email}")
    
    return admin_user


def initialize_admin_system():
    """Main function to initialize admin user and permissions"""
    db = SessionLocal()
    try:
        logger.info("🚀 Starting admin system initialization...")
        
        # Step 1: Create default tenant
        tenant = create_default_tenant(db)
        
        # Step 2: Create default branch
        branch = create_default_branch(db)
        
        # Step 3: Create roles
        admin_role = create_admin_role(db)
        create_additional_roles(db)
        
        # Step 4: Create permissions
        create_permissions(db)
        
        # Step 5: Assign permissions to admin role
        assign_admin_permissions(db, admin_role)
        
        # Step 6: Create admin user
        admin_user = create_admin_user(db, admin_role, branch, tenant)
        
        logger.info("=" * 70)
        logger.info("✅ ADMIN SYSTEM INITIALIZATION COMPLETE!")
        logger.info("=" * 70)
        logger.info("")
        logger.info("🔐 ADMIN LOGIN CREDENTIALS:")
        logger.info(f"   📧 Email: admin@tsh.sale")
        logger.info(f"   🔑 Password: admin123")
        logger.info("")
        logger.info("🌐 Access Points:")
        logger.info(f"   • Frontend: http://localhost:5173")
        logger.info(f"   • Backend API: http://localhost:8000")
        logger.info(f"   • API Docs: http://localhost:8000/docs")
        logger.info("")
        logger.info("⚠️  SECURITY WARNING:")
        logger.info("   Please change the default password immediately after first login!")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ Error during initialization: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    initialize_admin_system()
