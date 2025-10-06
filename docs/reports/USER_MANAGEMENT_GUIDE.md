# 🔐 TSH ERP System - Authentication & User Management Guide

## 📋 Table of Contents
1. [Admin Login Credentials](#admin-login-credentials)
2. [User Management Features](#user-management-features)
3. [Permission System](#permission-system)
4. [Mobile App Integration](#mobile-app-integration)
5. [Security Best Practices](#security-best-practices)

---

## 🔑 Admin Login Credentials

### **Owner/Admin Account**
```
📧 Email: admin@tsh.sale
🔑 Password: admin123
👤 Role: Admin (Full System Access)
🏢 Branch: Headquarters - Main Office
```

⚠️ **IMPORTANT**: Please change this password immediately after first login!

### **Access Points**
- **Frontend Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 👥 User Management Features

### **Full CRUD Operations**

As an Admin/Owner, you have complete control over all users:

#### ✅ **Create Users**
- Add new users with custom roles
- Assign to specific branches
- Set employee codes and contact information
- Configure initial permissions

#### 📋 **View All Users**
- See complete user list with pagination
- View user details including:
  - Name and email
  - Role and branch assignment
  - Active status
  - Last login timestamp
  - Employee code
  - Contact information

#### ✏️ **Update Users**
- Modify user information
- Change roles and permissions
- Update branch assignments
- Enable/disable user accounts
- Reset passwords

#### 🗑️ **Delete Users**
- Remove users from the system
- Confirmation required for safety
- Audit log maintained for accountability

---

## 🛡️ Permission System

### **Built-in Roles**

1. **Admin** (Full Access)
   - All system permissions
   - User management
   - System configuration
   - Financial approvals

2. **Manager**
   - Branch management
   - Staff supervision
   - Reporting access
   - Inventory oversight

3. **Salesperson**
   - Sales order creation
   - Customer management
   - Mobile app access
   - Commission tracking

4. **Cashier**
   - POS operations
   - Payment processing
   - Cash handling
   - Shift management

5. **Inventory**
   - Stock management
   - Warehouse operations
   - Stock movements
   - Inventory reports

6. **Accountant**
   - Financial entries
   - Accounting reports
   - Invoice management
   - Payment tracking

7. **HR**
   - Employee management
   - Attendance tracking
   - Leave management
   - Payroll processing

8. **Viewer**
   - Read-only access
   - Dashboard viewing
   - Report access (no export)

### **Permission Types**

Each role can have permissions for:
- `CREATE` - Create new records
- `READ` - View records
- `UPDATE` - Modify existing records
- `DELETE` - Remove records
- `APPROVE` - Approve transactions
- `EXPORT` - Export data
- `IMPORT` - Import data

### **Resources**

Permissions are granted per resource:
- **USER** - User management
- **BRANCH** - Branch management
- **PRODUCT** - Product catalog
- **INVENTORY** - Stock management
- **SALES** - Sales operations
- **CUSTOMER** - Customer management
- **FINANCIAL** - Accounting & finance
- **REPORTS** - Reporting system
- **SETTINGS** - System configuration

---

## 📱 Mobile App Integration

### **Mobile-First Design**

Most users will access the system via mobile applications:

### **Available Mobile Apps**

Located in `/mobile/flutter_apps/`:

1. **Admin Dashboard** (`01_tsh_admin_app`)
   - Full system administration
   - User management on-the-go
   - Quick reports and analytics

2. **HR App** (`02_tsh_hr_app`)
   - Employee management
   - Attendance tracking
   - Leave approvals

3. **Inventory App** (`03_tsh_inventory_app`)
   - Stock checking
   - Warehouse management
   - Stock movements

4. **Retail Sales App** (`04_tsh_retail_sales_app`)
   - POS functionality
   - Quick sales
   - Customer management

5. **Salesperson App** (`05_tsh_salesperson_app`)
   - Route planning
   - Customer visits
   - Order taking
   - Commission tracking

6. **Partner Network App** (`06_tsh_partner_network_app`)
   - Partner management
   - Commission tracking
   - Performance metrics

7. **Wholesale Client App** (`07_tsh_wholesale_client_app`)
   - Wholesale orders
   - Credit management
   - Order history

8. **Consumer App** (`08_tsh_consumer_app`)
   - Retail shopping
   - Product browsing
   - Order tracking

### **Mobile User Management**

When creating users for mobile access:

1. **Set Appropriate Role**
   - Salesperson → `Salesperson` role
   - Store Staff → `Cashier` role
   - Warehouse → `Inventory` role

2. **Enable Mobile Permissions**
   - Check the user's role has mobile access
   - Assign to correct branch
   - Set employee code for tracking

3. **Mobile Login**
   - Users use same credentials as web
   - Email + Password authentication
   - JWT tokens for session management

---

## 🔒 Security Best Practices

### **For Administrators**

1. **Change Default Password**
   ```
   ⚠️ Change admin@tsh.sale password immediately
   Use strong password: min 12 characters, mixed case, numbers, symbols
   ```

2. **User Account Security**
   - Create unique accounts for each user
   - Never share admin credentials
   - Disable inactive accounts
   - Regular password updates

3. **Permission Management**
   - Follow principle of least privilege
   - Grant only necessary permissions
   - Regular permission audits
   - Remove permissions when role changes

4. **Audit Logging**
   - All user actions are logged
   - Review audit logs regularly
   - Monitor suspicious activities
   - Track permission changes

5. **Branch Isolation**
   - Users typically assigned to one branch
   - Cross-branch access requires special permissions
   - Manager approval for branch transfers

### **For Mobile Users**

1. **Device Security**
   - Use device lock screen
   - Keep app updated
   - Don't share devices
   - Logout when done

2. **Network Security**
   - Use secure WiFi
   - Enable VPN if available
   - Avoid public networks for sensitive operations

3. **Password Security**
   - Don't save passwords in browser
   - Use password manager
   - Change periodically
   - Don't share with colleagues

---

## 📊 User Management Workflow

### **Adding a New Employee**

1. **Navigate to User Management**
   - Login as Admin
   - Go to "User Management" from sidebar
   - Click "Add New User" button

2. **Fill User Details**
   ```
   Name: Employee Full Name
   Email: employee@tsh.sale
   Employee Code: EMP001 (unique)
   Phone: +964 XXX XXXX XXX
   Password: Secure initial password
   ```

3. **Assign Role & Branch**
   ```
   Role: Select appropriate role
   Branch: Assign home branch
   Status: Active ✓
   ```

4. **Notify User**
   - Send credentials securely
   - Provide mobile app download link
   - Share first-time login instructions

5. **Verify Access**
   - Test login
   - Confirm permissions working
   - Check mobile app access

### **Managing Existing Users**

1. **View User List**
   - Paginated table with all users
   - Search and filter capabilities
   - Sort by various fields

2. **Edit User**
   - Click edit icon
   - Update any field
   - Change role or branch
   - Save changes

3. **Modify Permissions**
   - Go to Permissions page
   - Select user
   - Grant/revoke specific permissions
   - Override role permissions if needed

4. **Deactivate User**
   - Edit user
   - Uncheck "Active" status
   - User cannot login but data preserved
   - Can reactivate later

5. **Delete User**
   - Use with caution (permanent)
   - Confirmation required
   - Audit log maintained
   - Consider deactivation instead

---

## 🎯 Quick Start Guide

### **For Admin/Owner (First Time)**

1. **Login to System**
   ```bash
   URL: http://localhost:5173
   Email: admin@tsh.sale
   Password: admin123
   ```

2. **Change Admin Password**
   - Go to Profile/Settings
   - Change password to secure one
   - Save changes

3. **Add Your First User**
   - Navigate to User Management
   - Click "Add New User"
   - Fill in details
   - Assign appropriate role
   - Save user

4. **Configure Mobile Access**
   - Ensure user has correct role
   - Share mobile app download link
   - Provide login credentials
   - Test mobile login

5. **Monitor System**
   - Check Dashboard regularly
   - Review user activity
   - Monitor sales/inventory
   - Check audit logs

---

## 🆘 Support & Troubleshooting

### **Common Issues**

**Cannot Login**
- Verify credentials are correct
- Check account is active
- Ensure network connectivity
- Try password reset

**Permission Denied**
- Check user role
- Verify specific permissions
- Contact administrator
- Review audit logs

**Mobile App Issues**
- Update to latest version
- Check internet connection
- Verify credentials
- Re-download if needed

### **Contact Information**

For technical support:
- **Email**: support@tsh.sale
- **System Admin**: admin@tsh.sale

---

## 📈 System Statistics

Current system includes:
- ✅ 1 Admin account configured
- ✅ 7 user roles available
- ✅ 60+ permission types
- ✅ 8 mobile applications
- ✅ Multi-branch support
- ✅ Audit logging enabled
- ✅ JWT authentication
- ✅ Role-based access control

---

**Last Updated**: October 2, 2025
**Version**: 1.0.0
**System**: TSH ERP System
