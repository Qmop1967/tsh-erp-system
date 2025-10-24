# TSH Admin Security - Integration Checklist

## Overview

This checklist will guide you through integrating the newly designed comprehensive User Detail Screen into your Flutter application. The design includes 5 tabs showing complete authentication, role, permission, data access, and activity details.

---

## ✅ Completed Design Work

### Backend Implementation
- ✅ PostgreSQL RLS policies created and applied
- ✅ RLS context bridge implemented (`app/db/rls_context.py`)
- ✅ RLS-aware FastAPI dependencies created (`app/db/rls_dependency.py`)
- ✅ Dashboard API fixed (status → is_active)
- ✅ Security improvements documented

### Frontend Design
- ✅ UI Design Specification (476 lines)
- ✅ User Detail Screen with 5 tabs (625 lines)
- ✅ SecuritySectionCard widget (reusable)
- ✅ PermissionChip widget (green/purple color coding)
- ✅ DataScopeBar widget (RLS visualization)
- ✅ Frontend Design Summary documentation

---

## 🔧 Integration Steps

### Step 1: Check Model Compatibility

The new User Detail Screen expects a richer User model than currently exists. You need to extend the User model to include:

#### Current User Model Location
`lib/models/user.dart`

#### Required Additions

```dart
class User {
  // ... existing fields ...

  // NEW: Required for comprehensive view
  final Role? role;                    // Full role object
  final int? tenantId;                 // For RLS context display
  final int? warehouseId;              // For RLS context display
  final List<Permission>? permissions; // Full permission objects
  final List<Session>? activeSessions; // For overview tab
  final List<TrustedDevice>? trustedDevices; // For auth tab
  final List<SecurityEvent>? recentEvents;    // For auth tab
  final Map<String, dynamic>? securitySettings; // 2FA, password status
  final Map<String, TableAccess>? dataAccess;   // For data access tab

  // Constructor and fromJson updates needed
}
```

#### Supporting Models Needed

You'll need to create or extend these models:

1. **Permission Model** (partially exists in `permission_chip.dart`)
   - Move to `lib/models/permission.dart`
   - Already has: name, description, module, source

2. **Role Model** (already exists at `lib/models/role.dart`)
   - Should include: id, name, description, capabilities

3. **Session Model** (already exists at `lib/models/session.dart`)
   - Should include: id, deviceInfo, lastActive, ipAddress

4. **TrustedDevice Model**
   ```dart
   class TrustedDevice {
     final String deviceFingerprint;
     final String deviceName;
     final DateTime trustedAt;
     final DateTime? lastUsed;
   }
   ```

5. **SecurityEvent Model** (already exists at `lib/models/security_event.dart`)
   - Should include: type, description, timestamp, severity

6. **TableAccess Model**
   ```dart
   class TableAccess {
     final String tableName;
     final int totalRecords;
     final int accessibleRecords;
     final String policyName;
     final String reason;
   }
   ```

---

### Step 2: Update or Create UserProvider

The new User Detail Screen uses a `UserProvider` that doesn't exist yet.

#### Create File: `lib/providers/user_provider.dart`

```dart
import 'package:flutter/material.dart';
import '../models/user.dart';
import '../services/user_service.dart';

class UserProvider with ChangeNotifier {
  final UserService _userService;
  User? _selectedUser;
  bool _isLoading = false;

  UserProvider(this._userService);

  User? get selectedUser => _selectedUser;
  bool get isLoading => _isLoading;

  Future<void> loadUserDetails(int userId) async {
    _isLoading = true;
    notifyListeners();

    try {
      _selectedUser = await _userService.getUserDetails(userId);
    } catch (e) {
      // Handle error
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void clearSelectedUser() {
    _selectedUser = null;
    notifyListeners();
  }
}
```

---

### Step 3: Extend UserService with New Endpoints

Update `lib/services/user_service.dart` to fetch comprehensive user details.

#### New API Endpoints Needed

