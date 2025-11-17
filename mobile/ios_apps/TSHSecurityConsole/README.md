# TSH Security Console - iOS App

**Native iOS application for TSH ERP Owner/Director security monitoring and approval management.**

---

## Overview

The TSH Security Console is a specialized iOS application designed exclusively for Owner/Director level access. It provides real-time security monitoring, sensitive operation approval workflows, and comprehensive oversight of the TSH ERP ecosystem.

### Key Features

- **Security Dashboard**: Real-time security metrics, threat levels, and system health
- **Owner Approval System**: Approve/deny sensitive operations with 6-digit codes or QR scanning
- **Session Management**: Monitor and terminate active user sessions
- **User Management**: View and manage system users
- **Biometric Authentication**: Face ID / Touch ID support for sensitive actions
- **Push Notifications**: Real-time alerts via TSH NeuroLink
- **Arabic/English Localization**: Full RTL support for Arabic

---

## Architecture

### Tech Stack

- **Language**: Swift 5.9+
- **UI Framework**: SwiftUI
- **Minimum iOS**: 16.0
- **Architecture Pattern**: MVVM (Model-View-ViewModel)
- **Networking**: async/await with URLSession
- **Security**: Keychain for token storage
- **Authentication**: JWT Bearer tokens

### Project Structure

```
TSHSecurityConsole/
├── App/
│   ├── TSHSecurityConsoleApp.swift    # App entry point
│   ├── AppDelegate.swift              # Push notification handling
│   └── ContentView.swift              # Main tab navigation
├── Core/
│   ├── Network/
│   │   └── APIClient.swift            # Network layer with retry logic
│   ├── Storage/
│   │   └── KeychainService.swift      # Secure credential storage
│   ├── Security/
│   │   └── BiometricAuth.swift        # Face ID/Touch ID
│   └── Localization/
│       ├── en.lproj/Localizable.strings
│       └── ar.lproj/Localizable.strings
├── Models/
│   ├── User.swift                     # User and auth models
│   ├── Approval.swift                 # Approval request models
│   └── Session.swift                  # Session and dashboard models
├── Services/
│   ├── AuthService.swift              # Authentication operations
│   ├── ApprovalService.swift          # Approval workflow operations
│   ├── SecurityService.swift          # Security dashboard operations
│   └── NotificationService.swift      # APNS token management
├── ViewModels/
│   ├── AuthViewModel.swift            # Authentication state management
│   ├── DashboardViewModel.swift       # Dashboard data management
│   └── ApprovalsViewModel.swift       # Approval list management
└── Views/
    ├── Auth/
    │   └── LoginView.swift            # Login screen
    ├── Dashboard/
    │   └── DashboardView.swift        # Security dashboard
    ├── Approvals/
    │   ├── ApprovalsListView.swift    # Pending approvals list
    │   └── QRScannerView.swift        # QR code scanning
    ├── Sessions/
    │   └── SessionsListView.swift     # Active sessions management
    ├── Users/
    │   └── UsersListView.swift        # User list
    └── Settings/
        └── SettingsView.swift         # App settings
```

---

## Backend Integration

### Required Backend Endpoints

The app integrates with these FastAPI endpoints:

#### Authentication
- `POST /api/auth/login/mobile` - Mobile login
- `POST /api/auth/mfa/verify-login` - MFA verification
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Current user info

#### Owner Approvals
- `POST /api/auth/owner/request-approval` - Request approval
- `GET /api/auth/owner/pending` - List pending approvals
- `GET /api/auth/owner/all` - All approvals with filters
- `GET /api/auth/owner/{id}` - Approval details
- `POST /api/auth/owner/approve` - Approve with code
- `POST /api/auth/owner/{id}/deny` - Deny request
- `POST /api/auth/owner/qr/scan` - QR scan approval
- `GET /api/auth/owner/stats/summary` - Approval statistics

#### Security BFF
- `GET /api/bff/security/dashboard` - Security dashboard data
- `GET /api/bff/security/sessions` - Active sessions
- `POST /api/bff/security/sessions/{id}/terminate` - Terminate session
- `GET /api/bff/security/audit-log` - Audit log

#### Users
- `GET /api/users` - User list

#### Notifications
- `POST /api/notifications/device-token` - Register APNS token

---

## Setup Instructions

### Prerequisites

1. **Xcode 15.0+** installed on macOS
2. **Apple Developer Account** (for device testing and push notifications)
3. **TSH ERP Backend** running and accessible

### Creating the Xcode Project

1. Open Xcode
2. Create new project: **File → New → Project**
3. Select **iOS → App**
4. Configure:
   - Product Name: `TSHSecurityConsole`
   - Team: Your Development Team
   - Organization Identifier: `com.tsh.security`
   - Interface: SwiftUI
   - Language: Swift
   - Storage: None (we use Keychain)

5. Add all source files from this directory to the project

### Configuring Capabilities

