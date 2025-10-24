"""
Comprehensive Permission Seeder for TSH ERP System
This script creates a well-organized, detailed permission structure
"""

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.permissions import Permission, ModuleType, ActionType
from datetime import datetime


def get_comprehensive_permissions():
    """
    Define all permissions organized by module and action
    Format: {
        'code': 'unique.permission.code',
        'name': 'Human Readable Name',
        'description': 'Detailed description',
        'module': ModuleType.MODULE_NAME,
        'action': ActionType.ACTION_NAME,
        'category': 'subcategory',  # optional
        'display_order': 0  # for UI ordering
    }
    """

    permissions = []
    order = 0

    # ============================================================
    # 1. APPLICATION ACCESS PERMISSIONS (NEW!)
    # ============================================================
    app_access_perms = [
        {
            'code': 'app.web_admin.access',
            'name': 'Access Web Admin Panel',
            'description': 'Can access the web-based administration panel',
            'module': ModuleType.APPLICATION_ACCESS,
            'action': ActionType.VIEW,
            'category': 'web_applications',
            'display_order': order := order + 1
        },
        {
            'code': 'app.mobile_salesperson.access',
            'name': 'Access Mobile Salesperson App',
            'description': 'Can access the mobile salesperson application',
            'module': ModuleType.APPLICATION_ACCESS,
            'action': ActionType.VIEW,
            'category': 'mobile_applications',
            'display_order': order := order + 1
        },
        {
            'code': 'app.admin_security.access',
            'name': 'Access Admin Security App',
            'description': 'Can access the admin security & permissions management app',
            'module': ModuleType.APPLICATION_ACCESS,
            'action': ActionType.VIEW,
            'category': 'admin_applications',
            'display_order': order := order + 1
        },
        {
            'code': 'app.pos.access',
            'name': 'Access POS System',
            'description': 'Can access the point of sale system',
            'module': ModuleType.APPLICATION_ACCESS,
            'action': ActionType.VIEW,
            'category': 'pos_applications',
            'display_order': order := order + 1
        },
        {
            'code': 'app.warehouse.access',
            'name': 'Access Warehouse App',
            'description': 'Can access the warehouse management application',
            'module': ModuleType.APPLICATION_ACCESS,
            'action': ActionType.VIEW,
            'category': 'warehouse_applications',
            'display_order': order := order + 1
        },
    ]
    permissions.extend(app_access_perms)

    # ============================================================
    # 2. USER MANAGEMENT PERMISSIONS
    # ============================================================
    user_actions = [
        {'action': ActionType.VIEW, 'name_suffix': 'View', 'desc_suffix': 'view and list'},
        {'action': ActionType.CREATE, 'name_suffix': 'Create', 'desc_suffix': 'create new'},
        {'action': ActionType.UPDATE, 'name_suffix': 'Update', 'desc_suffix': 'edit and update'},
        {'action': ActionType.DELETE, 'name_suffix': 'Delete', 'desc_suffix': 'delete'},
        {'action': ActionType.EXPORT, 'name_suffix': 'Export', 'desc_suffix': 'export data of'},
    ]

    for action_def in user_actions:
        permissions.append({
            'code': f'user.{action_def["action"].value}',
            'name': f'{action_def["name_suffix"]} Users',
            'description': f'Can {action_def["desc_suffix"]} users',
            'module': ModuleType.USER_MANAGEMENT,
            'action': action_def['action'],
            'category': 'users',
            'display_order': order := order + 1
        })

    # Additional user-specific permissions
    permissions.extend([
        {
            'code': 'user.reset_password',
            'name': 'Reset User Password',
            'description': 'Can reset passwords for other users',
            'module': ModuleType.USER_MANAGEMENT,
            'action': ActionType.UPDATE,
            'category': 'users',
            'display_order': order := order + 1
        },
        {
            'code': 'user.activate_deactivate',
            'name': 'Activate/Deactivate Users',
            'description': 'Can activate or deactivate user accounts',
            'module': ModuleType.USER_MANAGEMENT,
            'action': ActionType.UPDATE,
            'category': 'users',
            'display_order': order := order + 1
        },
    ])

    # ============================================================
    # 3. ROLE & PERMISSION MANAGEMENT
    # ============================================================
    role_perms = [
        {
            'code': 'role.view',
            'name': 'View Roles',
            'description': 'Can view and list all roles',
            'module': ModuleType.ROLE_PERMISSION,
            'action': ActionType.VIEW,
            'category': 'roles',
            'display_order': order := order + 1
        },
        {
            'code': 'role.create',
            'name': 'Create Roles',
            'description': 'Can create new roles',
            'module': ModuleType.ROLE_PERMISSION,
            'action': ActionType.CREATE,
            'category': 'roles',
            'display_order': order := order + 1
        },
        {
            'code': 'role.update',
            'name': 'Update Roles',
            'description': 'Can edit and update roles',
            'module': ModuleType.ROLE_PERMISSION,
            'action': ActionType.UPDATE,
            'category': 'roles',
            'display_order': order := order + 1
        },
        {
            'code': 'role.delete',
            'name': 'Delete Roles',
            'description': 'Can delete roles',
            'module': ModuleType.ROLE_PERMISSION,
            'action': ActionType.DELETE,
            'category': 'roles',
            'display_order': order := order + 1
        },
        {
            'code': 'permission.view',
            'name': 'View Permissions',
            'description': 'Can view all available permissions',
            'module': ModuleType.ROLE_PERMISSION,
            'action': ActionType.VIEW,
            'category': 'permissions',
            'display_order': order := order + 1
        },
        {
            'code': 'permission.assign',
            'name': 'Assign Permissions',
            'description': 'Can assign permissions to roles and users',
            'module': ModuleType.ROLE_PERMISSION,
            'action': ActionType.UPDATE,
            'category': 'permissions',
            'display_order': order := order + 1
        },
        {
            'code': 'permission.revoke',
            'name': 'Revoke Permissions',
            'description': 'Can revoke permissions from roles and users',
            'module': ModuleType.ROLE_PERMISSION,
            'action': ActionType.DELETE,
            'category': 'permissions',
            'display_order': order := order + 1
        },
    ]
    permissions.extend(role_perms)

    # ============================================================
    # 4. BRANCH MANAGEMENT PERMISSIONS
    # ============================================================
    branch_actions = [
        {'action': ActionType.VIEW, 'name_suffix': 'View', 'desc_suffix': 'view and list'},
        {'action': ActionType.CREATE, 'name_suffix': 'Create', 'desc_suffix': 'create new'},
        {'action': ActionType.UPDATE, 'name_suffix': 'Update', 'desc_suffix': 'edit and update'},
        {'action': ActionType.DELETE, 'name_suffix': 'Delete', 'desc_suffix': 'delete'},
        {'action': ActionType.EXPORT, 'name_suffix': 'Export', 'desc_suffix': 'export data of'},
    ]

    for action_def in branch_actions:
        permissions.append({
            'code': f'branch.{action_def["action"].value}',
            'name': f'{action_def["name_suffix"]} Branches',
            'description': f'Can {action_def["desc_suffix"]} branches',
            'module': ModuleType.BRANCH_MANAGEMENT,
            'action': action_def['action'],
            'category': 'branches',
            'display_order': order := order + 1
        })

    # ============================================================
    # 5. INVENTORY MANAGEMENT PERMISSIONS
    # ============================================================

    # Products
    product_actions = [
        {'action': ActionType.VIEW, 'name_suffix': 'View', 'desc_suffix': 'view and search'},
        {'action': ActionType.CREATE, 'name_suffix': 'Create', 'desc_suffix': 'create new'},
        {'action': ActionType.UPDATE, 'name_suffix': 'Update', 'desc_suffix': 'edit and update'},
        {'action': ActionType.DELETE, 'name_suffix': 'Delete', 'desc_suffix': 'delete'},
        {'action': ActionType.IMPORT, 'name_suffix': 'Import', 'desc_suffix': 'import'},
        {'action': ActionType.EXPORT, 'name_suffix': 'Export', 'desc_suffix': 'export'},
        {'action': ActionType.PRINT, 'name_suffix': 'Print', 'desc_suffix': 'print'},
    ]

    for action_def in product_actions:
        permissions.append({
            'code': f'inventory.product.{action_def["action"].value}',
            'name': f'{action_def["name_suffix"]} Products',
            'description': f'Can {action_def["desc_suffix"]} products',
            'module': ModuleType.INVENTORY,
            'action': action_def['action'],
            'category': 'products',
            'display_order': order := order + 1
        })

    # Stock Management
    stock_perms = [
        {
            'code': 'inventory.stock.view',
            'name': 'View Stock Levels',
            'description': 'Can view stock levels and inventory quantities',
            'module': ModuleType.INVENTORY,
            'action': ActionType.VIEW,
            'category': 'stock',
            'display_order': order := order + 1
        },
        {
            'code': 'inventory.stock.adjust',
            'name': 'Adjust Stock',
            'description': 'Can adjust stock levels manually',
            'module': ModuleType.INVENTORY,
            'action': ActionType.UPDATE,
            'category': 'stock',
            'display_order': order := order + 1
        },
        {
            'code': 'inventory.stock.transfer',
            'name': 'Transfer Stock',
            'description': 'Can create and manage stock transfers between branches',
            'module': ModuleType.INVENTORY,
            'action': ActionType.CREATE,
            'category': 'stock',
            'display_order': order := order + 1
        },
        {
            'code': 'inventory.stock.approve',
            'name': 'Approve Stock Adjustments',
            'description': 'Can approve stock adjustment requests',
            'module': ModuleType.INVENTORY,
            'action': ActionType.APPROVE,
            'category': 'stock',
            'display_order': order := order + 1
        },
    ]
    permissions.extend(stock_perms)

    # Warehouses
    warehouse_actions = [
        {'action': ActionType.VIEW, 'name_suffix': 'View', 'desc_suffix': 'view'},
        {'action': ActionType.CREATE, 'name_suffix': 'Create', 'desc_suffix': 'create'},
        {'action': ActionType.UPDATE, 'name_suffix': 'Update', 'desc_suffix': 'update'},
        {'action': ActionType.DELETE, 'name_suffix': 'Delete', 'desc_suffix': 'delete'},
    ]

    for action_def in warehouse_actions:
        permissions.append({
            'code': f'inventory.warehouse.{action_def["action"].value}',
            'name': f'{action_def["name_suffix"]} Warehouses',
            'description': f'Can {action_def["desc_suffix"]} warehouses',
            'module': ModuleType.INVENTORY,
            'action': action_def['action'],
            'category': 'warehouses',
            'display_order': order := order + 1
        })

    # ============================================================
    # 6. SALES MANAGEMENT PERMISSIONS
    # ============================================================

    # Sales Orders
    order_actions = [
        {'action': ActionType.VIEW, 'name_suffix': 'View', 'desc_suffix': 'view'},
        {'action': ActionType.CREATE, 'name_suffix': 'Create', 'desc_suffix': 'create'},
        {'action': ActionType.UPDATE, 'name_suffix': 'Update', 'desc_suffix': 'update'},
        {'action': ActionType.DELETE, 'name_suffix': 'Delete', 'desc_suffix': 'delete'},
        {'action': ActionType.APPROVE, 'name_suffix': 'Approve', 'desc_suffix': 'approve'},
        {'action': ActionType.PRINT, 'name_suffix': 'Print', 'desc_suffix': 'print'},
        {'action': ActionType.EXPORT, 'name_suffix': 'Export', 'desc_suffix': 'export'},
    ]

    for action_def in order_actions:
        permissions.append({
            'code': f'sales.order.{action_def["action"].value}',
            'name': f'{action_def["name_suffix"]} Sales Orders',
            'description': f'Can {action_def["desc_suffix"]} sales orders',
            'module': ModuleType.SALES,
            'action': action_def['action'],
            'category': 'orders',
            'display_order': order := order + 1
        })

    # Quotations
    quote_actions = [
        {'action': ActionType.VIEW, 'name_suffix': 'View', 'desc_suffix': 'view'},
        {'action': ActionType.CREATE, 'name_suffix': 'Create', 'desc_suffix': 'create'},
        {'action': ActionType.UPDATE, 'name_suffix': 'Update', 'desc_suffix': 'update'},
        {'action': ActionType.DELETE, 'name_suffix': 'Delete', 'desc_suffix': 'delete'},
        {'action': ActionType.APPROVE, 'name_suffix': 'Approve', 'desc_suffix': 'approve'},
    ]

    for action_def in quote_actions:
        permissions.append({
            'code': f'sales.quotation.{action_def["action"].value}',
            'name': f'{action_def["name_suffix"]} Quotations',
            'description': f'Can {action_def["desc_suffix"]} sales quotations',
            'module': ModuleType.SALES,
            'action': action_def['action'],
            'category': 'quotations',
            'display_order': order := order + 1
        })

    # Invoices
    invoice_perms = [
        {
            'code': 'sales.invoice.view',
            'name': 'View Invoices',
            'description': 'Can view sales invoices',
            'module': ModuleType.SALES,
            'action': ActionType.VIEW,
            'category': 'invoices',
            'display_order': order := order + 1
        },
        {
            'code': 'sales.invoice.create',
            'name': 'Create Invoices',
            'description': 'Can create sales invoices',
            'module': ModuleType.SALES,
            'action': ActionType.CREATE,
            'category': 'invoices',
            'display_order': order := order + 1
        },
        {
            'code': 'sales.invoice.print',
            'name': 'Print Invoices',
            'description': 'Can print sales invoices',
            'module': ModuleType.SALES,
            'action': ActionType.PRINT,
            'category': 'invoices',
            'display_order': order := order + 1
        },
    ]
    permissions.extend(invoice_perms)

    # ============================================================
    # 7. PURCHASING MANAGEMENT PERMISSIONS
    # ============================================================

    # Purchase Orders
    po_actions = [
        {'action': ActionType.VIEW, 'name_suffix': 'View', 'desc_suffix': 'view'},
        {'action': ActionType.CREATE, 'name_suffix': 'Create', 'desc_suffix': 'create'},
        {'action': ActionType.UPDATE, 'name_suffix': 'Update', 'desc_suffix': 'update'},
        {'action': ActionType.DELETE, 'name_suffix': 'Delete', 'desc_suffix': 'delete'},
        {'action': ActionType.APPROVE, 'name_suffix': 'Approve', 'desc_suffix': 'approve'},
    ]

    for action_def in po_actions:
        permissions.append({
            'code': f'purchasing.po.{action_def["action"].value}',
            'name': f'{action_def["name_suffix"]} Purchase Orders',
            'description': f'Can {action_def["desc_suffix"]} purchase orders',
            'module': ModuleType.PURCHASING,
            'action': action_def['action'],
            'category': 'purchase_orders',
            'display_order': order := order + 1
        })

    # Suppliers
    supplier_actions = [
        {'action': ActionType.VIEW, 'name_suffix': 'View', 'desc_suffix': 'view'},
        {'action': ActionType.CREATE, 'name_suffix': 'Create', 'desc_suffix': 'create'},
        {'action': ActionType.UPDATE, 'name_suffix': 'Update', 'desc_suffix': 'update'},
        {'action': ActionType.DELETE, 'name_suffix': 'Delete', 'desc_suffix': 'delete'},
    ]

    for action_def in supplier_actions:
        permissions.append({
            'code': f'purchasing.supplier.{action_def["action"].value}',
            'name': f'{action_def["name_suffix"]} Suppliers',
            'description': f'Can {action_def["desc_suffix"]} suppliers',
            'module': ModuleType.PURCHASING,
            'action': action_def['action'],
            'category': 'suppliers',
            'display_order': order := order + 1
        })

    # ============================================================
    # 8. FINANCIAL MANAGEMENT PERMISSIONS
    # ============================================================

    # Payments
    payment_perms = [
        {
            'code': 'financial.payment.view',
            'name': 'View Payments',
            'description': 'Can view payment transactions',
            'module': ModuleType.FINANCIAL,
            'action': ActionType.VIEW,
            'category': 'payments',
            'display_order': order := order + 1
        },
        {
            'code': 'financial.payment.create',
            'name': 'Create Payments',
            'description': 'Can create payment transactions',
            'module': ModuleType.FINANCIAL,
            'action': ActionType.CREATE,
            'category': 'payments',
            'display_order': order := order + 1
        },
        {
            'code': 'financial.payment.approve',
            'name': 'Approve Payments',
            'description': 'Can approve payment transactions',
            'module': ModuleType.FINANCIAL,
            'action': ActionType.APPROVE,
            'category': 'payments',
            'display_order': order := order + 1
        },
        {
            'code': 'financial.payment.reject',
            'name': 'Reject Payments',
            'description': 'Can reject payment transactions',
            'module': ModuleType.FINANCIAL,
            'action': ActionType.REJECT,
            'category': 'payments',
            'display_order': order := order + 1
        },
    ]
    permissions.extend(payment_perms)

    # Accounting
    accounting_perms = [
        {
            'code': 'financial.account.view',
            'name': 'View Accounts',
            'description': 'Can view accounting information',
            'module': ModuleType.FINANCIAL,
            'action': ActionType.VIEW,
            'category': 'accounting',
            'display_order': order := order + 1
        },
        {
            'code': 'financial.transaction.view',
            'name': 'View Transactions',
            'description': 'Can view financial transactions',
            'module': ModuleType.FINANCIAL,
            'action': ActionType.VIEW,
            'category': 'transactions',
            'display_order': order := order + 1
        },
        {
            'code': 'financial.transaction.create',
            'name': 'Create Transactions',
            'description': 'Can create financial transactions',
            'module': ModuleType.FINANCIAL,
            'action': ActionType.CREATE,
            'category': 'transactions',
            'display_order': order := order + 1
        },
    ]
    permissions.extend(accounting_perms)

    # ============================================================
    # 9. CUSTOMER MANAGEMENT PERMISSIONS
    # ============================================================

    customer_actions = [
        {'action': ActionType.VIEW, 'name_suffix': 'View', 'desc_suffix': 'view'},
        {'action': ActionType.CREATE, 'name_suffix': 'Create', 'desc_suffix': 'create'},
        {'action': ActionType.UPDATE, 'name_suffix': 'Update', 'desc_suffix': 'update'},
        {'action': ActionType.DELETE, 'name_suffix': 'Delete', 'desc_suffix': 'delete'},
        {'action': ActionType.EXPORT, 'name_suffix': 'Export', 'desc_suffix': 'export'},
        {'action': ActionType.IMPORT, 'name_suffix': 'Import', 'desc_suffix': 'import'},
    ]

    for action_def in customer_actions:
        permissions.append({
            'code': f'customer.{action_def["action"].value}',
            'name': f'{action_def["name_suffix"]} Customers',
            'description': f'Can {action_def["desc_suffix"]} customers',
            'module': ModuleType.CUSTOMER,
            'action': action_def['action'],
            'category': 'customers',
            'display_order': order := order + 1
        })

    # ============================================================
    # 10. EMPLOYEE MANAGEMENT PERMISSIONS
    # ============================================================

    employee_actions = [
        {'action': ActionType.VIEW, 'name_suffix': 'View', 'desc_suffix': 'view'},
        {'action': ActionType.CREATE, 'name_suffix': 'Create', 'desc_suffix': 'create'},
        {'action': ActionType.UPDATE, 'name_suffix': 'Update', 'desc_suffix': 'update'},
        {'action': ActionType.DELETE, 'name_suffix': 'Delete', 'desc_suffix': 'delete'},
    ]

    for action_def in employee_actions:
        permissions.append({
            'code': f'employee.{action_def["action"].value}',
            'name': f'{action_def["name_suffix"]} Employees',
            'description': f'Can {action_def["desc_suffix"]} employees',
            'module': ModuleType.EMPLOYEE,
            'action': action_def['action'],
            'category': 'employees',
            'display_order': order := order + 1
        })

    # ============================================================
    # 11. REPORTS & ANALYTICS PERMISSIONS
    # ============================================================

    report_types = [
        ('sales', 'Sales Reports'),
        ('inventory', 'Inventory Reports'),
        ('financial', 'Financial Reports'),
        ('customer', 'Customer Reports'),
        ('employee', 'Employee Reports'),
    ]

    for report_code, report_name in report_types:
        permissions.extend([
            {
                'code': f'reports.{report_code}.view',
                'name': f'View {report_name}',
                'description': f'Can view {report_name.lower()}',
                'module': ModuleType.REPORTS,
                'action': ActionType.VIEW,
                'category': report_code,
                'display_order': order := order + 1
            },
            {
                'code': f'reports.{report_code}.export',
                'name': f'Export {report_name}',
                'description': f'Can export {report_name.lower()}',
                'module': ModuleType.REPORTS,
                'action': ActionType.EXPORT,
                'category': report_code,
                'display_order': order := order + 1
            },
        ])

    # Analytics
    analytics_perms = [
        {
            'code': 'analytics.dashboard.view',
            'name': 'View Dashboard Analytics',
            'description': 'Can view analytics dashboards',
            'module': ModuleType.ANALYTICS,
            'action': ActionType.VIEW,
            'category': 'dashboards',
            'display_order': order := order + 1
        },
        {
            'code': 'analytics.kpi.view',
            'name': 'View KPIs',
            'description': 'Can view key performance indicators',
            'module': ModuleType.ANALYTICS,
            'action': ActionType.VIEW,
            'category': 'kpi',
            'display_order': order := order + 1
        },
    ]
    permissions.extend(analytics_perms)

    # ============================================================
    # 12. SETTINGS & CONFIGURATION PERMISSIONS
    # ============================================================

    settings_perms = [
        {
            'code': 'settings.system.view',
            'name': 'View System Settings',
            'description': 'Can view system configuration settings',
            'module': ModuleType.SETTINGS,
            'action': ActionType.VIEW,
            'category': 'system',
            'display_order': order := order + 1
        },
        {
            'code': 'settings.system.update',
            'name': 'Update System Settings',
            'description': 'Can update system configuration settings',
            'module': ModuleType.SETTINGS,
            'action': ActionType.UPDATE,
            'category': 'system',
            'display_order': order := order + 1
        },
        {
            'code': 'settings.company.view',
            'name': 'View Company Settings',
            'description': 'Can view company information settings',
            'module': ModuleType.SETTINGS,
            'action': ActionType.VIEW,
            'category': 'company',
            'display_order': order := order + 1
        },
        {
            'code': 'settings.company.update',
            'name': 'Update Company Settings',
            'description': 'Can update company information settings',
            'module': ModuleType.SETTINGS,
            'action': ActionType.UPDATE,
            'category': 'company',
            'display_order': order := order + 1
        },
    ]
    permissions.extend(settings_perms)

    # ============================================================
    # 13. AUDIT & SECURITY PERMISSIONS
    # ============================================================

    audit_perms = [
        {
            'code': 'audit.logs.view',
            'name': 'View Audit Logs',
            'description': 'Can view system audit logs',
            'module': ModuleType.AUDIT,
            'action': ActionType.VIEW,
            'category': 'logs',
            'display_order': order := order + 1
        },
        {
            'code': 'audit.logs.export',
            'name': 'Export Audit Logs',
            'description': 'Can export audit logs',
            'module': ModuleType.AUDIT,
            'action': ActionType.EXPORT,
            'category': 'logs',
            'display_order': order := order + 1
        },
        {
            'code': 'audit.security_events.view',
            'name': 'View Security Events',
            'description': 'Can view security events and alerts',
            'module': ModuleType.AUDIT,
            'action': ActionType.VIEW,
            'category': 'security',
            'display_order': order := order + 1
        },
    ]
    permissions.extend(audit_perms)

    return permissions


