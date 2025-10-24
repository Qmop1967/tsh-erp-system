# TSH Access Management - Backend Integration Plan

## Current Situation

The TSH ERP Ecosystem **already has comprehensive security infrastructure**:
- ✅ Advanced security models (ABAC, RBAC, PBAC, RLS, FLS)
- ✅ MFA implementation (TOTP, SMS, Email, Biometric)
- ✅ Device management with GPS tracking
- ✅ Session management with risk scoring
- ✅ Audit logging and security events
- ✅ User, role, and permission management

## Integration Approach

Instead of creating a standalone app, TSH Access Management should be a **mobile/web interface** to the existing backend.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   TSH ERP Backend                           │
│              (FastAPI - Port 8000)                          │
│                                                             │
│  ├─ /api/auth/* - Authentication & MFA                     │
│  ├─ /api/users/* - User management                         │
│  ├─ /api/permissions/* - Role & permission mgmt            │
│  ├─ /api/security/* - Security events, audit logs          │
│  └─ /api/admin/* - Admin dashboard                         │
└─────────────────────────────────────────────────────────────┘
                           ↑
                           │ REST API + JWT
                           │
      ┌────────────────────┼────────────────────┐
      │                    │                    │
      ▼                    ▼                    ▼
┌──────────┐      ┌──────────────┐      ┌──────────────┐
│ Web App  │      │ TSH Access   │      │ TSH Field    │
│ (React)  │      │ Management   │      │ Rep (Flutter)│
│Port 5173 │      │  (Flutter)   │      │ Port 5174    │
│          │      │  Port 5175   │      │              │
└──────────┘      └──────────────┘      └──────────────┘
   Admin              Admin/IT           Field Staff
  Dashboard          Mobile/Web          Mobile App
```

## Implementation Plan

### Phase 1: API Client Setup (Day 1)
- [ ] Create `lib/services/api_client.dart` - HTTP client with JWT handling
- [ ] Create `lib/services/auth_service.dart` - Login, logout, token refresh
- [ ] Create `lib/models/user.dart` - User model matching backend
- [ ] Create `lib/providers/auth_provider.dart` - State management for auth
- [ ] Test login with existing backend users

### Phase 2: Core Features (Day 2-3)
- [ ] **Dashboard** - Real-time metrics from `/api/admin/dashboard`
- [ ] **User Management** - CRUD operations via `/api/users/*`
- [ ] **Role Management** - Via `/api/permissions/roles/*`
- [ ] **Permission Management** - Via `/api/permissions/*`

### Phase 3: Security Features (Day 4-5)
- [ ] **Device Management** - List/approve/revoke devices
- [ ] **Session Management** - View/terminate active sessions
- [ ] **Login Logs** - View login attempts and audit trail
- [ ] **Security Events** - Real-time alerts and monitoring

### Phase 4: Advanced Features (Day 6-7)
- [ ] **MFA Management** - Enable/disable MFA for users
- [ ] **Audit Trail** - Comprehensive logging viewer
- [ ] **Reports** - Security and access reports
- [ ] **Settings** - System configuration

## Backend API Endpoints to Use

### Authentication
```
POST   /api/auth/login - Login with email/password
POST   /api/auth/logout - Logout and blacklist token
POST   /api/auth/refresh - Refresh access token
POST   /api/auth/mfa/verify - Verify MFA code
GET    /api/auth/me - Get current user info
```

### User Management
```
GET    /api/users - List all users
GET    /api/users/{id} - Get user details
POST   /api/users - Create new user
PUT    /api/users/{id} - Update user
DELETE /api/users/{id} - Delete user
GET    /api/users/{id}/sessions - User's active sessions
POST   /api/users/{id}/sessions/{session_id}/terminate - Terminate session
```

### Roles & Permissions
```
GET    /api/permissions/roles - List all roles
POST   /api/permissions/roles - Create role
PUT    /api/permissions/roles/{id} - Update role
DELETE /api/permissions/roles/{id} - Delete role
GET    /api/permissions - List all permissions
POST   /api/permissions/roles/{id}/permissions - Assign permissions to role
```

### Security & Monitoring
```
GET    /api/security/events - Security events
GET    /api/security/audit-logs - Audit trail
GET    /api/security/devices - All registered devices
PUT    /api/security/devices/{id}/status - Approve/block device
GET    /api/security/login-attempts - Login attempt history
```

### Admin Dashboard
```
GET    /api/admin/dashboard/metrics - Dashboard metrics
GET    /api/admin/dashboard/analytics - Charts and analytics
```

## Shared Configuration

### API Base URL
```dart
// lib/config/api_config.dart
class ApiConfig {
  static const String baseUrl = 'http://localhost:8000';
  static const String apiPrefix = '/api';

  // Endpoints
  static const String authEndpoint = '$apiPrefix/auth';
  static const String usersEndpoint = '$apiPrefix/users';
  static const String permissionsEndpoint = '$apiPrefix/permissions';
  static const String securityEndpoint = '$apiPrefix/security';
  static const String adminEndpoint = '$apiPrefix/admin';
}
```

### Authentication Flow
```dart
// 1. User enters credentials
// 2. POST /api/auth/login → Returns JWT access_token
// 3. Store token in secure storage
// 4. Include token in all requests: Authorization: Bearer <token>
// 5. If MFA required → Show MFA screen → POST /api/auth/mfa/verify
// 6. On token expiry → POST /api/auth/refresh with refresh_token
// 7. On logout → POST /api/auth/logout → Clear local storage
```

## Database Integration

TSH Access Management will **share the same PostgreSQL database** as the main ERP system:

```
Database: tsh_erp
Tables Used:
  - users
  - roles
  - permissions
  - role_permissions
  - user_permissions
  - user_sessions
  - user_devices
  - login_attempts
  - security_events
  - audit_logs
  - mfa_methods
  - advanced_security.* (all advanced security tables)
```

## Benefits of Integration

✅ **Single Source of Truth** - All user data in one database
✅ **Consistent Authentication** - Same JWT tokens across all apps
✅ **Real-time Sync** - Changes reflect immediately everywhere
✅ **Unified Audit Trail** - All actions logged centrally
✅ **Reduced Complexity** - No duplicate infrastructure
✅ **Better Security** - Centralized security policies
✅ **Cost Effective** - Single backend to maintain

## Next Steps

1. **Update Flutter app dependencies** - Add `dio`, `flutter_secure_storage`, `provider`
2. **Create API client layer** - HTTP client with interceptors
3. **Implement authentication** - Login screen connecting to backend
4. **Build dashboard** - Fetch real metrics from admin endpoint
5. **Add CRUD operations** - User, role, permission management
6. **Implement security features** - Device mgmt, sessions, logs
7. **Test integration** - E2E testing with real backend

## File Structure

```
lib/
├── config/
│   └── api_config.dart
├── models/
│   ├── user.dart
│   ├── role.dart
│   ├── permission.dart
│   ├── device.dart
│   ├── session.dart
│   └── security_event.dart
├── services/
│   ├── api_client.dart
│   ├── auth_service.dart
│   ├── user_service.dart
│   ├── role_service.dart
│   ├── permission_service.dart
│   └── security_service.dart
├── providers/
│   ├── auth_provider.dart
│   ├── user_provider.dart
│   └── security_provider.dart
├── screens/
│   ├── auth/
│   │   ├── login_screen.dart
│   │   └── mfa_screen.dart
│   ├── dashboard/
│   │   └── dashboard_screen.dart
│   ├── users/
│   │   ├── users_list_screen.dart
│   │   └── user_detail_screen.dart
│   ├── roles/
│   │   └── roles_screen.dart
│   ├── permissions/
│   │   └── permissions_screen.dart
│   └── security/
│       ├── devices_screen.dart
│       ├── sessions_screen.dart
│       ├── audit_logs_screen.dart
│       └── security_events_screen.dart
└── main.dart
```

## Security Considerations

🔒 **JWT Storage** - Use `flutter_secure_storage` for tokens
🔒 **SSL Pinning** - Implement for production API calls
🔒 **Token Refresh** - Auto-refresh before expiry
🔒 **Secure Communication** - HTTPS only in production
🔒 **Biometric Auth** - For mobile app unlock
🔒 **Root Detection** - Prevent running on compromised devices

---

**Created:** 2025-10-21
**Version:** 1.0.0
**Status:** Integration Plan - Ready for Implementation
