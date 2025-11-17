# Apple Push Notification Service (APNS) Setup Guide

This guide explains how to configure APNS for the TSH Security Console iOS app.

## Prerequisites

1. **Apple Developer Account** (Apple Developer Program membership required)
2. **App ID with Push Notification capability** enabled
3. **APNS Authentication Key** (.p8 file)

## Step 1: Create APNS Key in Apple Developer Portal

1. Go to [Apple Developer Portal](https://developer.apple.com/account)
2. Navigate to **Certificates, Identifiers & Profiles**
3. Go to **Keys** section
4. Click **+** to create a new key
5. Enter a name: `TSH Security Console APNS Key`
6. Check **Apple Push Notifications service (APNs)**
7. Click **Continue** and then **Register**
8. **IMPORTANT**: Download the `.p8` file immediately (you can only download it once)
9. Note down:
   - **Key ID**: Displayed on the key details page
   - **Team ID**: Found in Membership section

## Step 2: Configure App ID

1. In **Identifiers** section, select your App ID (e.g., `com.tsh.securityconsole`)
2. Enable **Push Notifications** capability
3. Save changes

## Step 3: Configure Backend Environment

### Option A: Using .p8 Key File (Recommended)

```bash
# In your .env file or environment
APNS_ENABLED=true
APNS_PRODUCTION=false  # Set to true for App Store builds
APNS_TEAM_ID=YOUR_TEAM_ID_FROM_PORTAL
APNS_KEY_ID=YOUR_KEY_ID_FROM_STEP_1
APNS_BUNDLE_ID=com.tsh.securityconsole
APNS_KEY_PATH=/path/to/AuthKey_KEYID.p8
```

### Option B: Using Key Content (Docker/Kubernetes)

```bash
# Inline key content
APNS_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg...
-----END PRIVATE KEY-----"
```

## Step 4: iOS App Configuration

### Info.plist

Add these entries:

```xml
<key>UIBackgroundModes</key>
<array>
    <string>remote-notification</string>
</array>
```

### Capabilities in Xcode

1. Open project in Xcode
2. Select target → **Signing & Capabilities**
3. Click **+ Capability**
4. Add **Push Notifications**
5. Add **Background Modes** and enable **Remote notifications**

### Provisioning Profile

Ensure your provisioning profile includes Push Notifications entitlement.

## Step 5: Testing

### Sandbox Testing (Development)

```bash
# Set in backend .env
APNS_PRODUCTION=false
```

- Use Development provisioning profile
- Connect real iOS device (simulators don't support push)
- Build and run from Xcode

### Production Testing

```bash
# Set in backend .env
APNS_PRODUCTION=true
```

- Use Distribution/App Store provisioning profile
- TestFlight or App Store build

## Step 6: Verify Configuration

### Backend Health Check

```bash
# Check if APNS is configured
curl -X GET http://localhost:8000/health | jq .apns_status
```

### Test Push Notification

```python
# Python test script
from app.neurolink.app.services.apns_delivery import apns_service

# Test with your device token
result = await apns_service.send_notification(
    device_token="YOUR_DEVICE_TOKEN_HERE",
    title="Test Notification",
    body="APNS is working!",
    badge=1
)
print(result)
```

## Troubleshooting

### Common Errors

1. **BadDeviceToken**
   - Token format is wrong or token is for different environment (sandbox vs production)
   - Ensure device token matches environment (development vs production)

2. **TooManyRequests**
   - Rate limit exceeded
   - Implement exponential backoff

3. **Unregistered**
   - User uninstalled app or disabled notifications
   - Remove token from database

4. **InvalidProviderToken**
   - JWT token expired or invalid
   - Check APNS_TEAM_ID and APNS_KEY_ID
   - Verify .p8 key is correct

5. **BadPath**
   - Device token in URL is malformed
   - Must be 64 hex characters

### Token Format

APNS device tokens should be:
- 64 hexadecimal characters
- No spaces or angle brackets
- Example: `740f4707bebcf74f9b7c25d48e3358945f6aa01da5ddb387462c7eaf61bb78ad`

## Security Best Practices

1. **Never commit .p8 file to version control**
2. Store key securely (AWS Secrets Manager, Vault, etc.)
3. Rotate keys periodically
4. Monitor failed delivery rates
5. Implement token cleanup for unregistered devices

## Production Checklist

- [ ] APNS_PRODUCTION=true
- [ ] Team ID verified
- [ ] Key ID verified
- [ ] .p8 key securely stored
- [ ] Bundle ID matches App Store submission
- [ ] Distribution provisioning profile configured
- [ ] Background modes enabled in capabilities
- [ ] Notification permission requested on first launch
- [ ] Error handling for notification permission denied
- [ ] Token registration on login
- [ ] Token cleanup on logout
- [ ] Token refresh on app update

## Related Files

- **APNS Service**: `/app/neurolink/app/services/apns_delivery.py`
- **Owner Notification Service**: `/app/services/owner_notification_service.py`
- **iOS Notification Service**: `TSHSecurityConsole/Services/NotificationService.swift`
- **iOS App Delegate**: `TSHSecurityConsole/App/AppDelegate.swift`
- **Environment Config**: `/app/neurolink/.env.example`

## Apple Documentation

- [Setting Up a Remote Notification Server](https://developer.apple.com/documentation/usernotifications/setting_up_a_remote_notification_server)
- [Sending Notification Requests to APNs](https://developer.apple.com/documentation/usernotifications/setting_up_a_remote_notification_server/sending_notification_requests_to_apns)
- [Establishing a Token-Based Connection to APNs](https://developer.apple.com/documentation/usernotifications/setting_up_a_remote_notification_server/establishing_a_token-based_connection_to_apns)