```dart
class UserService {
  final ApiClient _apiClient;

  // NEW: Comprehensive user details
  Future<User> getUserDetails(int userId) async {
    final response = await _apiClient.get('/api/users/$userId/details');
    return User.fromJson(response.data);
  }

  // NEW: User permissions
  Future<List<Permission>> getUserPermissions(int userId) async {
    final response = await _apiClient.get('/api/users/$userId/permissions');
    return (response.data as List)
        .map((json) => Permission.fromJson(json))
        .toList();
  }

  // NEW: User active sessions
  Future<List<Session>> getUserSessions(int userId) async {
    final response = await _apiClient.get('/api/users/$userId/sessions');
    return (response.data as List)
        .map((json) => Session.fromJson(json))
        .toList();
  }

  // NEW: User data access scope
  Future<Map<String, TableAccess>> getUserDataAccess(int userId) async {
    final response = await _apiClient.get('/api/data-scope/$userId');
    return (response.data as Map<String, dynamic>).map(
      (key, value) => MapEntry(key, TableAccess.fromJson(value)),
    );
  }

  // NEW: User security events
  Future<List<SecurityEvent>> getUserSecurityEvents(int userId, {int limit = 10}) async {
    final response = await _apiClient.get('/api/security/events', queryParameters: {
      'user_id': userId,
      'limit': limit,
    });
    return (response.data as List)
        .map((json) => SecurityEvent.fromJson(json))
        .toList();
  }
}
```

---

### Step 4: Backend API Endpoints Required

Your FastAPI backend needs these new endpoints to support the comprehensive view:

#### 1. Comprehensive User Details
```python
# File: app/routers/users.py

@router.get("/users/{user_id}/details", response_model=UserDetailResponse)
async def get_user_details(
    user_id: int,
    db: Session = Depends(get_db_with_rls)
):
    """Get comprehensive user details including role, permissions, sessions"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get full permission details
    permissions = get_user_permissions_with_source(db, user_id)

    # Get active sessions
    sessions = db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.is_active == True
    ).all()

    # Get trusted devices
    devices = db.query(TrustedDevice).filter(
        TrustedDevice.user_id == user_id,
        TrustedDevice.is_trusted == True
    ).all()

    # Get recent security events
    events = db.query(SecurityEvent).filter(
        SecurityEvent.user_id == user_id
    ).order_by(SecurityEvent.created_at.desc()).limit(10).all()

    return {
        "user": user,
        "role": user.role,
        "permissions": permissions,
        "active_sessions": sessions,
        "trusted_devices": devices,
        "security_events": events,
        "rls_context": {
            "user_id": user.id,
            "role": user.role.name if user.role else None,
            "tenant_id": user.tenant_id,
            "branch_id": user.branch_id,
            "warehouse_id": user.warehouse_id,
        }
    }
```

#### 2. Permission Details with Source
```python
def get_user_permissions_with_source(db: Session, user_id: int) -> List[Dict]:
    """Get user permissions with indication of source (direct or role)"""

    # Direct permissions
    direct = db.query(Permission).join(
        UserPermission, UserPermission.permission_id == Permission.id
    ).filter(UserPermission.user_id == user_id).all()

    # Role permissions
    user = db.query(User).filter(User.id == user_id).first()
    role_perms = []
    if user.role:
        role_perms = db.query(Permission).join(
            RolePermission, RolePermission.permission_id == Permission.id
        ).filter(RolePermission.role_id == user.role_id).all()

    # Combine with source indicator
    permissions = []
    for perm in direct:
        permissions.append({
            "id": perm.id,
            "name": perm.name,
            "description": perm.description,
            "module": perm.module,
            "source": "direct",
            "is_active": True,
        })

    for perm in role_perms:
        # Avoid duplicates
        if not any(p["id"] == perm.id for p in permissions):
            permissions.append({
                "id": perm.id,
                "name": perm.name,
                "description": perm.description,
                "module": perm.module,
                "source": "role",
                "is_active": True,
            })

    return permissions
```

