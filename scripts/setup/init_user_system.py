"""
Initialize User Management System for TSH ERP
تهيئة نظام إدارة المستخدمين لـ TSH ERP
"""

import sys
import os
# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User
from app.models.role import Role  
from app.models.branch import Branch
from app.services.auth_service import AuthService

def initialize_roles(db: Session):
    """Initialize default roles - تهيئة الأدوار الافتراضية"""
    default_roles = [
        {"name": "admin"},
        {"name": "manager"}, 
        {"name": "sales"},
        {"name": "inventory"},
        {"name": "accounting"},
        {"name": "cashier"},
        {"name": "viewer"}
    ]
    
    for role_data in default_roles:
        existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing_role:
            role = Role(**role_data)
            db.add(role)
            print(f"✓ Created role: {role_data['name']}")
        else:
            print(f"- Role already exists: {role_data['name']}")
    
    db.commit()

def initialize_branches(db: Session):
    """Initialize default branches - تهيئة الفروع الافتراضية"""
    default_branches = [
        {
            "name": "Main Branch",
            "name_ar": "الفرع الرئيسي", 
            "name_en": "Main Branch",
            "location": "Baghdad, Iraq",
            "branch_code": "MAIN",
            "branch_type": "MAIN_WHOLESALE",
            "is_active": True,
            "description_ar": "الفرع الرئيسي لتجارة الجملة",
            "description_en": "Main wholesale branch",
            "phone": "+964-xxx-xxxx",
            "email": "main@tsh-erp.com"
        },
        {
            "name": "Dora Branch", 
            "name_ar": "فرع الدورة",
            "name_en": "Dora Branch",
            "location": "Dora, Baghdad",
            "branch_code": "DORA",
            "branch_type": "DORA_BRANCH",
            "is_active": True,
            "description_ar": "فرع الدورة للبيع بالتجزئة",
            "description_en": "Dora retail branch",
            "phone": "+964-xxx-yyyy",
            "email": "dora@tsh-erp.com"
        }
    ]
    
    for branch_data in default_branches:
        existing_branch = db.query(Branch).filter(Branch.branch_code == branch_data["branch_code"]).first()
        if not existing_branch:
            branch = Branch(**branch_data)
            db.add(branch)
            print(f"✓ Created branch: {branch_data['name']} ({branch_data['branch_code']})")
        else:
            print(f"- Branch already exists: {branch_data['name']} ({branch_data['branch_code']})")
    
    db.commit()

def initialize_admin_user(db: Session):
    """Initialize default admin user - تهيئة مستخدم المدير الافتراضي"""
    
    # Get admin role and main branch
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    main_branch = db.query(Branch).filter(Branch.branch_code == "MAIN").first()
    
    if not admin_role:
        print("❌ Admin role not found. Please run initialize_roles first.")
        return
        
    if not main_branch:
        print("❌ Main branch not found. Please run initialize_branches first.")
        return
    
    # Check if admin user already exists
    existing_admin = db.query(User).filter(User.email == "admin@tsh-erp.com").first()
    if existing_admin:
        print("- Admin user already exists: admin@tsh-erp.com")
        return
    
    # Create admin user
    admin_user_data = {
        "name": "System Administrator",
        "email": "admin@tsh-erp.com", 
        "password": AuthService.get_password_hash("admin123"),  # Hash the password
        "role_id": admin_role.id,
        "branch_id": main_branch.id,
        "employee_code": "ADM001",
        "phone": "+964-xxx-0001",
        "is_salesperson": False,
        "is_active": True
    }
    
    admin_user = User(**admin_user_data)
    db.add(admin_user)
    db.commit()
    print("✓ Created admin user: admin@tsh-erp.com (password: admin123)")

def initialize_sample_users(db: Session):
    """Initialize sample users - تهيئة مستخدمين تجريبيين"""
    
    # Get roles and branches
    manager_role = db.query(Role).filter(Role.name == "manager").first()
    sales_role = db.query(Role).filter(Role.name == "sales").first()
    main_branch = db.query(Branch).filter(Branch.branch_code == "MAIN").first()
    dora_branch = db.query(Branch).filter(Branch.branch_code == "DORA").first()
    
    sample_users = [
        {
            "name": "Ahmed Manager",
            "email": "manager@tsh-erp.com",
            "password": "manager123",
            "role_id": manager_role.id if manager_role else 1,
            "branch_id": main_branch.id if main_branch else 1,
            "employee_code": "MGR001",
            "phone": "+964-xxx-0002",
            "is_salesperson": False,
            "is_active": True
        },
        {
            "name": "Sara Sales",
            "email": "sales@tsh-erp.com", 
            "password": "sales123",
            "role_id": sales_role.id if sales_role else 1,
            "branch_id": dora_branch.id if dora_branch else 1,
            "employee_code": "SAL001",
            "phone": "+964-xxx-0003",
            "is_salesperson": True,
            "is_active": True
        }
    ]
    
    for user_data in sample_users:
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing_user:
            # Hash password
            user_data["password"] = AuthService.get_password_hash(user_data["password"])
            user = User(**user_data)
            db.add(user)
            print(f"✓ Created user: {user_data['name']} ({user_data['email']})")
        else:
            print(f"- User already exists: {user_data['name']} ({user_data['email']})")
    
    db.commit()

def main():
    """Main initialization function"""
    print("🚀 Initializing TSH ERP User Management System...")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        print("\n1. Initializing Roles...")
        initialize_roles(db)
        
        print("\n2. Initializing Branches...")
        initialize_branches(db)
        
        print("\n3. Initializing Admin User...")
        initialize_admin_user(db)
        
        print("\n4. Initializing Sample Users...")
        initialize_sample_users(db)
        
        print("\n" + "=" * 50)
        print("✅ User Management System initialized successfully!")
        print("\nDefault login credentials:")
        print("- Admin: admin@tsh-erp.com / admin123")
        print("- Manager: manager@tsh-erp.com / manager123")
        print("- Sales: sales@tsh-erp.com / sales123")
        
    except Exception as e:
        print(f"❌ Error initializing user system: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