def seed_permissions(db: Session):
    """Seed all permissions into the database"""

    print("🌱 Starting permission seeding...")

    permissions_data = get_comprehensive_permissions()

    created_count = 0
    updated_count = 0
    skipped_count = 0

    for perm_data in permissions_data:
        # Check if permission already exists
        existing_perm = db.query(Permission).filter(Permission.code == perm_data['code']).first()

        if existing_perm:
            # Update existing permission
            existing_perm.name = perm_data['name']
            existing_perm.description = perm_data['description']
            existing_perm.module = perm_data['module']
            existing_perm.action = perm_data['action']
            existing_perm.category = perm_data.get('category')
            existing_perm.display_order = perm_data.get('display_order', 0)
            existing_perm.updated_at = datetime.utcnow()
            updated_count += 1
        else:
            # Create new permission
            new_perm = Permission(
                code=perm_data['code'],
                name=perm_data['name'],
                description=perm_data['description'],
                module=perm_data['module'],
                action=perm_data['action'],
                category=perm_data.get('category'),
                display_order=perm_data.get('display_order', 0),
                is_active=True
            )
            db.add(new_perm)
            created_count += 1

    db.commit()

    print(f"✅ Permission seeding completed!")
    print(f"   - Created: {created_count}")
    print(f"   - Updated: {updated_count}")
    print(f"   - Total: {len(permissions_data)}")

    # Display permissions by module
    print("\n📋 Permissions by Module:")
    for module in ModuleType:
        count = db.query(Permission).filter(Permission.module == module).count()
        print(f"   - {module.value}: {count} permissions")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_permissions(db)
    except Exception as e:
        print(f"❌ Error seeding permissions: {e}")
        db.rollback()
        raise
    finally:
        db.close()
