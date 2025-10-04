# 📱 TSH ERP System - Mobile Access Policy

## 🎯 Access Control Policy

### **Web Frontend Access (Restricted)**
✅ **Admin Only** - Full web access
❌ **All Other Users** - Must use mobile apps

### **Mobile App Access (All Users)**
✅ **All Roles** - Can access via mobile apps
✅ **Salesperson** - TSH Salesperson App
✅ **Cashier** - TSH Retail Sales App
✅ **Inventory** - TSH Inventory Management App
✅ **HR** - TSH HR Management App
✅ **Accountant** - TSH Admin Dashboard App (Mobile)
✅ **Manager** - TSH Admin Dashboard App (Mobile)

---

## 🔐 Authentication Endpoints

### **1. Web Login** `/api/auth/login`
- **Allowed**: Admin users only
- **Blocked**: All other roles
- **Response**: 403 Forbidden for non-admin users
- **Message**: "Web access denied. {Role} users must use the mobile application."

### **2. Mobile Login** `/api/auth/login/mobile`
- **Allowed**: All active users
- **Platform**: Mobile apps only
- **Response**: Includes recommended app for user's role

---

## 👥 User Roles & Their Apps

| Role | Web Access | Mobile App | Description |
|------|-----------|------------|-------------|
| **Admin** | ✅ Yes | ✅ Yes | Full web & mobile access |
| **Manager** | ❌ No | ✅ Yes | Admin Dashboard App (Mobile) |
| **Salesperson** | ❌ No | ✅ Yes | TSH Salesperson App |
| **Travel Salesperson** | ❌ No | ✅ Yes | TSH Salesperson App |
| **Cashier** | ❌ No | ✅ Yes | TSH Retail Sales App |
| **Inventory** | ❌ No | ✅ Yes | TSH Inventory Management App |
| **Accountant** | ❌ No | ✅ Yes | Admin Dashboard App (Mobile) |
| **HR** | ❌ No | ✅ Yes | TSH HR Management App |
| **Viewer** | ❌ No | ✅ Yes | Admin Dashboard App (Mobile) |

---

## 📱 Available Mobile Applications

Located in: `/mobile/flutter_apps/`

### **1. TSH Salesperson App** (`05_tsh_salesperson_app`)
**For**: Salesperson, Travel Salesperson
**Features**:
- Customer visits & route planning
- Sales order creation
- Product catalog
- Customer management
- Commission tracking
- GPS location tracking
- Offline mode support

**Launch**:
```bash
cd mobile/flutter_apps/05_tsh_salesperson_app
flutter run
```

### **2. TSH Retail Sales App** (`04_tsh_retail_sales_app`)
**For**: Cashier
**Features**:
- POS operations
- Quick checkout
- Payment processing
- Receipt printing
- Cash register management
- Daily sales reports

**Launch**:
```bash
cd mobile/flutter_apps/04_tsh_retail_sales_app
flutter run
```

### **3. TSH Inventory Management App** (`03_tsh_inventory_app`)
**For**: Inventory Manager
**Features**:
- Stock checking
- Warehouse management
- Stock movements
- Barcode scanning
- Transfer requests
- Stock alerts

**Launch**:
```bash
cd mobile/flutter_apps/03_tsh_inventory_app
flutter run
```

### **4. TSH HR Management App** (`02_tsh_hr_app`)
**For**: HR Staff
**Features**:
- Employee management
- Attendance tracking
- Leave approvals
- Payroll overview
- Employee documents

**Launch**:
```bash
cd mobile/flutter_apps/02_tsh_hr_app
flutter run
```

### **5. TSH Admin Dashboard App** (`01_tsh_admin_app`)
**For**: Admin, Manager, Accountant
**Features**:
- Full system overview
- Reports & analytics
- User management
- System configuration
- Financial overview

**Launch**:
```bash
cd mobile/flutter_apps/01_tsh_admin_app
flutter run
```

---

## 🚀 How Users Access the System

### **For Admin (You)**

1. **Web Access**:
   ```
   URL: http://localhost:5173
   Email: admin@tsh.sale
   Password: admin123
   Status: ✅ ALLOWED
   ```

2. **Mobile Access**:
   ```
   Download: TSH Admin Dashboard App
   Email: admin@tsh.sale
   Password: admin123
   Status: ✅ ALLOWED
   ```

### **For Salesperson (Example: Ayad/frati@tsh.sale)**

1. **Web Access**:
   ```
   URL: http://localhost:5173
   Status: ❌ BLOCKED
   Message: "Web access denied. Travel Salesperson users must use the mobile application."
   ```

