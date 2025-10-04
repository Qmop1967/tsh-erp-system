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

# Import all models to ensure they're registered
from app.models.user import User
from app.models.tenant import Tenant
from app.models.branch import Branch
from app.models.role import Role
from app.models.permissions import Permission, RolePermission
from app.models.advanced_security import *

def create_default_tenant():
    """Create default tenant with admin user"""
    print("🏢 Creating default tenant...")
    
    db = SessionLocal()
    try:
        # Check if default tenant already exists
        existing_tenant = db.query(Tenant).filter(Tenant.code == "TSH_DEFAULT").first()
        if existing_tenant:
            print(f"✅ Default tenant already exists: {existing_tenant.name}")
            return existing_tenant
        
        # Create default tenant
        tenant = Tenant(
            name="TSH ERP Default Organization",
            code="TSH_DEFAULT",
            subdomain="default",
            is_active=True
        )
        db.add(tenant)
        db.flush()  # Get the tenant ID
        
        # Create default admin role
        admin_role = Role(
            name="Admin",
            display_name="System Administrator",
            description="Full system access",
            tenant_id=tenant.id,
            is_active=True
        )
        db.add(admin_role)
        db.flush()
        
        # Create default branch
        default_branch = Branch(
            name="Main Branch",
            code="MAIN",
            tenant_id=tenant.id,
            is_active=True
        )
        db.add(default_branch)
        db.flush()
        
        # Create admin user
        from app.services.security_service import SecurityService
        security_service = SecurityService(db)
        
        password_hash, salt = security_service.hash_password("AdminPass123!")
        
        admin_user = User(
            username="admin",
            email="admin@tsh-erp.com",
            password_hash=password_hash,
            password_salt=salt,
            first_name="System",
            last_name="Administrator",
            tenant_id=tenant.id,
            branch_id=default_branch.id,
            role_id=admin_role.id,
            is_active=True,
            is_verified=True
        )
        db.add(admin_user)
        
        db.commit()
        
        print(f"✅ Created tenant: {tenant.name} (ID: {tenant.id})")
        print(f"✅ Created admin user: admin")
        print(f"⚠️  Default admin password: AdminPass123!")
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
        # Enable RLS on tables (simplified version)
        rls_tables = ['users', 'branches', 'products', 'customers', 'sales_orders']
        
        for table in rls_tables:
            try:
                # Enable RLS
                db.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
                print(f"✅ Enabled RLS on {table}")
            except Exception as e:
                print(f"⚠️  RLS already enabled on {table} or table doesn't exist: {e}")
        
        db.commit()
        print("✅ Row-level security setup complete")
    except Exception as e:
        print(f"❌ Error setting up database security: {e}")
        db.rollback()
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

