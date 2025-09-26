#!/usr/bin/env python3
"""
TSH ERP System - Advanced Security Setup Script
This script initializes the enhanced security features and multi-tenancy system.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.db.database import engine, SessionLocal
from app.services.tenant_service import TenantService, setup_row_level_security
from app.services.security_service import SecurityService
from app.services.permission_service import PermissionService
from app.models.permissions import Permission, RolePermission
from app.models.role import Role

def create_default_tenant():
    """Create default tenant with admin user"""
    print("🏢 Creating default tenant...")
    
    db = SessionLocal()
    try:
        tenant_service = TenantService(db)
        
        # Create default tenant
        admin_user_data = {
            "username": "admin",
            "email": "admin@tsh-erp.com",
            "password": "AdminPass123!",  # Change this in production
            "first_name": "System",
            "last_name": "Administrator"
        }
        
        tenant = tenant_service.create_tenant(
            name="TSH ERP Default Organization",
            code="TSH_DEFAULT",
            subdomain="default",
            admin_user=admin_user_data
        )
        
        print(f"✅ Created tenant: {tenant.name} (ID: {tenant.id})")
        print(f"✅ Created admin user: {admin_user_data['username']}")
        print(f"⚠️  Default admin password: {admin_user_data['password']}")
        print("⚠️  CHANGE THE DEFAULT PASSWORD IMMEDIATELY!")
        
        return tenant
    
    except Exception as e:
        print(f"❌ Error creating default tenant: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def setup_database_security():
    """Setup row-level security and indexes"""
    print("🔒 Setting up database security...")
    
    db = SessionLocal()
    try:
        setup_row_level_security(db)
        print("✅ Row-level security policies enabled")
    except Exception as e:
        print(f"❌ Error setting up database security: {e}")
    finally:
        db.close()

def create_encryption_key():
    """Create encryption key for sensitive data"""
    print("🔐 Creating encryption key...")
    
    from cryptography.fernet import Fernet
    
    key_file = Path("config/encryption.key")
    
    if key_file.exists():
        print("✅ Encryption key already exists")
        return
    
    try:
        key = Fernet.generate_key()
        key_file.parent.mkdir(exist_ok=True)
        
        with open(key_file, "wb") as f:
            f.write(key)
        
        # Set restrictive permissions
        os.chmod(key_file, 0o600)
        
        print("✅ Encryption key created and secured")
        print(f"📁 Key location: {key_file}")
        
    except Exception as e:
        print(f"❌ Error creating encryption key: {e}")

def create_backup_directories():
    """Create backup and security directories"""
    print("📁 Creating backup directories...")
    
    directories = [
        "backups",
        "logs/security",
        "logs/audit",
        "temp/exports"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_default_permissions():
    """Setup default role permissions"""
    print("🔑 Setting up default permissions...")
    
    db = SessionLocal()
    try:
        permission_service = PermissionService(db)
        
        # Get admin role (created by tenant setup)
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if not admin_role:
            print("❌ Admin role not found")
            return
        
        # Get all permissions
        permissions = db.query(Permission).all()
        
        # Grant all permissions to admin role
        for permission in permissions:
            existing = db.query(RolePermission).filter(
                RolePermission.role_id == admin_role.id,
                RolePermission.permission_id == permission.id
            ).first()
            
            if not existing:
                role_permission = RolePermission(
                    role_id=admin_role.id,
                    permission_id=permission.id,
                    granted_by=1,  # System user
                    granted_at=datetime.utcnow()
                )
                db.add(role_permission)
        
        db.commit()
        print(f"✅ Granted {len(permissions)} permissions to Admin role")
        
    except Exception as e:
        print(f"❌ Error setting up permissions: {e}")
        db.rollback()
    finally:
        db.close()

def create_sample_users():
    """Create sample users for testing"""
    print("👥 Creating sample users...")
    
    db = SessionLocal()
    try:
        from app.models.user import User
        from app.services.security_service import SecurityService
        
        security_service = SecurityService(db)
        
        sample_users = [
            {
                "username": "manager",
                "email": "manager@tsh-erp.com",
                "password": "ManagerPass123!",
                "first_name": "Branch",
                "last_name": "Manager",
                "role": "Manager"
            },
            {
                "username": "operator",
                "email": "operator@tsh-erp.com", 
                "password": "OperatorPass123!",
                "first_name": "System",
                "last_name": "Operator",
                "role": "Operator"
            }
        ]
        
        for user_data in sample_users:
            # Check if user exists
            existing = db.query(User).filter(User.username == user_data["username"]).first()
            if existing:
                print(f"✅ User {user_data['username']} already exists")
                continue
            
            # Hash password
            password_hash, salt = security_service.hash_password(user_data["password"])
            
            # Create user (simplified - in production, use proper user creation service)
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                password_hash=password_hash,
                password_salt=salt,
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                tenant_id=1,  # Default tenant
                branch_id=1,  # Default branch
                is_active=True,
                is_verified=True
            )
            
            db.add(user)
            print(f"✅ Created user: {user_data['username']}")
        
        db.commit()
        
    except Exception as e:
        print(f"❌ Error creating sample users: {e}")
        db.rollback()
    finally:
        db.close()

def verify_setup():
    """Verify that the setup was successful"""
    print("🔍 Verifying setup...")
    
    checks = []
    
    # Check encryption key
    key_file = Path("config/encryption.key")
    checks.append(("Encryption key", key_file.exists()))
    
    # Check backup directory
    backup_dir = Path("backups")
    checks.append(("Backup directory", backup_dir.exists()))
    
    # Check database connection
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        checks.append(("Database connection", True))
    except:
        checks.append(("Database connection", False))
    
    # Check tenant exists
    try:
        db = SessionLocal()
        from app.models.permissions import Tenant
        tenant_count = db.query(Tenant).count()
        db.close()
        checks.append(("Default tenant", tenant_count > 0))
    except:
        checks.append(("Default tenant", False))
    
    # Check permissions
    try:
        db = SessionLocal()
        permission_count = db.query(Permission).count()
        db.close()
        checks.append(("Permissions loaded", permission_count > 0))
    except:
        checks.append(("Permissions loaded", False))
    
    print("\n📋 Setup Verification:")
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 Setup completed successfully!")
        print("\n📝 Next Steps:")
        print("1. Change default admin password")
        print("2. Configure environment variables (.env)")
        print("3. Run database migrations: alembic upgrade head")
        print("4. Start the application: uvicorn app.main:app --reload")
        print("5. Access settings at: http://localhost:8000/settings")
    else:
        print("\n⚠️  Some checks failed. Please review the errors above.")

def main():
    """Main setup function"""
    print("🚀 TSH ERP System - Advanced Security Setup")
    print("=" * 50)
    
    try:
        # Step 1: Create encryption key
        create_encryption_key()
        
        # Step 2: Create directories
        create_backup_directories()
        
        # Step 3: Setup database security
        setup_database_security()
        
        # Step 4: Create default tenant
        tenant = create_default_tenant()
        if not tenant:
            print("❌ Failed to create default tenant. Aborting setup.")
            return
        
        # Step 5: Setup permissions
        setup_default_permissions()
        
        # Step 6: Create sample users
        create_sample_users()
        
        # Step 7: Verify setup
        verify_setup()
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("Please check the error and try again.")

if __name__ == "__main__":
    main()