In Xcode, go to your target's **Signing & Capabilities**:

1. **Push Notifications**: Enable for APNS
2. **Keychain Sharing**: Enable for secure storage
3. **Background Modes**: Enable "Remote notifications"
4. **Camera Usage**: Required for QR scanning (add `NSCameraUsageDescription` to Info.plist)

### Info.plist Configuration

Add these keys:

```xml
<key>NSCameraUsageDescription</key>
<string>Camera access is required for QR code scanning to approve requests</string>

<key>NSFaceIDUsageDescription</key>
<string>Face ID is used to verify your identity for sensitive security operations</string>

<key>UIBackgroundModes</key>
<array>
    <string>remote-notification</string>
</array>
```

### API Configuration

Update the base URL in `APIClient.swift`:

```swift
private let baseURL = "https://erp.tsh.sale/api"  // Production
// private let baseURL = "https://staging.erp.tsh.sale/api"  // Staging
```

---

## Building and Running

### Simulator

```bash
# From Xcode
1. Select target device (iPhone 15 Pro recommended)
2. Press Cmd + R or click Run

# From command line
xcodebuild -scheme TSHSecurityConsole -destination 'platform=iOS Simulator,name=iPhone 15 Pro' build
```

### Physical Device

1. Connect your iPhone
2. Select your device in Xcode
3. Ensure signing is configured
4. Press Cmd + R

### Testing Push Notifications

Push notifications require:
1. Physical device (not simulator)
2. Valid APNS certificate
3. Backend configured to send via TSH NeuroLink

---

## Security Considerations

### Authentication
- JWT tokens stored in iOS Keychain (hardware-encrypted)
- Automatic token refresh on 401 responses
- Token blacklist checking on backend
- Session timeout enforcement

### Biometric Security
- Face ID / Touch ID for sensitive operations
- Required for approval actions
- Graceful fallback if unavailable

### Data Protection
- No sensitive data stored in UserDefaults
- Tokens cleared on logout
- Certificate pinning can be added for production

### Role Enforcement
- Only Owner/Admin/Director roles allowed
- Role check on both client and server
- Immediate logout if unauthorized

---

## Arabic/RTL Support

The app fully supports Arabic with RTL layout:

- Language toggle in Settings
- All text elements localized
- Layout direction automatically switches
- Arabic descriptions for approvals
- RTL-aware UI components

Toggle language in the app:
```swift
appState.toggleLanguage()  // Switches between Arabic/English
```

---

## Testing

### Unit Tests

Create test files in `TSHSecurityConsoleTests/`:

```swift
// Example: TestAuthService.swift
import XCTest
@testable import TSHSecurityConsole

class TestAuthService: XCTestCase {
    func testTokenValidation() async throws {
        // Test token storage and retrieval
        KeychainService.shared.saveAccessToken("test_token")
        XCTAssertEqual(KeychainService.shared.getAccessToken(), "test_token")
        KeychainService.shared.clearAll()
        XCTAssertNil(KeychainService.shared.getAccessToken())
    }
}
```

### UI Tests

```swift
// Example: TestLoginFlow.swift
import XCTest

class TestLoginFlow: XCTestCase {
    func testLoginScreen() throws {
        let app = XCUIApplication()
        app.launch()

        // Verify login elements exist
        XCTAssertTrue(app.textFields["Email"].exists)
        XCTAssertTrue(app.secureTextFields["Password"].exists)
        XCTAssertTrue(app.buttons["Login"].exists)
    }
}
```

---

## Deployment

### App Store Submission

1. Archive the app: **Product → Archive**
2. Validate the archive
3. Upload to App Store Connect
4. Complete app metadata (Arabic + English)
5. Submit for review

### TestFlight Distribution

1. Archive and upload
2. Add internal/external testers
3. Distribute beta builds

### Enterprise Distribution

For internal TSH deployment:
1. Use Ad Hoc or Enterprise provisioning
2. Distribute via MDM or web link

---

## Known Limitations

1. **QR Scanner**: Requires physical device with camera
2. **Push Notifications**: Require APNS certificate
3. **Biometrics**: Device must support Face ID or Touch ID
4. **Offline Mode**: Limited functionality without network

---

## Future Enhancements

1. **WebSocket**: Real-time dashboard updates
2. **Offline Queue**: Queue approvals when offline
3. **Widget**: Security status home screen widget
4. **Apple Watch**: Companion app for quick approvals
5. **Map View**: Geographic session visualization
6. **Advanced Analytics**: Detailed security reports

---

## Support

For issues or questions:

- **Backend Issues**: Check `/api/health` endpoint
- **Authentication**: Verify JWT token validity
- **Push Notifications**: Check APNS configuration
- **Performance**: Monitor API response times

---

## License

Proprietary - TSH ERP Ecosystem
Copyright 2025 TSH

---

**Version**: 1.0.0
**Last Updated**: 2025-01-15
**Author**: TSH Development Team
