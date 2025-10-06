# TSH ERP System - Complete RBAC Integration Guide
## Role-Based Access Control System Setup & Integration

### 📋 Overview
This guide provides a comprehensive, systematic approach to enabling complete role, user, and permission integration across the entire TSH ERP System (Backend, Web Frontend, Mobile Apps).

---

## 🏗️ System Architecture

### Database Schema
```
┌─────────────────────────────────────────────────────┐
│              RBAC Database Structure                 │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────┐      ┌──────────────┐                │
│  │  Roles   │──────│ Role         │                │
│  │          │      │ Permissions  │                │
│  └────┬─────┘      └──────┬───────┘                │
│       │                   │                         │
│       │              ┌────┴────────┐                │
│       │              │ Permissions │                │
│       │              └─────────────┘                │
│  ┌────┴─────┐                                       │
│  │  Users   │       ┌──────────────┐                │
│  │          │───────│    User      │                │
│  └──────────┘       │ Permissions  │                │
│                     └──────────────┘                │
│                                                      │
│  ┌──────────────────────────────────┐               │
│  │      Audit Logs                  │               │
│  └──────────────────────────────────┘               │
└─────────────────────────────────────────────────────┘
```

### Current Models
1. **User** (`app/models/user.py`)
   - Links to Role via `role_id`
   - Contains `is_salesperson`, `is_active`, `branch_id`, `tenant_id`
   
2. **Role** (`app/models/role.py`)
   - Contains role metadata
   - Links to RolePermissions
   
3. **Permission** (`app/models/permissions.py`)
   - Defines system-wide permissions
   - Uses enums: `PermissionType`, `ResourceType`
   
4. **RolePermission** (`app/models/permissions.py`)
   - Maps roles to permissions
   - Supports ABAC (Attribute-Based Access Control) via conditions
   
5. **UserPermission** (`app/models/permissions.py`)
   - Direct user permission overrides
   - Higher priority than role permissions

---

## 🔧 Step-by-Step Integration

### Phase 1: Database Setup & Seeding

#### 1.1 Create Comprehensive Permission Seed Script
**Location:** `scripts/setup/comprehensive_rbac_setup.py`

This script will:
- ✅ Create all necessary permissions (already exists: `seed_permissions.py`)
- ✅ Create default roles with appropriate permissions
- ✅ Create default admin user with full access
- ✅ Create salesperson role and sample salesperson user

#### 1.2 Run Database Migrations
```bash
# Ensure all tables exist
alembic revision --autogenerate -m "Add RBAC tables"
alembic upgrade head

# Or if not using Alembic:
python scripts/setup/create_tables.py
```

#### 1.3 Seed Permissions and Roles
```bash
# Create all permissions and roles
python scripts/setup/seed_permissions.py

# Create sample users
python scripts/setup/init_user_system.py
```

---

### Phase 2: Backend Integration

#### 2.1 Update Authentication Service
**File:** `app/services/auth_service.py`

**Current State:** ✅ Already loads user with role relationship

**Enhancement Needed:**
```python
# Add permission checking to auth service
from app.services.permission_service import PermissionService

@staticmethod
def get_user_permissions(db: Session, user_id: int):
    """Get all user permissions"""
    permission_service = PermissionService(db)
    return permission_service.get_user_permissions(user_id)
```

#### 2.2 Create Permission Middleware
**File:** `app/middleware/permission_middleware.py` (NEW)

```python
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.permission_service import PermissionService
from app.db.database import get_db

class PermissionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Attach permission checker to request
        if hasattr(request.state, 'user_id'):
            db = next(get_db())
            permission_service = PermissionService(db)
            request.state.permission_service = permission_service
        
        response = await call_next(request)
        return response
```

#### 2.3 Update API Endpoints with Permission Decorators
**Example:** `app/routers/inventory.py`

```python
from app.services.permission_service import require_permission

@router.get("/items")
@require_permission("inventory.view")
async def get_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only users with "inventory.view" permission can access
    pass

@router.post("/items")
@require_permission("inventory.create")
async def create_item(...):
    pass
```

#### 2.4 Update Login Response to Include Permissions
**File:** `app/routers/auth.py`

