# 📱 Launch TSH Salesperson App on iPhone

## Step 1: Connect Your iPhone

### Option A: USB Cable (Recommended)
1. **Connect your iPhone** to your Mac using a USB cable
2. **Unlock your iPhone**
3. If prompted, **tap "Trust This Computer"** on your iPhone
4. Enter your iPhone passcode when asked

### Option B: WiFi Connection
1. First connect via USB once (do Option A above)
2. Open **Xcode** → Go to **Window** → **Devices and Simulators**
3. Select your iPhone from the left sidebar
4. Check **"Connect via network"**
5. Wait for the network icon to appear next to your device
6. You can now disconnect the USB cable

## Step 2: Enable Developer Mode (iOS 16+)

If you haven't enabled Developer Mode yet:
1. On your iPhone, go to **Settings**
2. Scroll down to **Privacy & Security**
3. Tap **Developer Mode**
4. Toggle it **ON**
5. **Restart your iPhone** when prompted
6. After restart, go back and confirm enabling Developer Mode

## Step 3: Launch the App

Run this command:
```bash
cd /Users/khaleelal-mulla/TSH_ERP_System_Local/mobile/flutter_apps/salesperson
./launch_salesperson_iphone.sh
```

Or manually with Flutter:
```bash
cd /Users/khaleelal-mulla/TSH_ERP_System_Local/mobile/flutter_apps/salesperson
flutter run --debug
```

## 🎯 TSH Salesperson App Features

Once launched, you'll have access to:
- 👤 **Customer Management** - View and manage your customers
- 📍 **GPS Tracking** - Track sales visits and routes
- 📊 **Sales Analytics** - View your performance metrics
- 💰 **Order Processing** - Create and manage orders
- 📱 **Mobile-Optimized** - Full bilingual Arabic/English support

## Troubleshooting

### "No devices found"
- Make sure iPhone is unlocked
- Check USB cable is working
- Try disconnecting and reconnecting
- Restart Xcode if using WiFi connection

### "Developer Mode not enabled"
- Follow Step 2 above
- Restart your iPhone after enabling
- Confirm in Settings that it's enabled

### "Code signing error"
- Open `ios/Runner.xcworkspace` in Xcode
- Select your Apple Developer account in Signing & Capabilities
- Let Xcode automatically manage signing

### Need to rebuild?
```bash
flutter clean
flutter pub get
flutter run
```

## Quick Commands

**Check connected devices:**
```bash
flutter devices
```

**Run on specific device:**
```bash
flutter devices  # Get device ID
flutter run -d [DEVICE_ID]
```

**Hot reload while running:**
- Press `r` in the terminal to hot reload
- Press `R` to hot restart
- Press `q` to quit

---

**Ready to launch?** Connect your iPhone and run the launch script! 🚀