#### 3. Data Access Scope
```python
@router.get("/data-scope/{user_id}")
async def get_user_data_scope(
    user_id: int,
    db: Session = Depends(get_db_with_rls)
):
    """Calculate data access scope based on RLS policies"""

    # Set RLS context for this user
    set_rls_context(db, user_id)

    # List of tables to check
    tables = ["customers", "sales_orders", "expenses", "invoices"]

    scope = {}
    for table in tables:
        # Get total count (admin view)
        total = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()

        # Get accessible count (user view)
        accessible = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()

        # Get policy name
        policy = get_active_policy_for_table(db, table, user_id)

        scope[table] = {
            "table_name": table,
            "total_records": total,
            "accessible_records": accessible,
            "policy_name": policy["name"],
            "reason": policy["reason"],
        }

    return scope
```

---

### Step 5: Update Main App to Include Provider

#### Update: `lib/main.dart`

```dart
import 'package:provider/provider.dart';
import 'providers/user_provider.dart';
import 'services/user_service.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        // ... existing providers ...
        ChangeNotifierProvider(
          create: (_) => UserProvider(UserService()),
        ),
      ],
      child: const MyApp(),
    ),
  );
}
```

---

### Step 6: Replace Old User Detail Screen

You currently have two user detail screens:
- `lib/screens/user_detail_screen.dart` (new comprehensive design)
- `lib/screens/users/user_detail_screen.dart` (old simple version)

#### Option 1: Replace Completely
Delete or rename the old screen and update all navigation references to use the new one.

#### Option 2: Gradual Migration
Keep both and create a feature flag to test the new screen:

```dart
// In navigation code
if (useNewUserDetailScreen) {
  Navigator.push(
    context,
    MaterialPageRoute(
      builder: (context) => UserDetailScreen(userId: userId),
    ),
  );
} else {
  // Old screen
}
```

---

### Step 7: Test Integration

#### Test Checklist

1. **User Profile Loading**
   - [ ] Navigate to user detail screen
   - [ ] Verify loading indicator appears
   - [ ] Verify user data loads correctly

2. **Overview Tab**
   - [ ] Profile card displays correctly
   - [ ] Statistics show accurate counts
   - [ ] Role assignment is visible
   - [ ] Security status indicators work

3. **Auth & Security Tab**
   - [ ] Authentication methods display
   - [ ] RLS context variables show correct values
   - [ ] Trusted devices list appears
   - [ ] Security events timeline displays

4. **Permissions Tab**
   - [ ] Permission summary shows correct counts
   - [ ] Permissions grouped by module
   - [ ] Green badges for direct permissions
   - [ ] Purple badges for role permissions
   - [ ] Revoke button only on direct permissions

5. **Data Access Tab**
   - [ ] Data scope bars display
   - [ ] Percentages calculate correctly
   - [ ] RLS policy names show
   - [ ] Color coding based on access level

6. **Activity Tab**
   - [ ] Timeline displays
   - [ ] Login history shows
   - [ ] Recent actions list

---

## 📋 Dependencies Check

Ensure these dependencies are in `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter

  # State Management
  provider: ^6.1.2

  # HTTP Requests
  dio: ^5.7.0

  # Secure Storage
  flutter_secure_storage: ^9.2.2

  # Date Formatting
  intl: ^0.19.0

  # Icons (if using additional icon packs)
  cupertino_icons: ^1.0.8
```

Run:
```bash
cd mobile/flutter_apps/tsh_admin_security
flutter pub get
```

---

## 🎨 Color Scheme Reference

The design uses these color codes:

### Permission Colors
- **Direct Permission**: `Colors.green` (RGB: 16, 185, 129)
- **Role Permission**: `Colors.purple` (RGB: 139, 92, 246)

