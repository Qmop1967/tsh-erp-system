# App Icon Setup Instructions

## TSH Sales Hub App Icon

### Step 1: Save the Logo Image

Please save the TSH Sales Hub logo image you provided to:
```
/Users/khaleelal-mulla/TSH_ERP_System_Local/tsh_salesperson_app/assets/icons/app_icon.png
```

**Requirements:**
- Format: PNG with transparency
- Recommended size: 1024x1024 pixels (minimum)
- Square aspect ratio
- Transparent or white background works best

### Step 2: Install Dependencies and Generate Icons

After saving the image, run the following commands:

```bash
cd /Users/khaleelal-mulla/TSH_ERP_System_Local/tsh_salesperson_app

# Install the flutter_launcher_icons package
flutter pub get

# Generate app icons for all platforms
flutter pub run flutter_launcher_icons
```

### Step 3: Verify Icon Generation

The script will generate icons for:
- ✅ iOS (multiple sizes in ios/Runner/Assets.xcassets/AppIcon.appiconset/)
- ✅ Android (various densities in android/app/src/main/res/)
- ✅ Web (favicon and web app icons)

### Step 4: Rebuild the App

After generating icons, clean and rebuild:

```bash
flutter clean
flutter run
```

## Alternative: Using Online Tool

If you prefer, you can also:

1. Go to: https://www.appicon.co/ or https://easyappicon.com/
2. Upload your TSH logo
3. Download the generated icon pack
4. Manually place icons in the appropriate folders:
   - iOS: `ios/Runner/Assets.xcassets/AppIcon.appiconset/`
   - Android: `android/app/src/main/res/mipmap-*/`

## Quick Command (After Image is Saved)

Run this command to set up everything:

```bash
cd /Users/khaleelal-mulla/TSH_ERP_System_Local/tsh_salesperson_app && \
flutter pub get && \
flutter pub run flutter_launcher_icons && \
echo "✅ App icons generated successfully!"
```

## Current Configuration

The pubspec.yaml has been updated with:
- Package: `flutter_launcher_icons: ^0.13.1`
- Image path: `assets/icons/app_icon.png`
- Background color: #1976D2 (TSH Blue)
- Platforms: iOS, Android, Web

## Troubleshooting

### Issue: Image not found
**Solution**: Make sure the image is saved to exactly `assets/icons/app_icon.png`

### Issue: Icons not updating on device
**Solution**: 
```bash
flutter clean
flutter pub cache clean
flutter pub get
flutter pub run flutter_launcher_icons
flutter run
```

### Issue: iOS icons not showing
**Solution**: In Xcode, clean build folder (Cmd+Shift+K) and rebuild

## Current Status

- ✅ Configuration added to pubspec.yaml
- ✅ Assets folder created
- ⏳ **ACTION REQUIRED**: Save the TSH logo to `assets/icons/app_icon.png`
- ⏳ **ACTION REQUIRED**: Run `flutter pub run flutter_launcher_icons`

---

**Note**: The TSH Sales Hub logo you provided is perfect for the app icon. Its circular design with the handshake and network motif represents the sales and connectivity aspects beautifully.
