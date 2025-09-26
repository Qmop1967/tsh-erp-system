# iOS Certificate Generation & Setup Guide

## Files Generated
- `TSH_iOS_Private_Key.key` - Your private key (KEEP SECURE!)
- `TSH_iOS_Certificate_Request.csr` - Certificate Signing Request for Apple

## Apple Developer Portal Steps

### 1. Create Development Certificate
1. Go to: https://developer.apple.com/account/resources/certificates/list
2. Click "+" to add new certificate
3. Select "Apple Development"
4. Upload `TSH_iOS_Certificate_Request.csr`
5. Download the certificate and double-click to install

### 2. Verify/Create App ID
1. Go to: https://developer.apple.com/account/resources/identifiers/list
2. Ensure App ID exists: `com.tsh.admin`
3. If not, create new App ID with this Bundle ID

### 3. Create Provisioning Profile
1. Go to: https://developer.apple.com/account/resources/profiles/list
2. Create new "Development" profile
3. Select App ID: `com.tsh.admin`
4. Select your development certificate
5. Select your device: `00008130-000431C1ABA001C`
6. Download and install

## Project Configuration
The setup script will automatically:
- Update bundle identifier to `com.tsh.admin`
- Update display name to "TSH Admin"
- Configure Xcode project settings

## Testing
After setup, test with:
```bash
cd "/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"
flutter clean
flutter build ios --device-id 00008130-0004310C1ABA001C
```

## Troubleshooting
- If signing fails, check Keychain Access for certificate and private key
- Verify Team ID matches: `3BJB4453J5`
- Ensure device is registered with UDID: `00008130-000431C1ABA001C`