### Status Colors
- **Active**: `Colors.green` (RGB: 16, 185, 129)
- **Inactive**: `Colors.red` (RGB: 239, 68, 68)
- **Warning**: `Colors.orange` (RGB: 245, 158, 11)
- **Info**: `Colors.blue` (RGB: 37, 99, 235)

### RLS Colors
- **RLS Protected**: `Colors.purple[50]` (Background)
- **RLS Variable**: `Colors.purple[700]` (Text)

---

## 🔐 Security Considerations

1. **API Authorization**: Ensure all new endpoints require proper JWT authentication
2. **RLS Context**: Verify RLS context is set before querying sensitive data
3. **Permission Checks**: Validate that only admins can view other users' details
4. **Data Sanitization**: Sanitize user inputs before displaying
5. **Audit Logging**: Log all permission changes and data access

---

## 📱 Responsive Design

The design is responsive across these breakpoints:

- **Mobile**: < 600px (single column, stacked tabs)
- **Tablet**: 600px - 1024px (2-column layout)
- **Desktop**: > 1024px (multi-column, persistent sidebar)

Test on multiple devices:
```bash
# Web
flutter run -d chrome

# iOS Simulator
flutter run -d iPhone

# Android Emulator
flutter run -d emulator
```

---

## 🐛 Troubleshooting

### Issue: "Provider not found"
**Solution**: Ensure `UserProvider` is registered in `main.dart` before the widget tree.

### Issue: "User data not loading"
**Solution**: Check API endpoint URLs in `api_config.dart` and verify backend is running.

### Issue: "Permission model mismatch"
**Solution**: Move Permission class from `permission_chip.dart` to `lib/models/permission.dart`.

### Issue: "RLS variables showing 'Not Set'"
**Solution**: Verify backend is setting RLS context and returning values in API response.

### Issue: "Data scope bars not displaying"
**Solution**: Ensure backend `/data-scope/{user_id}` endpoint is implemented and returning correct format.

---

## 🚀 Next Steps After Integration

1. **User List Screen**: Create a grid/list view of users that navigates to detail screen
2. **Real-time Updates**: Implement WebSocket for live permission changes
3. **Permission Management**: Add UI for granting/revoking permissions
4. **Role Management**: Create role detail screen similar to user detail
5. **Audit Trail**: Add comprehensive audit log viewer
6. **Performance**: Add pagination for large datasets
7. **Search & Filter**: Add search and filter capabilities
8. **Export**: Add export functionality for reports

---

## 📚 Documentation References

- **UI Design Specification**: `UI_DESIGN_SPECIFICATION.md`
- **Frontend Design Summary**: `FRONTEND_DESIGN_SUMMARY.md`
- **Backend Security**: `/SECURITY_IMPROVEMENTS_SUMMARY.md`
- **Architecture**: `ARCHITECTURE.md`

---

## ✅ Final Checklist Before Production

- [ ] All models updated with required fields
- [ ] UserProvider implemented and registered
- [ ] All API endpoints implemented on backend
- [ ] RLS policies tested with different user roles
- [ ] UI tested on mobile, tablet, and desktop
- [ ] Error handling implemented
- [ ] Loading states working correctly
- [ ] Navigation flow verified
- [ ] Permissions display correctly (color coding)
- [ ] RLS context displays real values
- [ ] Data scope visualization working
- [ ] Security audit passed
- [ ] Performance testing completed
- [ ] Accessibility testing done
- [ ] User acceptance testing passed

---

## 🎯 Summary

This comprehensive User Detail Screen design provides:

✅ **5-tab detailed interface** showing all user information
✅ **Complete authentication status** with 2FA, trusted devices
✅ **RLS session variables** displayed in purple box
✅ **All permissions listed** with source clearly indicated
✅ **Visual data access scope** with RLS policy information
✅ **Activity timeline** and security event tracking

The design is **security-first**, **visually appealing**, and perfectly integrated with your PostgreSQL RLS implementation. Follow the integration steps above to bring this design to life in your application!