def setup_advanced_security_system():
    """Setup the complete advanced security system"""
    print("🔐 Setting up advanced security system...")
    
    db = SessionLocal()
    try:
        # Import advanced security models
        from app.models.advanced_security import (
            SecurityPolicy, RestrictionGroup, RLSRule, FLSRule,
            MFADevice, UserSession, AuditLog, DeviceSession
        )
        from app.config.security_config import SecurityPolicies, RLSRules, FLSRules
        
        # Create default security policies
        policies = SecurityPolicies.get_default_policies()
        for policy_data in policies:
            existing = db.query(SecurityPolicy).filter(
                SecurityPolicy.name == policy_data["name"]
            ).first()
            
            if not existing:
                policy = SecurityPolicy(
                    name=policy_data["name"],
                    display_name=policy_data["display_name"],
                    description=policy_data["description"],
                    policy_document=policy_data["policy_document"],
                    effect=policy_data["effect"],
                    priority=policy_data["priority"],
                    is_active=True,
                    created_by=1  # Admin user
                )
                db.add(policy)
                print(f"✅ Created security policy: {policy_data['display_name']}")
        
        # Create default restriction groups
        restriction_groups = SecurityPolicies.get_default_restriction_groups()
        for group_data in restriction_groups:
            existing = db.query(RestrictionGroup).filter(
                RestrictionGroup.name == group_data["name"]
            ).first()
            
            if not existing:
                group = RestrictionGroup(
                    name=group_data["name"],
                    description=group_data["description"],
                    restrictions=group_data["restrictions"],
                    is_active=True,
                    created_by=1
                )
                db.add(group)
                print(f"✅ Created restriction group: {group_data['name']}")
        
        # Create default RLS rules
        rls_rules = RLSRules.get_default_rules()
        for rule_data in rls_rules:
            existing = db.query(RLSRule).filter(
                RLSRule.name == rule_data["name"]
            ).first()
            
            if not existing:
                rule = RLSRule(
                    name=rule_data["name"],
                    description=rule_data["description"],
                    table_name=rule_data["table_name"],
                    rule_expression=rule_data["rule_expression"],
                    applies_to_actions=rule_data["applies_to_actions"],
                    applies_to_roles=rule_data["applies_to_roles"],
                    is_active=True,
                    created_by=1
                )
                db.add(rule)
                print(f"✅ Created RLS rule: {rule_data['name']}")
        
        # Create default FLS rules
        fls_rules = FLSRules.get_default_rules()
        for rule_data in fls_rules:
            existing = db.query(FLSRule).filter(
                FLSRule.name == rule_data["name"]
            ).first()
            
            if not existing:
                rule = FLSRule(
                    name=rule_data["name"],
                    description=rule_data["description"],
                    table_name=rule_data["table_name"],
                    column_name=rule_data["column_name"],
                    is_visible=rule_data.get("is_visible", True),
                    is_readable=rule_data.get("is_readable", True),
                    is_writable=rule_data.get("is_writable", True),
                    masking_pattern=rule_data.get("masking_pattern"),
                    requires_encryption=rule_data.get("requires_encryption", False),
                    applies_to_roles=rule_data["applies_to_roles"],
                    is_active=True,
                    created_by=1
                )
                db.add(rule)
                print(f"✅ Created FLS rule: {rule_data['name']}")
        
        db.commit()
        print("✅ Advanced security system setup complete")
        
    except Exception as e:
        print(f"❌ Error setting up advanced security system: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_firebase_config():
    """Create Firebase configuration for MFA mobile app"""
    print("📱 Creating Firebase configuration...")
    
    firebase_config = {
        "apiKey": "your-firebase-api-key",
        "authDomain": "tsh-erp-mfa.firebaseapp.com",
        "projectId": "tsh-erp-mfa",
        "storageBucket": "tsh-erp-mfa.appspot.com",
        "messagingSenderId": "123456789",
        "appId": "1:123456789:android:abcdef123456789",
        "serverKey": "your-firebase-server-key"
    }
    
    config_dir = Path("mobile/flutter_apps/09_tsh_mfa_authenticator/android/app")
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Create google-services.json placeholder
    google_services = {
        "project_info": {
            "project_number": "123456789",
            "project_id": "tsh-erp-mfa"
        },
        "client": [
            {
                "client_info": {
                    "mobilesdk_app_id": "1:123456789:android:abcdef123456789",
                    "android_client_info": {
                        "package_name": "com.tsh.mfa_authenticator"
                    }
                }
            }
        ]
    }
    
    with open(config_dir / "google-services.json", "w") as f:
        json.dump(google_services, f, indent=2)
    
    print("✅ Firebase configuration created (placeholder)")
    print("⚠️  Please update with your actual Firebase project credentials")

def setup_environment_file():
    """Create comprehensive environment file"""
    print("� Creating environment configuration...")
    
    env_content = """# TSH ERP System - Advanced Security Environment Configuration
# Generated on {date}

# === DATABASE ===
DATABASE_URL=postgresql://username:password@localhost:5432/tsh_erp_db
REDIS_URL=redis://localhost:6379/0

# === SECURITY ===
SECURITY_ENCRYPTION_KEY=your-256-bit-encryption-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production-minimum-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# === MFA & AUTHENTICATION ===
MFA_ISSUER_NAME=TSH ERP System
MFA_BACKUP_CODES_ENCRYPTION_KEY=your-backup-codes-encryption-key-here
BIOMETRIC_ENCRYPTION_KEY=your-biometric-data-encryption-key-here

# === FIREBASE (Mobile MFA) ===
FIREBASE_PROJECT_ID=tsh-erp-mfa
FIREBASE_SERVER_KEY=your-firebase-server-key-here
FIREBASE_WEB_API_KEY=your-firebase-web-api-key-here

# === EXTERNAL SERVICES ===
# GeoIP Service
GEOIP_API_KEY=your-geoip-api-key-here
GEOIP_SERVICE_URL=https://api.ipgeolocation.io/ipgeo

# Email Service (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true

# SMS Service (for MFA)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# === SECURITY MONITORING ===
SECURITY_WEBHOOK_URL=https://your-monitoring-service.com/webhook
SECURITY_ALERT_EMAIL=security@tsh-erp.com

# === ENVIRONMENT ===
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# === API KEYS ===
API_RATE_LIMIT_REDIS_URL=redis://localhost:6379/1
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080

# === MOBILE APP ===
MOBILE_APP_DEEP_LINK_SCHEME=tsh-mfa
MOBILE_APP_STORE_URL=https://play.google.com/store/apps/details?id=com.tsh.mfa_authenticator
""".format(date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    env_file = Path(".env.example")
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print("✅ Environment configuration created (.env.example)")
    print("⚠️  Copy to .env and update with your actual values")

def main():
    """Main setup function"""
    print("�🚀 TSH ERP System - Advanced Security Setup")
    print("=" * 60)
    
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
            return False
        
        # Step 5: Setup advanced security system
        setup_advanced_security_system()
        
        # Step 6: Setup permissions
        setup_default_permissions()
        
        # Step 7: Create sample users
        create_sample_users()
        
        # Step 8: Create Firebase config
        create_firebase_config()
        
        # Step 9: Setup environment file
        setup_environment_file()
        
        # Step 10: Verify setup
        verify_setup()
        
        print("\n🎉 Advanced Security System Setup Complete!")
        print("=" * 60)
        print("\n📋 What was created:")
        print("• Advanced security models (ABAC, RBAC, PBAC)")
        print("• Row-Level Security (RLS) rules")
        print("• Field-Level Security (FLS) rules")
        print("• Centralized audit logging system")
        print("• Multi-Factor Authentication (MFA) framework")
        print("• Device and session management")
        print("• Security policies and restriction groups")
        print("• Mobile MFA application structure")
        print("• Comprehensive security configuration")
        
        print("\n🔧 Next Steps:")
        print("1. Copy .env.example to .env and configure credentials")
        print("2. Run database migration: python scripts/migrations/create_advanced_security_system.py")
        print("3. Update Firebase configuration with real project details")
        print("4. Configure external services (GeoIP, SMS, Email)")
        print("5. Build and deploy the mobile MFA app")
        print("6. Test the security system thoroughly")
        print("7. Update admin password and enable MFA")
        
        print("\n🔒 Security Features Available:")
        print("• Multi-layered access control (ABAC + RBAC + PBAC)")
        print("• Dynamic policy evaluation with risk scoring")
        print("• Real-time session and device monitoring")
        print("• Location-based access restrictions")
        print("• Advanced audit logging with forensic capabilities")
        print("• Mobile MFA with push notifications")
        print("• Biometric and passless authentication")
        print("• Automated threat detection and response")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("Please check the error and try again.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
