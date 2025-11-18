# TSH Admin Security App - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
```bash
# Flutter SDK 3.0+
flutter --version

# Ensure you're in the app directory
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem/mobile/flutter_apps/02_tsh_admin_security
```

### Install Dependencies
```bash
flutter pub get
```

---

## 🏃 Running the App

### Development Mode (Local Backend)
```bash
# Run with local backend at http://192.168.68.51:8000
flutter run
```

### Staging Mode (Test with Real Data)
```bash
# Run with staging server at https://staging.erp.tsh.sale
flutter run --dart-define=ENVIRONMENT=staging
```

### Production Mode
```bash
# Run with production server at https://erp.tsh.sale
flutter run --dart-define=ENVIRONMENT=production
```

---

## 🔑 Test Credentials

### Staging Environment
```
Email: admin@tsh.sale
Password: [Ask the team]

Backend: https://staging.erp.tsh.sale
```

### Production Environment
```
Email: [Production admin email]
Password: [Production password]

Backend: https://erp.tsh.sale
```

---

## 🎯 Key Features Implemented

### 1. Real User Data Loading
- ✅ Fetches users from PostgreSQL database via FastAPI backend
- ✅ Supports pagination (20 users per page, max 100)
- ✅ Search by name or email
- ✅ Filter by active/inactive status

### 2. Zoho Integration Tracking
- ✅ Displays Zoho user ID
- ✅ Shows last sync timestamp
- ✅ Visual indicators for sync status
- ✅ Human-readable sync messages ("Synced 2h ago")

### 3. Multi-Environment Support
- ✅ Development: Local backend
- ✅ Staging: Test server
- ✅ Production: Live server
- ✅ Environment indicator in app bar

---

## 📊 User Data Fields

### Available in User Model:
```dart
id                 // User ID
name               // Full name
email              // Email address
employeeCode       // Employee code
phone              // Phone number
roleId             // Role ID
roleName           // Role name (Admin, Manager, etc.)
branchId           // Branch ID
branchName         // Branch name
isActive           // Active status
isSalesperson      // Salesperson flag
zohoUserId         // Zoho user ID (NEW)
zohoLastSync       // Last sync timestamp (NEW)
createdAt          // Creation date
updatedAt          // Last update
lastLogin          // Last login time
permissions        // List of permissions
```

---

## 🔧 Configuration Files

### API Configuration
**File:** `lib/config/api_config.dart`

```dart
// Environment-based URLs
static const String productionUrl = 'https://erp.tsh.sale';
static const String stagingUrl = 'https://staging.erp.tsh.sale';
static const String developmentUrl = 'http://192.168.68.51:8000';

// Automatically selected based on --dart-define=ENVIRONMENT
```

### User Model
**File:** `lib/models/user.dart`

```dart
class User {
  final int id;
  final String email;
  final String? name;
  // ... other fields
  final String? zohoUserId;      // NEW
  final DateTime? zohoLastSync;  // NEW

  // Helper methods
  bool get isSyncedWithZoho;     // Check sync status
  String get syncStatusMessage;  // Get readable message
}
```

---

## 🧪 Testing Workflow

### 1. Test on Development (Local)
```bash
# Start local backend first
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem
# [Start your local FastAPI server]

# Run Flutter app
cd mobile/flutter_apps/02_tsh_admin_security
flutter run
```

### 2. Test on Staging (Real Data)
```bash
# No need to start backend, uses staging server
flutter run --dart-define=ENVIRONMENT=staging

# Test scenarios:
# - Login with staging credentials
# - View users list (should load 500+ users)
# - Search for specific user
# - Filter by status
# - Check Zoho sync badges
```

### 3. Build for Production
```bash
# Build APK
flutter build apk --dart-define=ENVIRONMENT=production --release

# Build iOS
flutter build ios --dart-define=ENVIRONMENT=production --release
```

---

## 📱 UI Screenshots & Descriptions

### Users List Screen
```
┌─────────────────────────────────────┐
│ User Management                     │
│ Environment: Staging           🔄 ⚙️│
├─────────────────────────────────────┤
│ 🔍 Search users...                  │
├─────────────────────────────────────┤
│ ┌─────────────────────────────────┐ │
│ │ A  Ahmad Hassan                 │ │
│ │    ahmad@tsh.sale               │ │
│ │    👔 Manager  ☁️ Synced 2h ago │ │
│ │                           Active│ │
│ └─────────────────────────────────┘ │
│ ┌─────────────────────────────────┐ │
│ │ F  Fatima Ali                   │ │
│ │    fatima@tsh.sale              │ │
│ │    👔 Salesperson  ⚠️ Not synced│ │
│ │                           Active│ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
                                  [+]
```

### Zoho Sync Status Badges
```
✅ Green Badge: "Synced 2h ago"     - Recently synced
✅ Green Badge: "Synced 1d ago"     - Synced yesterday
⚠️ Orange Badge: "Not synced"       - No Zoho ID
```

---

