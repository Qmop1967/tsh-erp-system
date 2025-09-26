# 🔧 TSH Admin App - Connectivity Troubleshooting Guide

## ✅ What We've Fixed

### 1. **Network Configuration**
- ✅ Updated app to use Mac IP address: `192.168.0.237:8000`
- ✅ Created `lib/config/environment.dart` with correct API endpoint
- ✅ Fixed main.dart imports

### 2. **iOS App Transport Security (ATS)**
- ✅ Updated `ios/Runner/Info.plist` to allow HTTP connections
- ✅ Added exception for your Mac's IP address (192.168.0.237)
- ✅ Configured NSAllowsArbitraryLoads for development

### 3. **Backend Server**
- ✅ Started FastAPI server on `0.0.0.0:8000` (accessible from network)
- ✅ Server running and accessible from iPhone at `http://192.168.0.237:8000`

### 4. **iPhone Connection**
- ✅ iPhone 15 Pro Max detected wirelessly: `00008130-0004310C1ABA001C`
- ✅ App being redeployed with updated network configuration

## 🔍 How to Verify the Fix

### Step 1: Check Backend Server
```bash
# From your Mac terminal:
curl http://192.168.0.237:8000/docs
# Should show the API documentation
```

### Step 2: Test from iPhone Safari
1. Open Safari on your iPhone
2. Go to: `http://192.168.0.237:8000/docs`
3. You should see the TSH ERP API documentation

### Step 3: Check App Connectivity
1. Open the TSH Admin Dashboard app on your iPhone
2. The app should now connect to your Mac's backend server
3. Check for successful API calls in the app

## 🚨 If Still Not Working

### Common Issues & Solutions:

#### 1. **Firewall Blocking Connection**
```bash
# Check Mac firewall status
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# If firewall is on, add Python/uvicorn to exceptions
# Or temporarily disable: System Preferences > Security & Privacy > Firewall
```

#### 2. **WiFi Network Issues**
- Ensure both Mac and iPhone are on the same WiFi network
- Some corporate networks block device-to-device communication
- Try using a personal hotspot or home WiFi

#### 3. **Port 8000 Already in Use**
```bash
# Check what's using port 8000
lsof -i :8000

# Kill existing processes if needed
kill -9 [PID]
```

#### 4. **App Cache Issues**
On iPhone:
1. Double-tap home button
2. Swipe up on TSH Admin app to force close
3. Reopen the app

#### 5. **Certificate Trust Issues**
On iPhone:
1. Settings → General → VPN & Device Management
2. Find your Developer App certificate
3. Tap "Trust [Your Developer Name]"

## 🔄 Complete Reset Process

If the app still isn't working, follow these steps:

### 1. **Restart Backend Server**
```bash
# Stop current server (Ctrl+C in terminal)
# Then restart:
cd "/Users/khaleelal-mulla/Desktop/TSH ERP System"
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. **Force Rebuild and Redeploy App**
```bash
cd "/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"
flutter clean
flutter pub get
flutter run -d 00008130-0004310C1ABA001C
```

### 3. **Network Diagnostics**
```bash
# Test if iPhone can reach Mac
ping 192.168.0.237

# Test if port 8000 is accessible
nc -zv 192.168.0.237 8000
```

## 📱 Current Configuration Summary

- **Mac IP**: 192.168.0.237
- **Backend Server**: http://192.168.0.237:8000
- **iPhone Device ID**: 00008130-0004310C1ABA001C
- **App Bundle ID**: com.tsh.admin.tshAdminDashboard
- **Connection Type**: Wireless (WiFi)

## 🎯 Next Steps

1. **Wait for current deployment to complete**
2. **Test app connectivity on your iPhone**
3. **If successful**: App should now load and connect to backend
4. **If still failing**: Use the troubleshooting steps above

## 📞 Quick Commands for Future Use

```bash
# Start backend server
cd "/Users/khaleelal-mulla/Desktop/TSH ERP System"
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Deploy to iPhone
cd "/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"
flutter run -d 00008130-0004310C1ABA001C

# Check connected devices
flutter devices
```
