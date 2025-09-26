#!/usr/bin/env python3
"""
TSH ERP System - Simple Security Initialization
Initialize the enhanced security features.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import SessionLocal

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

def initialize_default_permissions():
    """Initialize default permissions in database"""
    print("🔑 Initializing default permissions...")
    
    db = SessionLocal()
    try:
        # Check if permissions table exists and has data
        result = db.execute(text("SELECT COUNT(*) FROM permissions"))
        count = result.scalar()
        
        if count > 0:
            print(f"✅ Permissions already initialized ({count} permissions found)")
            return True
        
        # Insert basic permissions
        permissions_sql = """
        INSERT INTO permissions (name, description, resource_type, permission_type, is_active, created_at) VALUES
        ('create_user', 'Create new users', 'USER', 'CREATE', true, NOW()),
        ('read_user', 'View user information', 'USER', 'READ', true, NOW()),
        ('update_user', 'Update user information', 'USER', 'UPDATE', true, NOW()),
        ('delete_user', 'Delete users', 'USER', 'DELETE', true, NOW()),
        ('create_backup', 'Create system backups', 'SETTINGS', 'CREATE', true, NOW()),
        ('view_audit_logs', 'View system audit logs', 'SETTINGS', 'READ', true, NOW()),
        ('view_system_health', 'View system health status', 'SETTINGS', 'READ', true, NOW()),
        ('create_product', 'Create new products', 'PRODUCT', 'CREATE', true, NOW()),
        ('read_product', 'View product information', 'PRODUCT', 'READ', true, NOW()),
        ('update_product', 'Update product information', 'PRODUCT', 'UPDATE', true, NOW()),
        ('delete_product', 'Delete products', 'PRODUCT', 'DELETE', true, NOW())
        ON CONFLICT (name) DO NOTHING;
        """
        
        db.execute(text(permissions_sql))
        db.commit()
        
        print("✅ Default permissions initialized")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing permissions: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def update_admin_role():
    """Update admin role with tenant support"""
    print("👑 Updating admin role...")
    
    db = SessionLocal()
    try:
        # Check if admin role exists
        result = db.execute(text("SELECT id FROM roles WHERE name = 'Admin' LIMIT 1"))
        admin_role = result.fetchone()
        
        if admin_role:
            # Update admin role with new fields
            db.execute(text("""
                UPDATE roles SET 
                    description = 'System Administrator with full access',
                    is_active = true,
                    created_at = COALESCE(created_at, NOW()),
                    updated_at = NOW()
                WHERE name = 'Admin'
            """))
            print("✅ Admin role updated")
        else:
            # Create admin role
            db.execute(text("""
                INSERT INTO roles (name, description, is_active, created_at, updated_at)
                VALUES ('Admin', 'System Administrator with full access', true, NOW(), NOW())
                ON CONFLICT (name) DO NOTHING
            """))
            print("✅ Admin role created")
        
        db.commit()
        return True
        
    except Exception as e:
        print(f"❌ Error updating admin role: {e}")
        db.rollback()
        return False
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
        db.execute(text("SELECT 1"))
        db.close()
        checks.append(("Database connection", True))
    except:
        checks.append(("Database connection", False))
    
    # Check permissions table
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT COUNT(*) FROM permissions"))
        permission_count = result.scalar()
        db.close()
        checks.append(("Permissions loaded", permission_count > 0))
    except:
        checks.append(("Permissions loaded", False))
    
    # Check roles table
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT COUNT(*) FROM roles"))
        role_count = result.scalar()
        db.close()
        checks.append(("Roles available", role_count > 0))
    except:
        checks.append(("Roles available", False))
    
    print("\n📋 Setup Verification:")
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 Security setup completed successfully!")
        print("\n📝 Next Steps:")
        print("1. Start the application: uvicorn app.main:app --reload")
        print("2. Access enhanced settings at: http://localhost:8000/api/security/system/health")
        print("3. View API documentation: http://localhost:8000/docs")
        print("4. Check security endpoints: http://localhost:8000/api/security/")
    else:
        print("\n⚠️  Some checks failed. Please review the errors above.")

def main():
    """Main setup function"""
    print("🚀 TSH ERP System - Security Initialization")
    print("=" * 50)
    
    try:
        # Step 1: Create encryption key
        create_encryption_key()
        
        # Step 2: Create directories
        create_backup_directories()
        
        # Step 3: Initialize permissions
        if not initialize_default_permissions():
            print("⚠️  Permissions initialization failed, but continuing...")
        
        # Step 4: Update admin role
        if not update_admin_role():
            print("⚠️  Admin role update failed, but continuing...")
        
        # Step 5: Verify setup
        verify_setup()
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("Please check the error and try again.")

if __name__ == "__main__":
    main()
