# iOS Certificates & Development Configuration

## Critical Signing & Asset Issues Fixed (September 26, 2025)

**Critical Issues Identified:**
- 🚨 **No Account for Team "3BJB4453J5"** - Team ID mismatch with available certificates
- 🚨 **No provisioning profiles for 'com.tsh.admin'** - Missing development profiles
- 🚨 **Missing Assets.xcassets** - Failed to read file attributes
- 🚨 **Missing AppIcon** - No matching app icon set named "AppIcon"
- ⚠️ **permission_handler_apple** deprecation warnings

**Emergency Fixes Applied:**
1. **Team ID Update:** Changed from `3BJB4453J5` → `38U844SAJ5` (available certificate)
2. **Assets Recreation:** 
   - Created `Assets.xcassets/AppIcon.appiconset/Contents.json`
   - Created `Assets.xcassets/LaunchImage.imageset/` with placeholders
3. **Available Certificates:**
   - Apple Development: Khaleel Ahmed (53P8RSV68A)
   - Apple Distribution: Khaleel Ahmed (38U844SAJ5)
4. **Bundle ID:** Kept as `com.tsh.admin` (needs provisioning profile)

**Status:** ⚠️ Partially resolved - need to create provisioning profile for com.tsh.admin

## Flutter Plugin Configuration Fixed (September 26, 2025)

**New Issues Identified:**
- ❌ Multiple Flutter plugin configuration errors (flutter_secure_storage, path_provider_foundation, etc.)
- ❌ iOS Deployment Target mismatch (9.0 vs required 12.0)
- ❌ MODULEMAP_FILE missing definitions
- ❌ CocoaPods base configuration conflicts

**Comprehensive Fix Applied:**
1. **Complete Deep Clean:** Removed all caches, DerivedData, Pods, and build artifacts
2. **Podfile Rewrite:** Complete rewrite with modern specifications:
   - Platform: iOS 12.0
   - use_modular_headers! enabled
   - Proper post_install deployment target enforcement
3. **CocoaPods:** Clean deintegration and reinstallation with --clean-install
4. **Project Settings:** Unified iOS deployment target to 12.0 across all configurations
5. **Flutter Dependencies:** Complete dependency refresh and verification

**Status:** ✅ All plugin configuration errors resolved, iOS deployment target unified

## Xcode Issues Fixed (September 26, 2025)

**Issues Identified:**
- ❌ "Unable to initiate PIF transfer session" dependency graph errors
- ❌ "Update to recommended settings" warnings for Runner and Pods
- ❌ Platform not specified in Podfile
- ❌ CocoaPods configuration conflicts

**Solutions Applied:**
1. **Deep Clean:** Removed all build artifacts, pods, and symlinks
2. **Podfile Fix:** Added explicit iOS 12.0 platform specification
3. **Dependencies:** Complete CocoaPods deintegration and reinstallation
4. **Project Settings:** 
   - iOS Deployment Target: 12.0
   - Bundle Identifier: com.tsh.admin
   - Development Team: 3BJB4453J5
   - Code Sign Style: Automatic

**Commands Used:**
```bash
cd /Users/khaleelal-mulla/Desktop/TSH\ ERP\ System/frontend/tsh_admin_dashboard
./fix_xcode_issues.sh
```

# iOS Certificates & Development Configuration

## Certificate Regeneration (September 26, 2025)

### Issue Resolved
- **Problem:** White screen on iOS app due to codesigning issues
- **Root Cause:** Certificate/Team ID mismatch and Flutter.framework signing failures
- **Solution:** Generated fresh Certificate Signing Request (CSR) and reconfigured project

### New Certificate Generation Process
1. **CSR Generated:** `/Users/khaleelal-mulla/Desktop/ios_certificates/TSH_iOS_Certificate_Request.csr`
2. **Private Key:** `TSH_iOS_Private_Key.key` (securely stored)
3. **Bundle ID Updated:** Changed from `com.tsh.tshAdminDashboard` to `com.tsh.admin`

### Setup Files Created
- `generate_csr.sh` - Generates Certificate Signing Request
- `setup_ios_certificates.sh` - Complete project configuration
- `README.md` - Step-by-step guide

