# TSH Consumer App - APK Build Instructions

## Method 1: GitHub Actions (RECOMMENDED - No Local Setup Required!)

GitHub Actions will automatically build the Android APK for you in the cloud.

### How to Use GitHub Actions:

**Step 1: Push the workflow file to GitHub**
```bash
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem/mobile/flutter_apps/10_tsh_consumer_app
git add .github/workflows/build-apk.yml
git commit -m "Add GitHub Actions workflow for Android APK build"
git push
```

**Step 2: Trigger the build manually**
1. Go to your GitHub repository
2. Click on the **Actions** tab
3. Click on **Build Android APK** workflow
4. Click **Run workflow** button
5. Select the branch (main/master)
6. Click **Run workflow**

**Step 3: Wait for build to complete (3-5 minutes)**
- Watch the build progress in real-time
- Green checkmark = Success!
- Red X = Failed (check logs)

**Step 4: Download the APK**
1. Click on the completed workflow run
2. Scroll down to **Artifacts** section
3. Click on `tsh-consumer-app-release` to download
4. Extract the ZIP file
5. You'll find `app-release.apk` inside

**Step 5: Share via WhatsApp**
- Send the APK file directly via WhatsApp
- Or upload to Google Drive and share the link

---

## Method 2: Build Locally (Requires Xcode License)

### Prerequisites:
1. Accept Xcode license:
```bash
sudo xcodebuild -license
```

### Build Commands:
```bash
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem/mobile/flutter_apps/10_tsh_consumer_app

# Install dependencies
flutter pub get

# Build APK
flutter build apk --release
```

### APK Location:
```
/Users/khaleelal-mulla/TSH_ERP_Ecosystem/mobile/flutter_apps/10_tsh_consumer_app/build/app/outputs/flutter-apk/app-release.apk
```

---

## Method 3: Use Build Script

Run the automated build script:
```bash
/Users/khaleelal-mulla/TSH_ERP_Ecosystem/mobile/flutter_apps/10_tsh_consumer_app/build_android_apk.sh
```

This script will:
- Clean previous builds
- Install dependencies
- Build the APK
- Open Finder at the APK location

---

## APK Details

**App Name:** TSH Consumer App
**Package:** com.tsh.consumer_app
**Version:** 1.0.0+1
**APK Size:** ~15-30 MB
**Target:** Android 5.0 (API 21) and above

---

## Distribution via WhatsApp

### Option A: Direct Share
1. Locate `app-release.apk`
2. Right-click → Share → WhatsApp
3. Select contacts or groups
4. Send!

### Option B: Cloud Link
1. Upload APK to Google Drive/Dropbox
2. Get shareable link
3. Share link via WhatsApp
4. Team members download and install

### Option C: AirDrop (Mac to iPhone)
1. AirDrop APK to your iPhone
2. Share via WhatsApp from iPhone

---

## Installation on Android Devices

**Steps for team members:**
1. Download the APK file
2. Go to **Settings → Security → Unknown Sources**
3. Enable **"Allow installation from unknown sources"**
4. Open the APK file
5. Tap **Install**
6. Open TSH Consumer App

**Note:** Users may see a warning - this is normal for apps not from Google Play Store.

---

## Automatic Builds

The GitHub Actions workflow is configured to:
- ✅ Build APK automatically when you push code changes to `lib/` or `android/` directories
- ✅ Build APK when you manually trigger the workflow
- ✅ Create a release with APK attached when you push a git tag (e.g., `v1.0.1`)

To create a tagged release:
```bash
git tag -a v1.0.1 -m "Release version 1.0.1"
git push origin v1.0.1
```

The APK will be automatically attached to the GitHub release.

---

## Troubleshooting

**Issue:** Xcode license error
**Fix:** Run `sudo xcodebuild -license` and type `agree`

**Issue:** Flutter not found
**Fix:** Ensure Flutter is installed and in PATH

**Issue:** Build fails with Gradle error
**Fix:** Clean build with `flutter clean` then rebuild

**Issue:** APK too large (>30MB)
**Fix:** Already optimized with `--release` flag

---

## Support

For issues or questions, contact the development team.

**Workflow Status:** Check the Actions tab on GitHub for build status.
**APK Downloads:** Available in Artifacts section of each successful build.
