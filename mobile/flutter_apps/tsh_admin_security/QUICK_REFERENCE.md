# TSH Admin Security - Quick Reference Guide

**Quick access to key information for developers and administrators**

---

## 📁 File Structure

```
mobile/flutter_apps/tsh_admin_security/
├── lib/
│   ├── screens/
│   │   └── user_detail_screen.dart       ⭐ Main feature (625 lines)
│   ├── widgets/
│   │   ├── security_section_card.dart    ⭐ Reusable card (70 lines)
│   │   ├── permission_chip.dart          ⭐ Permission display (150 lines)
│   │   └── data_scope_bar.dart           ⭐ Data access viz (380 lines)
│   ├── models/
│   │   └── user.dart                     (Needs extension)
│   ├── providers/
│   │   └── user_provider.dart            (Needs creation)
│   └── services/
│       └── user_service.dart             (Needs API methods)
└── docs/
    ├── UI_DESIGN_SPECIFICATION.md        (476 lines - complete design)
    ├── FRONTEND_DESIGN_SUMMARY.md        (300 lines - implementation)
    ├── INTEGRATION_CHECKLIST.md          (350 lines - step-by-step)
    └── IMPLEMENTATION_STATUS.md          (300 lines - current status)
```

---

## 🎨 Color Codes (Copy & Paste)

```dart
// Permission Colors
final directPermissionColor = Color(0xFF10B981);  // Green - Direct
final rolePermissionColor = Color(0xFF8B5CF6);    // Purple - Role

// Status Colors
final activeColor = Color(0xFF10B981);            // Green - Active
final inactiveColor = Color(0xFFEF4444);          // Red - Inactive
final warningColor = Color(0xFFF59E0B);           // Orange - Warning
final infoColor = Color(0xFF2563EB);              // Blue - Info

// RLS Colors
final rlsBackgroundColor = Colors.purple[50];     // RLS box background
final rlsTextColor = Colors.purple[700];          // RLS variable text
```

---

## 🔧 Quick Commands

### Flutter Development
```bash
# Navigate to project
cd mobile/flutter_apps/tsh_admin_security

# Install dependencies
flutter pub get

# Run on Chrome
flutter run -d chrome --web-port 3000

# Build for web
flutter build web

# Analyze code
flutter analyze

# Format code
flutter format lib/
```

### Backend Development
```bash
# Navigate to project root
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem

# Activate virtual environment
source .venv/bin/activate

# Run FastAPI server
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Apply RLS migration
psql -U tsh_admin -d tsh_erp -f database/migrations/implement_rls_policies.sql

# Check RLS policies
psql -U tsh_admin -d tsh_erp -c "SELECT * FROM pg_policies WHERE tablename IN ('customers', 'sales_orders', 'expenses', 'invoices');"
```

---

## 📊 User Detail Screen - Tab Reference

| Tab | Icon | Purpose | Key Features |
|-----|------|---------|--------------|
| **Overview** | 📊 | Quick summary | Profile, stats, role, sessions |
| **Auth & Security** | 🔐 | Authentication details | Auth methods, RLS variables, devices |
| **Permissions** | 🔓 | Complete permissions | Direct (green) + Role (purple) |
| **Data Access** | 👁️ | RLS scope | Table access bars, policies |
| **Activity** | 📈 | User activity | Timeline, login history, actions |

---

## 🎯 Key Visual Elements

### Permission Display

```
┌────────────────────────────────────────┐
│ 🟢 dashboard.view        [Direct]     │
│ 🟣 users.list            [Role]       │
│ 🟢 customers.update      [Direct]     │
│ 🟣 sales.view            [Role]       │
└────────────────────────────────────────┘

Green (🟢) = Direct permissions (user-specific)
Purple (🟣) = Role permissions (inherited)
```

### RLS Context Display

```
┌──────────────────────────────────────────────────┐
│ 🛡️ Row-Level Security (RLS) Context            │
│ PostgreSQL session variables set for this user  │
│                                                  │
│ ┌──────────────────────────────────────────────┐│
│ │ app.current_user_id     = 15        [Copy]  ││
│ │ app.current_user_role   = salesperson [Copy] ││
│ │ app.current_tenant_id   = 100       [Copy]  ││
│ │ app.current_branch_id   = 5         [Copy]  ││
│ │ app.current_warehouse_id = 2        [Copy]  ││
│ └──────────────────────────────────────────────┘│
└──────────────────────────────────────────────────┘
```

### Data Access Bar

```
┌────────────────────────────────────────────────┐
│ 📊 customers                    [Restricted]  │
│                                                │
│ Total: 1000   Accessible: 150   Percentage: 15%│
│ ████████░░░░░░░░░░░░░░░░░░░░░░░░ 15%          │
│                                                │
│ 📜 RLS Policy: customers_sales_rep_own_clients │
│ ℹ️  Access limited to own assigned clients    │
│                                                │
│ [View Details]  [Test Query]                  │
└────────────────────────────────────────────────┘
```

---

## 🔐 RLS Session Variables

When authenticating a user, set these PostgreSQL session variables:

```python
# Python (FastAPI)
from app.db.rls_context import set_rls_context

set_rls_context(
    db=db,
    user_id=user.id,                    # Required
    role_name=user.role.name,           # Required
    tenant_id=user.tenant_id,           # Optional
    branch_id=user.branch_id,           # Optional
    warehouse_id=user.warehouse_id      # Optional
)
```

```sql
-- SQL (Direct)
SELECT set_config('app.current_user_id', '15', false);
SELECT set_config('app.current_user_role', 'salesperson', false);
SELECT set_config('app.current_tenant_id', '100', false);
SELECT set_config('app.current_branch_id', '5', false);
SELECT set_config('app.current_warehouse_id', '2', false);
```

