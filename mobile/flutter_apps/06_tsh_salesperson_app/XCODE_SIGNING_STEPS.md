# 🔐 Xcode Code Signing - Step by Step Guide

## ✅ What's Already Done
- ✓ Fixed bundle identifier to `com.tsh.salesperson`
- ✓ Cleaned all build artifacts
- ✓ Configured automatic code signing
- ✓ Opened Xcode workspace for you
- ✓ Your iPhone is connected wirelessly (Device ID: 00008130-0004310C1ABA001C)

---

## 📱 Complete These Steps in Xcode (Takes 2 Minutes)

### STEP 1: Add Your Apple Account to Xcode

**If you already have an Apple account added in Xcode, SKIP to Step 2**

1. In Xcode menu bar → Click **Xcode** → **Settings** (or press `⌘,`)
2. Click the **Accounts** tab at the top
3. Click the **`+`** button at the bottom left
4. Select **Apple ID**
5. Enter your Apple ID email and password
6. Click **Sign In**
7. Close the Settings window

> 💡 **Note**: You can use ANY Apple ID - even a free one! You don't need a paid Apple Developer account for testing on your own device.

---

### STEP 2: Configure Signing in Your Project

**Now you should see the Xcode window with your project open.**

1. **Select the Project**
   - In the left sidebar (Project Navigator), click on **"Runner"** (the blue icon at the very top)

2. **Select the Target**
   - In the center panel under "TARGETS", click **"Runner"** (not "RunnerTests")

3. **Go to Signing Tab**
   - At the top of the center panel, click **"Signing & Capabilities"**

4. **Enable Automatic Signing**
   - Look for the checkbox: **☑ "Automatically manage signing"**
   - Make sure it's **CHECKED** ✓

5. **Select Your Team**
   - Under "Team", click the dropdown menu
   - You'll see options like:
     - "Your Name (Personal Team)" ← Use this if you have a free Apple ID
     - "Your Company Name" ← Use this if you have a paid developer account
   - **Select any available team**

6. **Verify Bundle Identifier**
   - Below the Team, you should see:
     - **Bundle Identifier**: `com.tsh.salesperson`
   - This should already be correct ✓

7. **Check for Success**
   - Below Bundle Identifier, you should see:
     - **Status**: ✓ with "Signing Certificate: Apple Development"
     - **Provisioning Profile**: "Xcode Managed Profile" or "iOS Team Provisioning Profile"
   - **NO red error messages** ✅

---

### STEP 3: Test Build (Optional but Recommended)

1. In Xcode menu bar → **Product** → **Build** (or press `⌘B`)
2. Wait for "Build Succeeded" message (should take 10-30 seconds)
3. If you see "Build Succeeded" → You're all set! ✅

---

### STEP 4: Close Xcode & Launch on iPhone

Once you've completed the above steps:

1. **Close Xcode** (or just leave it open, doesn't matter)

2. **Run the launch script**:
   ```bash
   cd /Users/khaleelal-mulla/TSH_ERP_System_Local/tsh_salesperson_app
   ./launch_on_iphone.sh
   ```

   OR run directly:
   ```bash
   flutter run -d 00008130-0004310C1ABA001C
   ```

---

## ❓ Troubleshooting

### "No account for team..."
- **Solution**: Go back to Step 1 and add your Apple ID to Xcode

### "No profiles found..."
- **Solution**: 
  1. Make sure "Automatically manage signing" is checked
  2. Select a team from the dropdown
  3. Wait a few seconds for Xcode to generate the profile

### "Failed to create provisioning profile..."
- **Solution**:
  1. Make sure you're connected to the internet
  2. Sign out and sign back into your Apple ID in Xcode Settings
  3. Try changing the Bundle Identifier slightly (e.g., `com.tsh.salesperson2`) and back

### "Device not trusted"
- **Solution** On your iPhone:
  1. Go to **Settings** → **General** → **VPN & Device Management** (or **Device Management**)
  2. Tap your Apple ID / Developer name
  3. Tap **"Trust [Your Name]"**
  4. Tap **"Trust"** again to confirm

### "Developer Mode not enabled" (iOS 16+)
- **Solution** On your iPhone:
  1. Go to **Settings** → **Privacy & Security** → **Developer Mode**
  2. Toggle **ON**
  3. Restart your iPhone when prompted
  4. After restart, confirm Developer Mode activation

---

## 🎯 Quick Reference

| Item | Value |
|------|-------|
| **App Name** | TSH Salesperson |
| **Bundle ID** | com.tsh.salesperson |
| **iPhone Device ID** | 00008130-0004310C1ABA001C |
| **Xcode Workspace** | `ios/Runner.xcworkspace` |
| **Launch Script** | `./launch_on_iphone.sh` |

---

## 💡 Understanding Free vs Paid Apple Developer

### Free Apple ID (Personal Team)
- ✓ Free to use
- ✓ Can test on your own devices
- ✗ Apps expire after 7 days (need to reinstall)
- ✗ Limited to 3 apps per device
- ✗ Cannot distribute via TestFlight or App Store

### Paid Apple Developer ($99/year)
- ✓ No expiration on apps
- ✓ Unlimited apps per device
- ✓ Can use TestFlight for beta testing
- ✓ Can publish to App Store
- ✓ Advanced capabilities (push notifications, etc.)

**For testing purposes, the free Apple ID is perfectly fine!**

---

## 🚀 After Successful Launch

Once the app is running on your iPhone, you can:

- ✓ Hot reload by pressing `r` in the terminal
- ✓ Hot restart by pressing `R` in the terminal
- ✓ Toggle performance overlay by pressing `p`
- ✓ Take a screenshot by pressing `s`
- ✓ Quit by pressing `q`

---

## 📞 Need Help?

If you're stuck, check:
1. Xcode's error messages (very descriptive)
2. Flutter terminal output
3. This guide's troubleshooting section

**Most common issue**: Not selecting a Team in Xcode's Signing & Capabilities tab

---

**Last Updated**: September 30, 2025