2. **Mobile Access**:
   ```
   Download: TSH Salesperson App
   Location: mobile/flutter_apps/05_tsh_salesperson_app
   Email: frati@tsh.sale
   Password: [user's password]
   Status: ✅ ALLOWED
   ```

### **For Other Roles**

All non-admin users follow the same pattern:
- ❌ **Web access blocked**
- ✅ **Mobile access allowed**
- 📱 **Directed to appropriate mobile app**

---

## 🔧 Testing the Access Control

### **Test 1: Admin Login (Web)**
```bash
# Expected: Success
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@tsh.sale","password":"admin123"}'

# Response: 200 OK with token
```

### **Test 2: Salesperson Login (Web)**
```bash
# Expected: Blocked (403)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"frati@tsh.sale","password":"[password]"}'

# Response: 403 Forbidden
# Message: "Web access denied. Travel Salesperson users must use the mobile application."
```

### **Test 3: Salesperson Login (Mobile)**
```bash
# Expected: Success
curl -X POST http://localhost:8000/api/auth/login/mobile \
  -H "Content-Type: application/json" \
  -d '{"email":"frati@tsh.sale","password":"[password]"}'

# Response: 200 OK with token and recommended app
```

---

## 📊 Login Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Attempts Login                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
                   ┌────────────────┐
                   │  Check Role    │
                   └────────────────┘
                            ↓
              ┌─────────────┴─────────────┐
              ↓                           ↓
        ┌──────────┐               ┌──────────────┐
        │  Admin?  │               │  Other Role? │
        └──────────┘               └──────────────┘
              ↓                           ↓
        ✅ ALLOW WEB                  ❌ BLOCK WEB
        ✅ ALLOW MOBILE               ✅ ALLOW MOBILE
              ↓                           ↓
        Dashboard Access          Redirect to Mobile App
```

---

## 💡 Why This Approach?

### **Benefits**

1. **Security**
   - Centralized admin control
   - Reduced web attack surface
   - Better access monitoring

2. **Mobile-First for Field Users**
   - Salespeople work on the move
   - Better mobile experience
   - GPS and offline capabilities
   - Camera for receipts/documents

3. **Performance**
   - Mobile apps optimized for specific roles
   - Lighter weight than web
   - Faster for field operations

4. **User Experience**
   - Each role gets tailored interface
   - No confusion with unused features
   - Role-specific workflows

5. **Management**
   - Easy to track mobile users
   - Better location tracking
   - Simplified permissions

---

## 🔄 Migration Guide

### **Informing Existing Users**

When you create new users or inform existing ones:

**Email Template**:
```
Subject: TSH ERP System - Your Mobile App Access

Hello [Name],

Your account has been created in the TSH ERP System.

IMPORTANT: As a [Role], you will use the mobile application, not the website.

📱 Mobile App: TSH [App Name] App
📧 Email: [user@tsh.sale]
🔑 Password: [temporary password]

📥 Download Location:
The app is available at: /mobile/flutter_apps/[app_folder]/

🚫 Note: Web login is restricted to administrators only.

For support, contact: admin@tsh.sale
```

---

## ⚙️ Configuration

### **To Change Access Policy**

Edit: `/app/routers/auth.py`

**Allow specific roles web access**:
```python
# Current: Only Admin
allowed_web_roles = ['admin']

# Example: Allow Admin and Manager
allowed_web_roles = ['admin', 'manager']

# Update the check:
if role_name.lower() not in allowed_web_roles:
    raise HTTPException(...)
```

### **To Add New Role**

1. Add role in database
2. Add to permission mapping in `get_user_permissions()`
3. Add to mobile app mapping in `get_recommended_mobile_app()`
4. Update this documentation

---

## 📞 Support

### **For Users**
- **Cannot login to web**: This is normal for non-admin users. Use mobile app.
- **Which mobile app**: Check the table above or error message will tell you.
- **App not working**: Contact admin@tsh.sale

### **For Admin**
- **Grant web access**: Only possible by changing user role to Admin
- **Revoke access**: Deactivate user or change role
- **View login attempts**: Check audit logs in admin panel

---

## ✅ Summary

- ✅ **Admin**: Full web + mobile access
- ❌ **All Others**: Mobile only (web blocked)
- 📱 **8 Mobile Apps**: Each optimized for specific roles
- 🔐 **Two Endpoints**: `/login` (web, admin only) and `/login/mobile` (all users)
- 🎯 **Salesperson**: Uses TSH Salesperson App exclusively

**This ensures field users have the best mobile experience while keeping web admin panel secure and admin-only.**

---

**Last Updated**: October 2, 2025
**Version**: 1.0.0
**Policy**: Mobile-First for All Non-Admin Users