---

## 📡 API Endpoints (Required)

### Backend Endpoints to Implement

```python
# Comprehensive user details
GET /api/users/{user_id}/details
Response: {
  "user": {...},
  "role": {...},
  "permissions": [{source: "direct"}, {source: "role"}, ...],
  "active_sessions": [...],
  "trusted_devices": [...],
  "security_events": [...],
  "rls_context": {
    "user_id": 15,
    "role": "salesperson",
    "tenant_id": 100,
    "branch_id": 5,
    "warehouse_id": 2
  }
}

# User permissions with source
GET /api/users/{user_id}/permissions
Response: [
  {"name": "dashboard.view", "source": "direct", "module": "Dashboard"},
  {"name": "users.list", "source": "role", "module": "Users"}
]

# User active sessions
GET /api/users/{user_id}/sessions
Response: [
  {"id": 1, "device_info": "Chrome/Mac", "last_active": "2025-10-23T10:30:00Z"}
]

# User data access scope
GET /api/data-scope/{user_id}
Response: {
  "customers": {
    "table_name": "customers",
    "total_records": 1000,
    "accessible_records": 150,
    "policy_name": "customers_sales_rep_own_clients",
    "reason": "Access limited to own assigned clients"
  }
}

# User security events
GET /api/security/events?user_id={user_id}&limit=10
Response: [
  {"type": "login", "description": "Login from Chrome/Mac", "timestamp": "..."}
]
```

---

## 🧩 Widget Usage Examples

### SecuritySectionCard

```dart
import 'package:tsh_admin_security/widgets/security_section_card.dart';

SecuritySectionCard(
  title: 'Authentication Methods',
  subtitle: 'Configured login methods for this user',
  icon: Icons.key,
  iconColor: Colors.blue,
  child: Column(
    children: [
      // Your content here
    ],
  ),
)
```

### PermissionChip

```dart
import 'package:tsh_admin_security/widgets/permission_chip.dart';

PermissionChip(
  permission: Permission(
    name: 'users.create',
    description: 'Can create new users',
    module: 'Users',
    source: 'direct',  // or 'role'
  ),
  showSource: true,
  onTap: () => print('Permission tapped'),
  onDelete: () => print('Revoke permission'),
)
```

### DataScopeBar

```dart
import 'package:tsh_admin_security/widgets/data_scope_bar.dart';

DataScopeBar(
  tableName: 'customers',
  totalRecords: 1000,
  accessibleRecords: 150,
  policyName: 'customers_sales_rep_own_clients',
  reason: 'Access limited to own assigned clients',
  onTap: () => print('View details'),
)
```

---

## 🐛 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| **Permission model not found** | Move Permission class from `permission_chip.dart` to `lib/models/permission.dart` |
| **Provider not found** | Register UserProvider in `main.dart` MultiProvider |
| **RLS variables show "Not Set"** | Verify backend is returning `rls_context` in API response |
| **Colors not matching design** | Use exact color codes from "Color Codes" section above |
| **User data not loading** | Check API endpoint URLs in `lib/config/api_config.dart` |
| **Tab not displaying** | Ensure TabController length matches number of tabs (5) |

---

## 📚 Documentation Quick Links

| Document | When to Use |
|----------|-------------|
| `UI_DESIGN_SPECIFICATION.md` | Understanding the complete design system |
| `FRONTEND_DESIGN_SUMMARY.md` | Quick overview of what was built |
| `INTEGRATION_CHECKLIST.md` | Step-by-step implementation guide |
| `IMPLEMENTATION_STATUS.md` | Current status and what's completed |
| `QUICK_REFERENCE.md` | This file - quick lookups |

---

## 🔑 Key Concepts

### Permission Source
- **Direct**: Granted directly to the user (stored in `user_permissions` table)
- **Role**: Inherited from user's role (stored in `role_permissions` table)

### RLS Policy Types
- **RBAC**: Role-based (admin sees all)
- **ReBAC**: Relationship-based (sales rep sees own clients)
- **ABAC**: Attribute-based (status = 'PENDING')

### Color Meanings
- **Green**: Direct permissions, active status, full access
- **Purple**: Role permissions, RLS-protected, policies
- **Orange**: Warning, partial access
- **Red**: Error, blocked, no access
- **Blue**: Information, trust

---

## ✅ Quick Test Checklist

```bash
# Test RLS Policies
psql -U tsh_admin -d tsh_erp -c "
SET app.current_user_id = '15';
SET app.current_user_role = 'salesperson';
SELECT COUNT(*) FROM customers;  -- Should show limited results
"

# Test Backend API
curl -X GET "http://localhost:8000/api/users/15/details" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test Frontend
flutter run -d chrome --web-port 3000
# Navigate to user detail screen and verify all 5 tabs load
```

---

## 📞 Need Help?

1. **Design Questions**: Check `UI_DESIGN_SPECIFICATION.md`
2. **Integration Steps**: Follow `INTEGRATION_CHECKLIST.md`
3. **Backend RLS**: Read `SECURITY_IMPROVEMENTS_SUMMARY.md`
4. **Current Status**: See `IMPLEMENTATION_STATUS.md`

---

## 🎯 Remember

✅ **Direct Permissions** = Green = User-specific grants
✅ **Role Permissions** = Purple = Inherited from role
✅ **RLS Variables** = Purple box in Auth & Security tab
✅ **Data Access** = Visual bars showing percentage access
✅ **5 Tabs** = Overview, Auth, Permissions, Data, Activity

---

**Last Updated**: 2025-10-23