### Required Actions
1. Upload CSR to Apple Developer Portal
2. Download and install new development certificate
3. Create/verify App ID: `com.tsh.admin`
4. Create development provisioning profile
5. Test build with: `flutter build ios --device-id 00008130-0004310C1ABA001C`

## Apple Developer Account Details
- **Developer Name:** Khaleel Ahmed
- **Team ID:** 3BJB4453J5
- **Account Type:** Individual Developer Account

## Certificates

### 1. Development Certificate
- **Type:** Apple Development
- **Subject:** Apple Development: Khaleel Ahmed (S3PRSVGBA)
- **Organizational Unit:** 3BJB4453J5
- **Serial Number:** 59 C1 6F A2 E4 9A 5D C4 7A 31 5A D5 23 FE 79 53
- **Valid From:** Thursday, 25 September 2025 at 7:32:54 PM AST
- **Valid Until:** Friday, 25 September 2026 at 7:32:54 PM AST
- **Usage:** Code signing for development, testing on devices
- **Algorithm:** RSA Encryption (1.2.840.113549.1.1.1)
- **Key Size:** 2,048 bits

### 2. Distribution Certificate
- **Type:** Apple Distribution
- **Subject:** Apple Distribution: Khaleel Ahmed (3BJB4453J5)
- **Organizational Unit:** 3BJB4453J5
- **Serial Number:** 72 86 CF 68 0B FB 2B 8E 7B 52 5F 08 77 71 67 D0
- **Valid From:** Thursday, 25 September 2025 at 7:34:21 PM AST
- **Valid Until:** Friday, 25 September 2026 at 7:34:20 PM AST
- **Usage:** Code signing for App Store distribution
- **Algorithm:** RSA Encryption (1.2.840.113549.1.1.1)
- **Key Size:** 2,048 bits

## App Configuration

### TSH Admin App
- **App ID:** TSH Admin (com.tsh.admin)
- **Bundle Identifier:** com.tsh.admin (explicit)
- **Platform:** iOS, iPadOS, macOS, tvOS, watchOS, visionOS
- **Description:** TSH Admin
- **Capabilities:**
  - In-App Purchase (enabled)

### Provisioning Profiles
1. **Development Profile:**
   - Name: TSH Admin Dev Profile
   - Type: Development
   - Platform: iOS
   - App ID: TSH Admin (com.tsh.admin)
   - Expires: 2026/09/25

2. **Distribution Profile:**
   - Name: TSH Admin Distribution Profile
   - Type: App Store
   - Platform: iOS
   - App ID: TSH Admin (com.tsh.admin)
   - Expires: 2026/09/25

## Registered Devices
- **Device:** khaleel_ahm@yahoo.com - iPhone 15 Pro Max
- **UDID:** 00008130-000431C1ABA001C
- **Type:** iPhone
- **Date Registered:** 2025/05/27

## API Keys
1. **Sign in with Apple Key**
   - Key ID: WJV4M5YR67
   - Created: 2020/05/11
   - Updated: 2020/05/16

2. **Firebase Notifications Key**
   - Key ID: 8MFTNDVNN7
   - Name: Firebase Noti
   - Created: 2020/05/05
   - Updated: 2020/05/05
   - Team Scoped: All topics
   - Environment: Sandbox & Production

## Certificate Installation Instructions

### For Development:
1. Download the development certificate from Apple Developer Portal
2. Double-click to install in Keychain Access
3. Ensure the private key is also installed
4. In Xcode, select the development certificate for debug builds

### For Distribution:
1. Download the distribution certificate from Apple Developer Portal
2. Double-click to install in Keychain Access
3. Ensure the private key is also installed
4. In Xcode, select the distribution certificate for release/archive builds

## Security Notes
- Certificates expire on September 25, 2026
- Both certificates use RSA 2048-bit encryption
- Private keys should be securely backed up
- Certificates are issued by Apple Worldwide Developer Relations Certification Authority

## Next Steps
1. Update Xcode project bundle identifier to match Apple Developer Account (com.tsh.admin)
2. Configure code signing settings in Xcode
3. Download and install provisioning profiles
4. Test development build on registered device
5. Prepare for App Store submission with distribution certificate
