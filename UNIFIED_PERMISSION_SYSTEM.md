# 🔐 TSH ERP System - Unified Authentication & Permission System

## 📋 **COMPLETE SYSTEM OVERVIEW**

This document provides the **systematic right way** to enable roles, users, and permissions integration across the entire TSH ERP System - unifying all features and data across web, mobile, and API platforms.

---

## 🎯 **CURRENT SYSTEM ARCHITECTURE**

### **1. Platform-Based Access Control**

```
┌─────────────────────────────────────────────────────────────┐
│                    TSH ERP SYSTEM                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐        ┌──────────────┐                 │
│  │   WEB APP    │        │  MOBILE APPS │                 │
│  │ (React/Vite) │        │   (Flutter)  │                 │
│  └──────────────┘        └──────────────┘                 │
│         │                        │                         │
│         │                        │                         │
│    /auth/login             /auth/login/mobile             │
│  (Admin Only)              (All Roles)                     │
│         │                        │                         │
│         └────────────┬───────────┘                         │
│                      │                                     │
│              ┌───────▼───────┐                            │
│              │  BACKEND API  │                            │
│              │   (FastAPI)   │                            │
│              └───────────────┘                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### **2. Role-Based Permission System**

| Role | Web Access | Mobile App | Permissions |
|------|-----------|------------|-------------|
| **Admin** | ✅ Full | ✅ Admin App | All permissions |
| **Manager** | ❌ Blocked | ✅ Manager App | Dashboard, Users, HR, Sales, Reports |
| **Salesperson** | ❌ Blocked | ✅ Salesperson App | Customers, Sales, Products (view only) |
| **Accountant** | ❌ Blocked | ✅ Accountant App | Accounting, Financial, Reports |
| **Inventory Manager** | ❌ Blocked | ✅ Inventory App | Inventory, Products, Warehouses |

---

## 🚨 **YOUR CURRENT ISSUE**

### **Problem:**
You're trying to login as a salesperson (`frati@tsh.sale`) in the **Flutter Salesperson App**, but getting authentication error.

### **Root Cause:**
The salesperson app login response format doesn't match what the backend returns.

### **Backend Returns:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "Frati Salesperson",
    "email": "frati@tsh.sale",
    "role": "Salesperson",
    "permissions": [...]
  }
}
```

### **Flutter App Expects:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "user": {...}
  }
}
```

---

## ✅ **SOLUTION: FIX FLUTTER APP AUTH SERVICE**

### **File to Fix:**
`mobile/flutter_apps/05_tsh_salesperson_app/lib/services/auth_service.dart`

### **Current Code (WRONG):**
```dart
if (data['success'] == true && data['data'] != null) {
  final authData = data['data'];
  final token = authData['access_token'];
  final userInfo = authData['user'];
  // ...
}
```

### **Fixed Code (CORRECT):**
```dart
// Backend returns direct response, not wrapped in success/data
final token = data['access_token'];
final userInfo = data['user'];

if (token != null && userInfo != null) {
  await _saveTokenAndUser(token, userInfo);
  return AuthModel.fromJson(userInfo);
}
```

---

## 🔧 **COMPLETE FIX IMPLEMENTATION**

Let me fix the auth service for you...

---

## 📊 **UNIFIED PERMISSION MATRIX**

### **Admin Permissions**
```python
[
    'admin',                    # Full system access
    'dashboard.view',           # View dashboard
    'users.view',              # View users
    'users.create',            # Create users
    'users.update',            # Update users
    'users.delete',            # Delete users
    'hr.view',                 # View HR
    'branches.view',           # View branches
    'warehouses.view',         # View warehouses
    'items.view',              # View items
    'products.view',           # View products
    'inventory.view',          # View inventory
    'customers.view',          # View customers
    'vendors.view',            # View vendors
    'sales.view',              # View sales
    'sales.create',            # Create sales
    'purchase.view',           # View purchases
    'accounting.view',         # View accounting
    'pos.view',                # View POS
    'cashflow.view',           # View cash flow
    'migration.view',          # View migrations
    'reports.view',            # View reports
    'settings.view'            # View settings
]
```

### **Salesperson Permissions**
```python
[
    'dashboard.view',          # View dashboard
    'customers.view',          # View customers
    'customers.create',        # Create customers
    'customers.update',        # Update customers
    'sales.view',              # View sales
    'sales.create',            # Create sales
    'sales.update',            # Update sales
    'products.view',           # View products (read-only)
    'inventory.view',          # View inventory (read-only)
    'reports.own'              # View own reports
]
```

---

## 🔐 **AUTHENTICATION FLOW**

### **Web Login (Admin Only)**
```
1. User opens: http://localhost:5173/login
2. Enters: admin@tsh.com / admin123
3. Frontend sends: POST /api/auth/login
4. Backend checks: role == 'Admin'
5. If Admin: ✅ Grant access + JWT token
6. If NOT Admin: ❌ 403 Error "Web access denied. Use mobile app."
```

### **Mobile Login (All Roles)**
```
1. User opens: TSH Salesperson App
2. Enters: frati@tsh.sale / password
3. App sends: POST /api/auth/login/mobile
4. Backend checks: user is_active == True
5. If Active: ✅ Grant access + JWT token
6. Return: user data + permissions
```

---

## 📱 **MOBILE APPS STRUCTURE**

```
mobile/flutter_apps/
├── 01_tsh_admin_app/          → Admin (full system access)
├── 02_tsh_manager_app/         → Manager (oversight & reports)
├── 03_tsh_accountant_app/      → Accountant (financial management)
├── 04_tsh_inventory_app/       → Inventory Manager (stock management)
├── 05_tsh_salesperson_app/     → Salesperson (sales & customers) ⬅️ YOUR APP
└── shared/
    └── tsh_core_package/       → Shared utilities & services
```

---

## 🎯 **SYSTEMATIC STEPS TO FIX YOUR ISSUE**

### **Step 1: Fix Flutter Auth Service**
Update the login response parsing to match backend format.

### **Step 2: Verify User Exists**
Check that `frati@tsh.sale` user exists with Salesperson role.

### **Step 3: Test Login**
Try logging in with correct credentials.

### **Step 4: Check Permissions**
Verify user has correct permissions for their role.

---

## 🔧 **HOW TO VERIFY USERS IN DATABASE**

### **Option 1: Backend API**
```bash
# Get all users
curl http://localhost:8000/api/users \
  -H "Authorization: Bearer <admin_token>"

# Get specific user
curl http://localhost:8000/api/users/1 \
  -H "Authorization: Bearer <admin_token>"
```

### **Option 2: Direct Database Query**
```python
# Run in Python console
from app.db.database import SessionLocal
from app.models.user import User

db = SessionLocal()
users = db.query(User).all()
for user in users:
    print(f"{user.email} - {user.role.name if user.role else 'No Role'}")
```

---

## 📝 **TEST CREDENTIALS**

Based on your system, these should work:

| Email | Password | Role | Platform |
|-------|----------|------|----------|
| admin@tsh.com | admin123 | Admin | Web + Mobile |
| frati@tsh.sale | (your password) | Salesperson | Mobile Only |

---

## 🚀 **NEXT STEPS**

1. **I'll fix the Flutter auth service now**
2. **Verify your user credentials**
3. **Test login again**
4. **If still fails, we'll check database**

---

Let me implement the fix...
