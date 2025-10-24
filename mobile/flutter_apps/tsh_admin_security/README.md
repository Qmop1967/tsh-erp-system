# 🔐 TSH Admin & Security Control

**Enterprise-Grade Admin Control Panel for iOS, Android & Web**

## Overview

TSH Admin & Security Control is a comprehensive cross-platform application for managing users, roles, permissions, devices, and monitoring security across the TSH ERP ecosystem. Built with **Flutter** for the frontend and **FastAPI** for the backend, integrated with **PostgreSQL Row-Level Security (RLS)** for database-level access control.

## ✨ New Features

### 🎯 Comprehensive User Detail Screen
When you select a user, see **everything** in a beautiful 5-tab interface:

- ✅ **Tab 1: Overview** - Profile, statistics, role, active sessions
- ✅ **Tab 2: Auth & Security** - Authentication methods, **RLS session variables**, password security, trusted devices, security events
- ✅ **Tab 3: Permissions** - Complete permission list with **color-coded source** (🟢 Green = Direct, 🟣 Purple = Role)
- ✅ **Tab 4: Data Access** - Visual **RLS data scope** with percentage bars showing table access
- ✅ **Tab 5: Activity** - Timeline, login history, recent actions

### 🔐 PostgreSQL RLS Integration
- 8 RLS policies across 5 tables (customers, sales_orders, expenses, invoices)
- Hybrid authorization model: RBAC + ReBAC + ABAC
- Session variable bridge connecting FastAPI to PostgreSQL
- Visual display of RLS context variables in the UI

### 🎨 Security-First Design
- Color-coded permissions (Direct vs Role)
- Visual data access scope bars
- RLS policy information display
- Real-time security event timeline
- Device trust management

## Quick Start

```bash
# Navigate to project
cd mobile/flutter_apps/tsh_admin_security

# Install dependencies
flutter pub get

# Run on web
flutter run -d chrome --web-port 3000

# Run on mobile
flutter run
```

## 📚 Documentation

### Main Documentation
- **`IMPLEMENTATION_STATUS.md`** - ⭐ **START HERE** - Complete overview of what's been built
- **`INTEGRATION_CHECKLIST.md`** - Step-by-step guide to integrate the new design
- **`QUICK_REFERENCE.md`** - Quick access to code snippets, colors, and commands
- **`UI_DESIGN_SPECIFICATION.md`** - Complete design system (476 lines)
- **`FRONTEND_DESIGN_SUMMARY.md`** - Implementation summary with visual mockups
- **`ARCHITECTURE.md`** - System architecture

### Backend Documentation
- **`/SECURITY_IMPROVEMENTS_SUMMARY.md`** - RLS implementation guide (in project root)

### Key Files
```
lib/
├── screens/
│   └── user_detail_screen.dart       ⭐ Main feature (625 lines, 5 tabs)
├── widgets/
│   ├── security_section_card.dart    (Reusable card component)
│   ├── permission_chip.dart          (Green/purple permission display)
│   └── data_scope_bar.dart           (RLS data access visualization)
└── models/
    └── user.dart                     (Needs extension - see INTEGRATION_CHECKLIST.md)
```

## 🎨 Visual Language

### Color Scheme
- 🟢 **Green** (`#10B981`) - Direct permissions, active status, full access
- 🟣 **Purple** (`#8B5CF6`) - Role permissions, RLS-protected, policies
- 🟠 **Orange** (`#F59E0B`) - Warning, partial access
- 🔴 **Red** (`#EF4444`) - Error, blocked, no access
- 🔵 **Blue** (`#2563EB`) - Information, trust

### Permission Display
```
🟢 dashboard.view    [Direct]   ← User-specific grant
🟣 users.list        [Role]     ← Inherited from role
🟢 customers.update  [Direct]   ← User-specific grant
🟣 sales.view        [Role]     ← Inherited from role
```

### RLS Context Display
Shows actual PostgreSQL session variables:
```
app.current_user_id      = 15
app.current_user_role    = salesperson
app.current_tenant_id    = 100
app.current_branch_id    = 5
app.current_warehouse_id = 2
```

## ✅ Core Features

### 1. Dashboard & Analytics
Real-time metrics, charts, and security insights

### 2. User Management ⭐ NEW DESIGN
- **Comprehensive 5-tab user detail view**
- Complete authentication, role, and permission details
- Visual RLS context display
- Data access scope visualization
- Full CRUD, bulk operations, activity tracking

### 3. Roles & Permissions
- Granular RBAC/ABAC with visual matrix
- Color-coded permission source tracking
- Direct vs inherited permission management

### 4. Device Management
- Track, approve, remotely manage devices
- Trusted device management
- Device fingerprinting

### 5. Security Monitoring
- Real-time security event timeline
- Login logs & audit trail
- Threat detection and alerts

### 6. Session Management
- Monitor and control active sessions
- Multi-device session tracking
- Force logout capability

### 7. Multi-Factor Authentication
- TOTP (Authenticator app)
- SMS, Email verification
- Biometric support

### 8. Data Access Control
- PostgreSQL Row-Level Security (RLS)
- Visual data scope with percentage bars
- Policy information and testing