```python
# In login endpoint, add:
from app.services.permission_service import PermissionService

@router.post("/login")
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    # ... existing auth logic ...
    
    # Get user permissions
    permission_service = PermissionService(db)
    user_permissions = permission_service.get_user_permissions(user.id)
    
    return {
        "token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.name if user.role else None,
            "permissions": user_permissions,  # Add this
            "branch_id": user.branch_id,
            # ... other fields
        }
    }
```

---

### Phase 3: Frontend (Web) Integration

#### 3.1 Update Auth Store to Include Permissions
**File:** `frontend/src/stores/authStore.ts`

```typescript
interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  permissions: Permission[];  // ADD THIS
  branch_id: number;
  // ... other fields
}

interface Permission {
  name: string;
  description: string;
  resource_type: string;
  permission_type: string;
  source: 'role' | 'direct';
  granted: boolean;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  
  // ADD THESE:
  hasPermission: (permission: string) => boolean;
  hasAnyPermission: (permissions: string[]) => boolean;
  hasAllPermissions: (permissions: string[]) => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // ... existing state ...
      
      hasPermission: (permission: string) => {
        const user = get().user;
        if (!user || !user.permissions) return false;
        
        // Admin gets everything
        if (user.role === 'Admin') return true;
        
        // Check specific permission
        return user.permissions.some(p => 
          p.name === permission && p.granted
        );
      },
      
      hasAnyPermission: (permissions: string[]) => {
        return permissions.some(p => get().hasPermission(p));
      },
      
      hasAllPermissions: (permissions: string[]) => {
        return permissions.every(p => get().hasPermission(p));
      },
    }),
    {
      name: 'auth-storage',
      // ... existing persist config
    }
  )
);
```

#### 3.2 Create Permission Guard Components
**File:** `frontend/src/components/guards/PermissionGuard.tsx` (NEW)

```typescript
import React from 'react';
import { useAuthStore } from '@/stores/authStore';
import { Navigate } from 'react-router-dom';

interface PermissionGuardProps {
  permission: string | string[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
  redirectTo?: string;
}

export const PermissionGuard: React.FC<PermissionGuardProps> = ({
  permission,
  children,
  fallback,
  redirectTo = '/unauthorized'
}) => {
  const { hasPermission, hasAnyPermission } = useAuthStore();
  
  const hasAccess = Array.isArray(permission)
    ? hasAnyPermission(permission)
    : hasPermission(permission);
  
  if (!hasAccess) {
    if (fallback) return <>{fallback}</>;
    if (redirectTo) return <Navigate to={redirectTo} />;
    return null;
  }
  
  return <>{children}</>;
};

// Usage example:
// <PermissionGuard permission="inventory.view">
//   <InventoryPage />
// </PermissionGuard>
```

#### 3.3 Update Navigation to Show/Hide Based on Permissions
**File:** `frontend/src/components/layout/Sidebar.tsx`

```typescript
import { useAuthStore } from '@/stores/authStore';

const navigationItems = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: HomeIcon,
    permission: 'dashboard.view'
  },
  {
    name: 'Inventory',
    href: '/inventory',
    icon: PackageIcon,
    permission: 'inventory.view'
  },
  // ... more items
];

export const Sidebar = () => {
  const { hasPermission } = useAuthStore();
  
  return (
    <nav>
      {navigationItems
        .filter(item => !item.permission || hasPermission(item.permission))
        .map(item => (
          <NavLink key={item.href} {...item} />
        ))
      }
    </nav>
  );
};
```

---

### Phase 4: Mobile (Flutter) Integration

#### 4.1 Update Auth Service Response Parsing
**File:** `mobile/flutter_apps/05_tsh_salesperson_app/lib/services/auth_service.dart`

