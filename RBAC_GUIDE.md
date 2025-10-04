# 🔐 TSH ERP System - Role-Based Access Control (RBAC) Guide

## 📋 Overview

**YES, it's completely normal** for users with different roles (like "Travel Salesperson") to access the frontend React application with their credentials. The system uses **Role-Based Access Control (RBAC)** to control what each user can see and do.

## 🎯 How It Works

### **Two-Layer Security**

1. **Authentication** (Who are you?)
   - Login with email + password
   - System verifies identity
   - JWT token issued

2. **Authorization** (What can you do?)
   - System checks user's role
   - Filters available features
   - Shows/hides menu items based on permissions

---

## 👥 User Role Access Matrix

### **Travel Salesperson Role**

User: Ayad (frati@tsh.sale)
Role: Travel Salesperson

#### ✅ **CAN ACCESS:**
- ✓ Login to frontend React app
- ✓ Dashboard (limited view)
- ✓ Customers management (create, view, update)
- ✓ Sales orders (create, view, update)
- ✓ Products catalog (view only)
- ✓ Inventory levels (view only)
- ✓ POS system (create transactions)
- ✓ Cash flow tracking (own transactions)
- ✓ Reports (sales reports only)

#### ❌ **CANNOT ACCESS:**
- ✗ User Management
- ✗ System Settings
- ✗ HR Management
- ✗ Financial/Accounting (full access)
- ✗ Purchase Orders
- ✗ Branch Management
- ✗ Warehouse Management (admin level)
- ✗ Delete operations (most)

#### 📱 **PRIMARY ACCESS:**
- **Mobile App Recommended**: Salesperson App (`05_tsh_salesperson_app`)
- **Web Access**: Limited to sales functions
- **Focus**: Customer visits, order taking, route planning

---

## 🔑 Complete Role Permissions Matrix

### **1. Admin (Full Access)**
```
✓ Everything (all modules, all operations)
✓ User Management (CRUD)
✓ System Configuration
✓ All Reports & Analytics
✓ Financial Approvals
```

### **2. Manager**
```
✓ Dashboard (full view)
✓ User Management (view only)
✓ HR Management
✓ Branch & Warehouse Management
✓ Inventory Management
✓ Sales & Purchase
✓ Accounting & Cash Flow
✓ POS System
✓ Reports
✗ System Settings (limited)
✗ User Creation/Deletion
```

### **3. Salesperson / Travel Salesperson**
```
✓ Dashboard (sales-focused)
✓ Customers (CRUD)
✓ Sales Orders (create, view, update)
✓ Products (view)
✓ Inventory (view levels)
✓ POS (transactions)
✓ Cash Flow (own transactions)
✓ Sales Reports
✗ User Management
✗ System Settings
✗ Full Accounting
✗ Purchase Orders
✗ HR Management
✗ Delete Operations
```

**Best Platform**: Mobile App (field sales)

### **4. Cashier**
```
✓ Dashboard (POS-focused)
✓ POS System (create transactions)
✓ Sales Orders (create, view)
✓ Customers (view, basic info)
✓ Products (view)
✓ Cash Handling
✗ User Management
✗ Inventory Management
✗ Accounting
✗ Reports (except shift reports)
```

**Best Platform**: POS Terminal / Retail Sales App

### **5. Inventory Manager**
```
✓ Dashboard (inventory-focused)
✓ Items Management (CRUD)
✓ Products (CRUD)
✓ Inventory (full control)
✓ Warehouses (manage)
✓ Stock Movements
✓ Inventory Reports
✗ User Management
✗ Sales Management
✗ Accounting
✗ HR Management
```

**Best Platform**: Inventory Management App

### **6. Accountant**
```
✓ Dashboard (financial-focused)
✓ Accounting (CRUD)
✓ Cash Flow (full view)
✓ Financial Reports
✓ Sales & Purchase (view)
✓ Invoicing
✗ User Management
✗ Inventory Management
✗ HR Management
✗ System Settings
```

**Best Platform**: Web Dashboard

### **7. HR Manager**
```
✓ Dashboard (HR-focused)
✓ HR Management (CRUD)
✓ Employee Records
✓ Attendance & Leave
✓ Users (view only)
✓ HR Reports
✗ Sales/Purchase
✗ Accounting
✗ Inventory
✗ System Settings
```

**Best Platform**: HR Management App

### **8. Viewer**
```
✓ Dashboard (read-only)
✓ Reports (view only)
✗ Any Create/Update/Delete
✗ User Management
✗ System Settings
```

**Best Platform**: Web Dashboard

---

## 🌐 Access Channels by Role

### **Web Dashboard (React Frontend)**

**Best For:**
- Admin (full control)
- Manager (oversight)
- Accountant (detailed work)
- HR Manager (employee management)
- Viewer (reporting)

**Limited For:**
- Salesperson (can access but limited features)
- Cashier (POS better on dedicated device)
- Inventory (mobile more convenient)

### **Mobile Apps (Flutter)**

**Recommended Apps by Role:**

| Role | Primary Mobile App | Purpose |
|------|-------------------|---------|
| Admin | `01_admin_dashboard` | On-the-go management |
| Manager | `01_admin_dashboard` | Branch oversight |
| Salesperson | `05_salesperson_app` | **PRIMARY - Field sales** |
| Cashier | `04_retail_sales_app` | POS transactions |
| Inventory | `03_inventory_app` | Stock management |
| HR | `02_hr_app` | Employee tracking |

---

## 🔒 Security Implementation

### **Backend (FastAPI)**

