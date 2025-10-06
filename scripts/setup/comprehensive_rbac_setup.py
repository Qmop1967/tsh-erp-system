#!/usr/bin/env python3
"""
TSH ERP System - Complete RBAC System Setup
Comprehensive setup script for Role-Based Access Control system
Runs all necessary initialization steps in the correct order
"""

import sys
import os
import subprocess

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def run_script(script_path, script_name):
    """Run a Python script and return success status"""
    print(f"\n▶️  Running: {script_name}")
    print(f"   Path: {script_path}")
    
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_path}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.returncode != 0:
            print(f"❌ Script failed with exit code {result.returncode}")
            if result.stderr:
                print("Error output:")
                print(result.stderr)
            return False
        
        print(f"✅ {script_name} completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error running script: {e}")
        return False

def check_database_connection():
    """Check if database is accessible"""
    print("\n🔍 Checking database connection...")
    
    try:
        from app.db.database import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n📋 Please ensure:")
        print("   1. PostgreSQL is running")
        print("   2. Database credentials in .env are correct")
        print("   3. Database 'tsh_erp' exists")
        return False

def verify_models():
    """Verify that all models are properly defined"""
    print("\n🔍 Verifying models...")
    
    try:
        from app.models.user import User
        from app.models.role import Role
        from app.models.branch import Branch
        from app.models.permissions import Permission, RolePermission, UserPermission
        
        print("✅ All required models loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        return False

def create_scripts_if_missing():
    """Ensure all required scripts exist"""
    print("\n🔍 Checking required scripts...")
    
    scripts_dir = os.path.join(project_root, "scripts", "setup")
    required_scripts = {
        "seed_permissions.py": True,
        "init_user_system.py": True,
        "create_salesperson_user.py": True
    }
    
    all_exist = True
    for script, exists in required_scripts.items():
        script_path = os.path.join(scripts_dir, script)
        if os.path.exists(script_path):
            print(f"✅ {script}")
        else:
            print(f"❌ {script} not found")
            all_exist = False
    
    return all_exist

def show_summary(db):
    """Show a summary of the setup"""
    print_header("SETUP SUMMARY")
    
    try:
        from app.models.user import User
        from app.models.role import Role
        from app.models.permissions import Permission, RolePermission
        
        # Count statistics
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        total_roles = db.query(Role).count()
        total_permissions = db.query(Permission).count()
        
        print(f"\n📊 Database Statistics:")
        print(f"   Total Users: {total_users}")
        print(f"   Active Users: {active_users}")
        print(f"   Total Roles: {total_roles}")
        print(f"   Total Permissions: {total_permissions}")
        
        # List users
        print(f"\n👥 Users:")
        users = db.query(User).all()
        for user in users[:10]:  # Show first 10
            role_name = user.role.name if user.role else "No Role"
            status = "🟢" if user.is_active else "🔴"
            salesperson = "📱" if user.is_salesperson else "💻"
            print(f"   {status} {salesperson} {user.email:30s} | {role_name:15s} | {user.name}")
        
        if total_users > 10:
            print(f"   ... and {total_users - 10} more users")
        
        # List roles
        print(f"\n🎭 Roles:")
        roles = db.query(Role).all()
        for role in roles:
            perm_count = db.query(RolePermission).filter(
                RolePermission.role_id == role.id
            ).count()
            print(f"   • {role.name:20s} | {perm_count:3d} permissions | {role.description or 'No description'}")
        
        # Show test credentials
        print(f"\n🔑 Test Login Credentials:")
        test_users = [
            ("admin@tsh-erp.com", "admin123", "Admin - Full Access"),
            ("manager@tsh-erp.com", "manager123", "Manager"),
            ("sales@tsh-erp.com", "sales123", "Sales"),
            ("frati@tsh.sale", "frati123", "Salesperson (Mobile)"),
        ]
        
        for email, password, description in test_users:
            user = db.query(User).filter(User.email == email).first()
            if user:
                status = "✅" if user.is_active else "❌"
                print(f"   {status} {email:25s} / {password:15s} - {description}")
        
    except Exception as e:
        print(f"❌ Error showing summary: {e}")

def main():
    """Main execution function"""
    print_header("TSH ERP SYSTEM - COMPLETE RBAC SETUP")
    print("This script will set up the complete Role-Based Access Control system")
    print("including permissions, roles, and test users.")
    
    # Step 0: Pre-flight checks
    print_header("PRE-FLIGHT CHECKS")
    
    if not check_database_connection():
        print("\n❌ Setup aborted: Database connection failed")
        return False
    
    if not verify_models():
        print("\n❌ Setup aborted: Model verification failed")
        return False
    
    if not create_scripts_if_missing():
        print("\n❌ Setup aborted: Required scripts not found")
        return False
    
    print("\n✅ All pre-flight checks passed")
    
    # Ask for confirmation
    print("\n⚠️  This will:")
    print("   1. Create all system permissions")
    print("   2. Create default roles (Admin, Manager, Sales, etc.)")
    print("   3. Grant permissions to roles")
    print("   4. Create default users (admin, manager, sales)")
    print("   5. Create Salesperson role and user (frati@tsh.sale)")
    print("   6. Create branches if they don't exist")
    
    response = input("\n▶️  Continue with setup? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("\n❌ Setup cancelled by user")
        return False
    
    # Step 1: Create permissions and roles
    print_header("STEP 1: PERMISSIONS & ROLES")
    
    scripts_dir = os.path.join(project_root, "scripts", "setup")
    
    if not run_script(
        os.path.join(scripts_dir, "seed_permissions.py"),
        "Seed Permissions"
    ):
        print("\n❌ Failed to seed permissions. Aborting.")
        return False
    
    # Step 2: Initialize user system (branches and users)
    print_header("STEP 2: INITIALIZE USER SYSTEM")
    
    if not run_script(
        os.path.join(scripts_dir, "init_user_system.py"),
        "Initialize User System"
    ):
        print("\n❌ Failed to initialize user system. Aborting.")
        return False
    
    # Step 3: Create salesperson role and user
    print_header("STEP 3: SALESPERSON SETUP")
    
    if not run_script(
        os.path.join(scripts_dir, "create_salesperson_user.py"),
        "Create Salesperson User"
    ):
        print("\n⚠️  Salesperson setup had issues, but continuing...")
    
    # Step 4: Show summary
    try:
        from app.db.database import SessionLocal
        db = SessionLocal()
        show_summary(db)
        db.close()
    except Exception as e:
        print(f"❌ Error showing summary: {e}")
    
    # Final success message
    print_header("SETUP COMPLETE!")
    
    print("\n🎉 RBAC system setup completed successfully!")
    print("\n📋 Next Steps:")
    print("   1. Start the backend server:")
    print("      cd /Users/khaleelal-mulla/TSH_ERP_System_Local")
    print("      uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("\n   2. Start the frontend:")
    print("      cd frontend")
    print("      npm run dev")
    print("\n   3. Test mobile app:")
    print("      cd mobile/flutter_apps/05_tsh_salesperson_app")
    print("      flutter run -d chrome")
    print("      Login: frati@tsh.sale / frati123")
    print("\n   4. Test web app:")
    print("      Open: http://localhost:5173")
    print("      Login: admin@tsh-erp.com / admin123")
    
    print("\n📚 Documentation:")
    print("   - COMPLETE_RBAC_INTEGRATION_GUIDE.md")
    print("   - UNIFIED_PERMISSION_SYSTEM.md")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