```dart
class LoginResponse {
  final String token;
  final User user;
  
  LoginResponse({required this.token, required this.user});
  
  factory LoginResponse.fromJson(Map<String, dynamic> json) {
    return LoginResponse(
      token: json['token'],
      user: User.fromJson(json['user']),
    );
  }
}

class User {
  final int id;
  final String name;
  final String email;
  final String role;
  final List<Permission> permissions;  // ADD THIS
  final int branchId;
  
  User({
    required this.id,
    required this.name,
    required this.email,
    required this.role,
    required this.permissions,  // ADD THIS
    required this.branchId,
  });
  
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      name: json['name'],
      email: json['email'],
      role: json['role'],
      permissions: (json['permissions'] as List?)
          ?.map((p) => Permission.fromJson(p))
          .toList() ?? [],  // ADD THIS
      branchId: json['branch_id'],
    );
  }
}

class Permission {
  final String name;
  final String description;
  final String resourceType;
  final String permissionType;
  final String source;
  final bool granted;
  
  Permission({
    required this.name,
    required this.description,
    required this.resourceType,
    required this.permissionType,
    required this.source,
    required this.granted,
  });
  
  factory Permission.fromJson(Map<String, dynamic> json) {
    return Permission(
      name: json['name'],
      description: json['description'],
      resourceType: json['resource_type'],
      permissionType: json['permission_type'],
      source: json['source'],
      granted: json['granted'],
    );
  }
}
```

#### 4.2 Create Permission Service for Flutter
**File:** `mobile/flutter_apps/05_tsh_salesperson_app/lib/services/permission_service.dart` (NEW)

```dart
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import '../models/user.dart';

class PermissionService {
  static User? _currentUser;
  
  static Future<void> setCurrentUser(User user) async {
    _currentUser = user;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('current_user', jsonEncode(user.toJson()));
  }
  
  static Future<void> loadCurrentUser() async {
    final prefs = await SharedPreferences.getInstance();
    final userJson = prefs.getString('current_user');
    if (userJson != null) {
      _currentUser = User.fromJson(jsonDecode(userJson));
    }
  }
  
  static bool hasPermission(String permission) {
    if (_currentUser == null) return false;
    
    // Admin gets everything
    if (_currentUser!.role == 'Admin') return true;
    
    // Check specific permission
    return _currentUser!.permissions.any(
      (p) => p.name == permission && p.granted
    );
  }
  
  static bool hasAnyPermission(List<String> permissions) {
    return permissions.any((p) => hasPermission(p));
  }
  
  static bool hasAllPermissions(List<String> permissions) {
    return permissions.every((p) => hasPermission(p));
  }
}
```

#### 4.3 Update Flutter UI with Permission Checks
**Example:** `mobile/flutter_apps/05_tsh_salesperson_app/lib/pages/home_page.dart`

```dart
import '../services/permission_service.dart';

class HomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          // Only show if user has permission
          if (PermissionService.hasPermission('sales.view'))
            SalesSection(),
          
          if (PermissionService.hasPermission('customers.view'))
            CustomersSection(),
          
          // ... more sections
        ],
      ),
    );
  }
}
```

---

### Phase 5: Create Sample Data for Testing

#### 5.1 Create Salesperson Role and User
**Script:** `scripts/setup/create_salesperson_user.py` (NEW)

```python
#!/usr/bin/env python3
"""Create salesperson role and sample salesperson user"""

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

def main():
    db = SessionLocal()
    try:
        # 1. Get or create Salesperson role
        salesperson_role = db.query(Role).filter(Role.name == "Salesperson").first()
        if not salesperson_role:
            salesperson_role = Role(
                name="Salesperson",
                description="Field sales representative",
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(salesperson_role)
            db.flush()
            
            # Grant salesperson permissions
            salesperson_permissions = [
                "dashboard.view",
                "sales.view", "sales.create",
                "customers.view", "customers.create", "customers.update",
                "inventory.view", "items.view", "products.view",
                "finance.transfers.view", "finance.transfers.create",
                "pos.view", "pos.operate"
            ]
            
            for perm_name in salesperson_permissions:
                permission = db.query(Permission).filter(Permission.name == perm_name).first()
                if permission:
                    role_perm = RolePermission(
                        role_id=salesperson_role.id,
                        permission_id=permission.id,
                        granted_by=1,
                        granted_at=datetime.utcnow()
                    )
                    db.add(role_perm)
            
            print(f"✅ Created Salesperson role with {len(salesperson_permissions)} permissions")
        
        # 2. Get main branch
        main_branch = db.query(Branch).filter(Branch.branch_code == "MAIN").first()
        if not main_branch:
            print("❌ Main branch not found. Run init_user_system.py first.")
            return
        
        # 3. Create salesperson user
        existing_user = db.query(User).filter(User.email == "frati@tsh.sale").first()
        if not existing_user:
            salesperson_user = User(
                name="Frati Al-Frati",
                email="frati@tsh.sale",
                password=AuthService.get_password_hash("frati123"),
                role_id=salesperson_role.id,
                branch_id=main_branch.id,
                employee_code="SAL002",
                phone="+964-xxx-0004",
                is_salesperson=True,
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(salesperson_user)
            db.commit()
            print(f"✅ Created salesperson user: frati@tsh.sale (password: frati123)")
        else:
            print("- Salesperson user already exists: frati@tsh.sale")
        
        db.commit()
        print("\n🎉 Salesperson setup complete!")
        print("📱 Test login: frati@tsh.sale / frati123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
```

