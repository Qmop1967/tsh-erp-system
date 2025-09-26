# 🍎 TSH Admin App - iOS Certificate & Deployment Guide

## 📋 Overview
This guide will help you update certificates, provisioning profiles, and deploy the TSH Admin app to your iPhone 15 Pro Max wirelessly.

## 🔐 Certificate Management

### Step 1: Download New Certificates from Apple Developer
1. Go to [Apple Developer Portal](https://developer.apple.com/account/)
2. Navigate to **Certificates, Identifiers & Profiles**
3. Download the following files:

#### Required Files:
- **Development Certificate** (.cer file)
- **Provisioning Profile** (.mobileprovision file)
- **Private Key** (.p12 file) - Export from Keychain if needed

### Step 2: Place Files in Project
```
frontend/tsh_admin_dashboard/ios/
├── certificates/
│   ├── ios_development.p12
│   └── ios_development.cer
└── profiles/
    └── TSH_Admin_Development.mobileprovision
```

## ⚙️ Project Configuration Updates

### Current Configuration:
- **Bundle ID**: `com.tsh.admin.tshAdminDashboard`
- **Team ID**: `38U844SAJ5` (update if changed)
- **App Name**: TSH Admin Dashboard

### Update Team ID (if changed):
1. Open `ios/Runner.xcodeproj/project.pbxproj`
2. Find all instances of `DEVELOPMENT_TEAM = 38U844SAJ5`
3. Replace with your new Team ID

## 📱 iPhone 15 Pro Max Wireless Setup

### Prerequisites:
1. **Developer Mode Enabled**:
   - Settings → Privacy & Security → Developer Mode → ON
   - Restart iPhone when prompted

2. **Trust Computer**:
   - Connect via USB first
   - Trust this computer when prompted

### Wireless Debugging Setup:
1. **Connect iPhone via USB**
2. **Open Xcode** → Window → Devices and Simulators
3. **Select your iPhone 15 Pro Max**
4. **Check ✅ "Connect via network"**
5. **Wait for WiFi icon** to appear next to device
6. **Disconnect USB** - wireless connection active!

## 🚀 Deployment Commands

### Method 1: Using Flutter (Recommended)
```bash
cd frontend/tsh_admin_dashboard
flutter devices                    # Check connected devices
flutter run -d [DEVICE_ID]        # Deploy to specific device
```

### Method 2: Using Xcode
1. Open `ios/Runner.xcworkspace` in Xcode
2. Select your iPhone from device dropdown
3. Press ▶️ Run or Cmd+R

### Method 3: Using Our Script
```bash
./update_certificates.sh
# Choose option 4 or 5 for deployment
```

## 🔧 Troubleshooting

### Common Issues:

#### "No devices found"
```bash
# Check USB connection and trust
flutter doctor -v
xcrun devicectl list devices
```

#### "Code signing failed"
1. Open Xcode
2. Select Runner target
3. Go to Signing & Capabilities
4. Update Team and Bundle ID
5. Let Xcode auto-manage signing

#### "App not launching on device"
1. Check iPhone Settings → General → VPN & Device Management
2. Trust your developer profile
3. Enable Developer Mode if disabled

### Device Detection Commands:
```bash
# Flutter device check
flutter devices

# iOS device check  
xcrun devicectl list devices

# System device info
system_profiler SPUSBDataType | grep iPhone
```

## 📂 File Structure After Setup
```
tsh_admin_dashboard/
├── ios/
│   ├── certificates/
│   │   ├── ios_development.p12
│   │   └── ios_development.cer
│   ├── profiles/
│   │   └── TSH_Admin_Development.mobileprovision
│   └── Runner.xcodeproj/
├── update_certificates.sh
└── ios_deployment_guide.md
```

## 🎯 Quick Deployment Checklist

- [ ] New certificates downloaded from Apple Developer
- [ ] Files placed in certificates/ and profiles/ directories  
- [ ] Team ID updated in Xcode project (if changed)
- [ ] iPhone 15 Pro Max connected and trusted
- [ ] Developer Mode enabled on iPhone
- [ ] Wireless debugging configured (optional)
- [ ] App successfully builds and deploys

## 🆘 Support Commands

If you encounter issues, run these diagnostic commands:

```bash
# Check Flutter installation
flutter doctor -v

# Check iOS setup
flutter doctor --verbose

# Check connected devices
flutter devices -v

# Check iOS device connection
xcrun devicectl list devices --include-locked

# Check Xcode command line tools
xcode-select --print-path
```

---

## 📞 Next Steps
1. Run `./update_certificates.sh` to start the process
2. Follow the prompts to update certificates
3. Use Xcode to verify signing configuration  
4. Deploy wirelessly to your iPhone 15 Pro Max