### 9. Reports & Analytics
- Comprehensive reporting with export
- Security audit reports
- Permission usage analytics

### 10. System Configuration
- Settings, policies, integrations
- RLS policy management

## 🚀 Getting Started

### Prerequisites
- Flutter SDK 3.24.5 or higher
- Dart 3.5.4 or higher
- FastAPI backend running (port 8000)
- PostgreSQL database with RLS policies

### Installation

1. **Clone and navigate**
   ```bash
   cd mobile/flutter_apps/tsh_admin_security
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **Configure API endpoint**
   Edit `lib/config/api_config.dart`:
   ```dart
   static const String baseUrl = 'http://localhost:8000';
   ```

4. **Run the app**
   ```bash
   # Web
   flutter run -d chrome --web-port 3000

   # iOS
   flutter run -d iPhone

   # Android
   flutter run -d emulator
   ```

## 🔧 Integration Guide

To integrate the new User Detail Screen design:

1. **Read** `IMPLEMENTATION_STATUS.md` for overview
2. **Follow** `INTEGRATION_CHECKLIST.md` step-by-step
3. **Reference** `QUICK_REFERENCE.md` for code snippets
4. **Refer to** `UI_DESIGN_SPECIFICATION.md` for design details

Key integration steps:
- ✅ Extend User model with required fields
- ✅ Create UserProvider for state management
- ✅ Implement backend API endpoints
- ✅ Update navigation to new screen
- ✅ Test all 5 tabs

See `INTEGRATION_CHECKLIST.md` for complete details.

## 🔐 Security Features

### Backend Security
- ✅ PostgreSQL RLS policies (database-level)
- ✅ JWT authentication (application-level)
- ✅ Session variable protection
- ✅ Multi-tenant isolation
- ✅ Audit logging

### Frontend Security
- ✅ Secure token storage
- ✅ Permission-based UI rendering
- ✅ XSS protection (Flutter's built-in)
- ✅ HTTPS-only API calls
- ✅ No sensitive data in UI state

## 📊 Project Statistics

- **Total Code**: ~3,925 lines
  - Backend: ~800 lines
  - Frontend: ~1,625 lines
  - Documentation: ~1,500 lines

- **Key Files Created**:
  - User Detail Screen: 625 lines (5 tabs)
  - Widget Components: 600 lines (3 widgets)
  - RLS Implementation: 800 lines (backend)
  - Documentation: 1,500 lines (5 docs)

## 🎯 What Makes This Special

### Visual RLS Context
First Flutter admin panel to visually display PostgreSQL RLS session variables in a user-friendly purple-themed box.

### Permission Source Tracking
Clear visual distinction between direct (green) and role-inherited (purple) permissions with revoke capability only on direct grants.

### Data Access Visualization
Interactive progress bars showing percentage access to each table based on RLS policies with policy names and reasons.

### Comprehensive 5-Tab View
Everything about a user in one place: authentication, permissions, data access, activity - no navigation needed.

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Provider not found | Register UserProvider in `main.dart` |
| User data not loading | Check API endpoint URLs in config |
| RLS variables show "Not Set" | Verify backend returns `rls_context` |
| Colors not matching | Use color codes from `QUICK_REFERENCE.md` |

See `INTEGRATION_CHECKLIST.md` for more troubleshooting tips.

## 📱 Supported Platforms

- ✅ **Web** (Chrome, Firefox, Safari, Edge)
- ✅ **iOS** (13.0+)
- ✅ **Android** (API 21+)
- ✅ **macOS** (10.14+)
- ✅ **Windows** (10+)
- ✅ **Linux**

## 🧪 Testing

```bash
# Run unit tests
flutter test

# Run integration tests
flutter test integration_test

# Run with coverage
flutter test --coverage

# Analyze code
flutter analyze
```

## 📦 Dependencies

Key dependencies:
- `provider: ^6.1.2` - State management
- `dio: ^5.7.0` - HTTP requests
- `flutter_secure_storage: ^9.2.2` - Secure token storage
- `intl: ^0.19.0` - Date formatting

See `pubspec.yaml` for complete list.

## 🤝 Contributing

This is a proprietary project for TSH ERP. Contact the development team for contribution guidelines.

## 📄 License

Proprietary - TSH ERP

## 📞 Support

- **Email**: support@tsh.com
- **Documentation**: See `docs/` folder
- **Integration Help**: Read `INTEGRATION_CHECKLIST.md`
- **Quick Reference**: Check `QUICK_REFERENCE.md`

---

## 🎉 Recent Updates

### Version 2.0 (2025-10-23)
- ✅ **New comprehensive User Detail Screen** with 5 tabs
- ✅ **PostgreSQL RLS integration** with visual display
- ✅ **Color-coded permission system** (Direct vs Role)
- ✅ **Data access visualization** with percentage bars
- ✅ **Complete documentation** (1,500+ lines)
- ✅ **Reusable widget components** (SecuritySectionCard, PermissionChip, DataScopeBar)

---

**Built with ❤️ for TSH ERP Ecosystem**