```python
# Authentication: Verify user identity
@router.post("/login")
async def login(credentials):
    user = authenticate_user(email, password)
    token = create_jwt_token(user)
    return {
        "token": token,
        "user": user_info,
        "permissions": get_user_permissions(user.role)
    }

# Authorization: Check permissions
@router.get("/users")
@require_permission("users.view")  # Only roles with this permission
async def get_users():
    return users
```

### **Frontend (React)**

```typescript
// Check if user has permission
const { user } = useAuthStore()

// Show/Hide based on role
{user.permissions.includes('users.view') && (
  <MenuItem>User Management</MenuItem>
)}

// Protect routes
<ProtectedRoute 
  requiredPermission="users.view"
  component={UsersPage} 
/>
```

---

## 📱 Travel Salesperson Workflow

### **Typical Day for "Ayad" (Travel Salesperson)**

**Morning:**
1. Open Mobile App (`05_salesperson_app`)
2. Login: `frati@tsh.sale` / password
3. Check route plan for the day
4. View customer list in assigned area

**During Day:**
5. Visit customers (GPS tracking)
6. Take orders on mobile app
7. Check product availability (inventory view)
8. Process payments if needed (POS)
9. Create new customer accounts
10. Update customer information

**Evening:**
11. Submit cash collected
12. Review daily sales report
13. Plan next day's route
14. Sync all data to server

### **What Ayad CAN'T Do:**
- ❌ Access other users' accounts
- ❌ See financial reports (company-wide)
- ❌ Manage inventory (admin level)
- ❌ Create other user accounts
- ❌ Change system settings
- ❌ Delete major records
- ❌ Approve purchases
- ❌ Access HR records

---

## 🎯 Why This Design?

### **Benefits**

1. **Security**
   - Each user sees only what they need
   - Reduces risk of data breaches
   - Prevents accidental mistakes

2. **Simplicity**
   - Salespeople see sales features only
   - No confusion with unnecessary options
   - Focused user interface

3. **Mobile Optimization**
   - Field workers use mobile apps
   - Lightweight, focused features
   - Offline capability (coming soon)

4. **Audit Trail**
   - Track who did what
   - Role-based logging
   - Accountability

5. **Scalability**
   - Easy to add new roles
   - Granular permission control
   - Flexible hierarchy

---

## 🔧 How to Test Role-Based Access

### **Step 1: Login as Admin**
```
URL: http://localhost:5173
Email: admin@tsh.sale
Password: admin123
```
→ You'll see ALL features and modules

### **Step 2: Login as Travel Salesperson**
```
URL: http://localhost:5173
Email: frati@tsh.sale
Password: [their password]
```
→ You'll see LIMITED features:
- Dashboard (sales view)
- Customers
- Sales
- Products (view only)
- Basic reports

### **Step 3: Compare**
- Notice different sidebar menus
- Try accessing User Management as Salesperson (should be blocked)
- Check which buttons are visible/hidden

---

## 📊 Permission Checking Examples

### **Frontend Permission Checks**

```typescript
// In any component
import { useAuthStore } from '@/stores/authStore'

function MyComponent() {
  const { user } = useAuthStore()
  
  // Check single permission
  const canViewUsers = user.permissions.includes('users.view')
  
  // Check role
  const isAdmin = user.role === 'Admin'
  
  // Conditional rendering
  return (
    <div>
      {canViewUsers && <UserManagementLink />}
      {isAdmin && <SystemSettingsLink />}
      
      {/* Everyone sees this */}
      <Dashboard />
    </div>
  )
}
```

### **Backend Permission Checks**

```python
# In route handlers
@router.get("/users")
@require_permission("users.view")
async def get_users(current_user: User = Depends(get_current_user)):
    # Only users with "users.view" permission reach here
    return users

# Custom check
def check_permission(user: User, permission: str) -> bool:
    return permission in get_user_permissions(user)
```

---

## 🆘 Common Questions

### **Q: Can Salesperson see the web dashboard?**
A: Yes, they can login and see a LIMITED dashboard with only sales-related features.

### **Q: Should Salesperson use web or mobile?**
A: **Mobile App is recommended** for field salespeople. Web is backup/office use.

### **Q: Can Salesperson create customers?**
A: Yes! They have `customers.create` permission for field operations.

### **Q: Can Salesperson see all sales?**
A: They can see their own sales and team sales (if configured). Not company-wide.

### **Q: What if Salesperson tries to access Users page?**
A: They won't see it in the menu. If they try direct URL, they'll get "Permission Denied" error.

### **Q: Can roles be customized?**
A: Yes! Admin can modify role permissions from the Permissions page.

### **Q: Can one user have multiple roles?**
A: No, one user = one role. But roles can have overlapping permissions.

### **Q: How to give Salesperson more access?**
A: Admin can:
1. Change their role to "Manager"
2. OR create custom permissions for their user
3. OR modify the "Salesperson" role permissions

---

## 🎊 Summary

**YES, Travel Salesperson can access the React frontend - this is by design!**

✅ **Normal Behavior:**
- Same login system for all users
- Role determines what they see
- Permissions control what they can do

✅ **Security:**
- Backend validates every request
- Frontend hides unauthorized features
- Audit logs track all actions

✅ **Best Practice:**
- Salesperson → Mobile App (primary)
- Web Dashboard → Backup/office use
- Each role sees appropriate interface

**Your system is working correctly! 🎉**

---

**Last Updated**: October 2, 2025  
**System**: TSH ERP v1.0.0  
**Documentation**: Role-Based Access Control