---

## 🧪 Testing Checklist

### Backend Testing
- [ ] Run permission seeding script
- [ ] Verify all permissions created in database
- [ ] Verify all roles created with correct permissions
- [ ] Test login endpoint returns permissions
- [ ] Test permission decorator blocks unauthorized access
- [ ] Test admin user has full access
- [ ] Test salesperson user has limited access

### Web Frontend Testing
- [ ] Login shows user permissions in auth store
- [ ] Navigation hides items user doesn't have permission for
- [ ] PermissionGuard component works correctly
- [ ] Attempting to access unauthorized route redirects
- [ ] Admin sees all menu items
- [ ] Salesperson sees limited menu items

### Mobile Testing
- [ ] Flutter app parses login response correctly
- [ ] Permissions stored in local storage
- [ ] PermissionService correctly checks permissions
- [ ] UI sections hide based on permissions
- [ ] Salesperson can login with frati@tsh.sale
- [ ] Salesperson sees appropriate features only

---

## 📚 Quick Reference

### Common Permissions
```
- dashboard.view
- inventory.view, inventory.create, inventory.update, inventory.delete
- sales.view, sales.create, sales.update, sales.approve
- customers.view, customers.create, customers.update
- users.view, users.create, users.update, users.delete
- settings.view, settings.update
- reports.view, reports.export
```

### Default Roles
```
Admin          - Full system access
Manager        - Branch/department management
Salesperson    - Field sales operations
Cashier        - POS operations
Accountant     - Financial operations
Inventory Manager - Inventory management
```

### Sample Users
```
admin@tsh-erp.com    / admin123     (Admin)
manager@tsh-erp.com  / manager123   (Manager)
sales@tsh-erp.com    / sales123     (Sales)
frati@tsh.sale       / frati123     (Salesperson)
```

---

## 🚀 Quick Start Commands

```bash
# 1. Setup database and permissions
python scripts/setup/seed_permissions.py
python scripts/setup/init_user_system.py
python scripts/setup/create_salesperson_user.py

# 2. Start backend
cd /Users/khaleelal-mulla/TSH_ERP_System_Local
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Start frontend
cd frontend
npm run dev

# 4. Test Salesperson Flutter app
cd mobile/flutter_apps/05_tsh_salesperson_app
flutter run -d chrome
```

---

## 🔒 Security Best Practices

1. **Never expose all permissions in frontend** - Only send necessary permissions
2. **Always validate permissions on backend** - Frontend checks are for UX only
3. **Use HTTPS in production** - Secure token transmission
4. **Rotate JWT secrets regularly** - Use environment variables
5. **Log all permission checks** - Audit trail for security
6. **Implement rate limiting** - Prevent brute force attacks
7. **Use refresh tokens** - For better security

---

## 📝 Next Steps

1. ✅ Create comprehensive setup script
2. ✅ Update backend auth endpoints
3. ✅ Create permission middleware
4. ✅ Update frontend auth store
5. ✅ Create permission guard components
6. ✅ Update Flutter auth service
7. ✅ Create Flutter permission service
8. ✅ Test end-to-end flow
9. ⏳ Deploy to production

---

**Status:** Ready for Implementation  
**Last Updated:** 2025-01-19  
**Maintained By:** TSH ERP Development Team