## 🐛 Troubleshooting

### Error: "Failed to fetch users"
**Cause:** Cannot connect to backend
**Solution:**
1. Check internet connection
2. Verify backend is running
3. Check environment configuration
4. Review console logs for detailed error

### Error: "Unauthorized" or "401"
**Cause:** Invalid or expired token
**Solution:**
1. Logout and login again
2. Clear app data
3. Verify credentials

### Users Not Showing Zoho Status
**Cause:** Backend not returning zoho_user_id
**Solution:**
1. Verify backend API response includes zoho_user_id
2. Check User model fromJson() method
3. Review API logs

### App Crashes on Launch
**Cause:** Dependency or configuration issue
**Solution:**
```bash
# Clean and rebuild
flutter clean
flutter pub get
flutter run
```

---

## 📚 API Endpoints Used

### Authentication
```
POST /api/auth/login
GET  /api/auth/me
POST /api/auth/logout
```

### User Management
```
GET    /api/users              # List all users (paginated)
GET    /api/users/{id}         # Get specific user
POST   /api/users              # Create user
PUT    /api/users/{id}         # Update user
DELETE /api/users/{id}         # Delete user
```

### Query Parameters
```
skip      - Pagination offset (0, 20, 40...)
limit     - Page size (default: 20, max: 100)
search    - Search by name or email
is_active - Filter by active status (true/false)
```

---

## 🔐 Security Notes

### Authentication
- JWT token stored securely using FlutterSecureStorage
- Token automatically added to all API requests
- Automatic logout on token expiration

### Authorization
- All endpoints require valid authentication
- Role-based access control enforced
- Permission checks before operations

### Data Protection
- HTTPS for staging/production
- No credentials in source code
- Sensitive data encrypted

---

## 📦 Build & Deployment

### Development Build
```bash
# Debug build (fast, includes debug info)
flutter run --debug
```

### Staging Build
```bash
# Profile build for performance testing
flutter build apk --dart-define=ENVIRONMENT=staging --profile
```

### Production Build
```bash
# Release build (optimized, minified)
flutter build apk --dart-define=ENVIRONMENT=production --release

# Output: build/app/outputs/flutter-apk/app-release.apk
```

### iOS Production Build
```bash
flutter build ios --dart-define=ENVIRONMENT=production --release

# Open Xcode to archive and upload to App Store
open ios/Runner.xcworkspace
```

---

## 🎓 Code Examples

### Fetching Users with Pagination
```dart
import 'package:tsh_admin_security/services/user_service.dart';

final userService = UserService();

// Get paginated users
final response = await userService.getUsersPaginated(
  page: 1,
  pageSize: 20,
  search: 'ahmad',
  isActive: true,
);

print('Total users: ${response.total}');
print('Loaded ${response.users.length} users');

// Navigate pages
if (response.hasNextPage) {
  final nextPage = await userService.getUsersPaginated(page: 2);
}
```

### Checking Zoho Sync Status
```dart
import 'package:tsh_admin_security/models/user.dart';

User user = /* ... */;

// Check if synced
if (user.isSyncedWithZoho) {
  print('User is synced with Zoho');
  print('Zoho ID: ${user.zohoUserId}');
  print('Last sync: ${user.zohoLastSync}');
  print('Status: ${user.syncStatusMessage}');
} else {
  print('User is not synced with Zoho');
}
```

### Creating New User
```dart
final newUser = await userService.createUser({
  'name': 'New User',
  'email': 'newuser@tsh.sale',
  'password': 'secure_password',
  'role_id': 2,
  'branch_id': 1,
  'phone': '+964 770 123 4567',
  'is_active': true,
});

print('Created user with ID: ${newUser.id}');
```

---

## 📊 Performance Tips

### Optimize List Rendering
- Use ListView.builder for large lists
- Implement infinite scroll pagination
- Cache frequently accessed data

### Network Optimization
- Use connection pooling
- Implement request debouncing
- Cache API responses

### Memory Management
- Dispose controllers properly
- Clear large lists when not needed
- Use weak references for callbacks

---

## 🆘 Support & Resources

### Documentation
- Full Integration Report: `INTEGRATION_REPORT.md`
- Backend API Docs: `https://erp.tsh.sale/docs`
- Project Architecture: `../../ARCHITECTURE.md`

### Getting Help
1. Check INTEGRATION_REPORT.md for detailed info
2. Review console logs for error details
3. Test on staging before production
4. Contact backend team for API issues

---

## ✅ Pre-Launch Checklist

- [ ] Tested on staging environment
- [ ] All CRUD operations working
- [ ] Pagination tested with 500+ users
- [ ] Search functionality verified
- [ ] Zoho sync status displaying correctly
- [ ] Error handling tested
- [ ] Authentication/logout working
- [ ] Built production APK/iOS successfully
- [ ] Performance tested (no lag)
- [ ] Security audit completed

---

**Last Updated:** 2025-11-16
**Version:** 2.0.0
**Status:** Production Ready
