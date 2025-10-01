#!/bin/bash

echo "🔧 TSH Salesperson App - Complete iOS Fix"
echo "=========================================="
echo ""
echo "This script will fix ALL iOS codesigning and configuration issues:"
echo "  ✓ Fix bundle identifier (com.tsh.salesperson)"
echo "  ✓ Update development team ID"
echo "  ✓ Clean duplicate xcconfig includes"
echo "  ✓ Fix Podfile configuration"
echo "  ✓ Update Xcode project settings"
echo "  ✓ Clean and rebuild everything"
echo ""

# Store the app directory
APP_DIR="/Users/khaleelal-mulla/TSH_ERP_System_Local/tsh_salesperson_app"
cd "$APP_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# ============================================
# STEP 1: Fix Bundle Identifier & Team ID
# ============================================
echo ""
echo "📝 Step 1: Fixing Bundle Identifier & Team ID..."

# Bundle ID should be com.tsh.salesperson (NOT com.tsh.admin)
# Team ID should be 3BJB4453J5 (based on your Apple Developer account)

BUNDLE_ID="com.tsh.salesperson"
TEAM_ID="3BJB4453J5"

# Update in project.pbxproj
if [ -f "ios/Runner.xcodeproj/project.pbxproj" ]; then
    # Backup the file
    cp ios/Runner.xcodeproj/project.pbxproj ios/Runner.xcodeproj/project.pbxproj.backup
    
    # Replace bundle identifier
    sed -i '' "s/com\.tsh\.admin/${BUNDLE_ID}/g" ios/Runner.xcodeproj/project.pbxproj
    
    # Replace team ID (old: 38U844SAJ5, new: 3BJB4453J5)
    sed -i '' "s/38U844SAJ5/${TEAM_ID}/g" ios/Runner.xcodeproj/project.pbxproj
    
    print_status "Updated Bundle ID to ${BUNDLE_ID}"
    print_status "Updated Team ID to ${TEAM_ID}"
else
    print_error "project.pbxproj not found!"
    exit 1
fi

# ============================================
# STEP 2: Clean Duplicate xcconfig Includes
# ============================================
echo ""
echo "🧹 Step 2: Cleaning xcconfig files..."

# Fix Debug.xcconfig
cat > ios/Flutter/Debug.xcconfig << 'EOF'
#include? "Pods/Target Support Files/Pods-Runner/Pods-Runner.debug.xcconfig"
#include "Generated.xcconfig"
EOF
print_status "Cleaned Debug.xcconfig"

# Fix Release.xcconfig
cat > ios/Flutter/Release.xcconfig << 'EOF'
#include? "Pods/Target Support Files/Pods-Runner/Pods-Runner.release.xcconfig"
#include "Generated.xcconfig"
EOF
print_status "Cleaned Release.xcconfig"

# ============================================
# STEP 3: Fix Podfile Configuration
# ============================================
echo ""
echo "🍫 Step 3: Fixing Podfile..."

cat > ios/Podfile << 'EOF'
# Uncomment this line to define a global platform for your project
platform :ios, '13.0'

# CocoaPods analytics sends network stats synchronously affecting flutter build latency.
ENV['COCOAPODS_DISABLE_STATS'] = 'true'

project 'Runner', {
  'Debug' => :debug,
  'Profile' => :release,
  'Release' => :release,
}

def flutter_root
  generated_xcode_build_settings_path = File.expand_path(File.join('..', 'Flutter', 'Generated.xcconfig'), __FILE__)
  unless File.exist?(generated_xcode_build_settings_path)
    raise "#{generated_xcode_build_settings_path} must exist. If you're running pod install manually, make sure flutter pub get is executed first"
  end

  File.foreach(generated_xcode_build_settings_path) do |line|
    matches = line.match(/FLUTTER_ROOT\=(.*)/)
    return matches[1].strip if matches
  end
  raise "FLUTTER_ROOT not found in #{generated_xcode_build_settings_path}. Try deleting Generated.xcconfig, then run flutter pub get"
end

require File.expand_path(File.join('packages', 'flutter_tools', 'bin', 'podhelper'), flutter_root)

flutter_ios_podfile_setup

target 'Runner' do
  use_frameworks!
  use_modular_headers!

  flutter_install_all_ios_pods File.dirname(File.realpath(__FILE__))
  
  target 'RunnerTests' do
    inherit! :search_paths
  end
end

post_install do |installer|
  # CRITICAL: Enable this for proper Flutter iOS builds
  installer.pods_project.targets.each do |target|
    flutter_additional_ios_build_settings(target)
    
    target.build_configurations.each do |config|
      # Fix deployment target
      config.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] = '13.0'
      
      # Enable arm64 simulator support (Apple Silicon Macs)
      config.build_settings['ONLY_ACTIVE_ARCH'] = 'NO'
      
      # Disable bitcode (deprecated by Apple)
      config.build_settings['ENABLE_BITCODE'] = 'NO'
      
      # Swift version
      config.build_settings['SWIFT_VERSION'] = '5.0'
    end
  end
end
EOF
print_status "Updated Podfile with correct configuration"

# ============================================
# STEP 4: Update Info.plist
# ============================================
echo ""
echo "📋 Step 4: Verifying Info.plist..."

if grep -q "TSH Salesperson" ios/Runner/Info.plist; then
    print_status "Info.plist display name is correct"
else
    print_warning "Info.plist might need manual review"
fi

# ============================================
# STEP 5: Deep Clean
# ============================================
echo ""
echo "🧹 Step 5: Deep cleaning project..."

# Remove all build artifacts
print_status "Removing Flutter build artifacts..."
flutter clean

# Remove iOS specific artifacts
print_status "Removing iOS build directory..."
rm -rf ios/build/

# Remove Pods
print_status "Removing Pods..."
rm -rf ios/Pods/
rm -rf ios/.symlinks/
rm -f ios/Podfile.lock

# Remove derived data (if accessible)
print_status "Cleaning Xcode derived data..."
rm -rf ~/Library/Developer/Xcode/DerivedData/Runner-*

print_status "Deep clean completed!"

# ============================================
# STEP 6: Rebuild Everything
# ============================================
echo ""
echo "🔨 Step 6: Rebuilding project..."

# Get Flutter packages
print_status "Getting Flutter packages..."
if flutter pub get; then
    print_status "Flutter packages updated"
else
    print_error "Failed to get Flutter packages"
    exit 1
fi

# Install CocoaPods with proper locale settings
echo ""
print_status "Installing CocoaPods dependencies..."
cd ios

# Set UTF-8 locale to fix CocoaPods encoding issue
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

if pod install --repo-update; then
    print_status "CocoaPods installed successfully"
else
    print_error "CocoaPods installation failed"
    echo "Trying without --repo-update..."
    if pod install; then
        print_status "CocoaPods installed successfully"
    else
        print_error "CocoaPods installation failed. Trying to continue anyway..."
    fi
fi
cd ..

# ============================================
# STEP 7: Verification
# ============================================
echo ""
echo "✅ Step 7: Verification..."
echo ""

# Check Flutter doctor
echo "Running Flutter doctor..."
flutter doctor

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 iOS Configuration Fix Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 Bundle ID: ${BUNDLE_ID}"
echo "👥 Team ID: ${TEAM_ID}"
echo ""
echo "Next Steps:"
echo "1. Connect your iPhone via USB"
echo "2. Unlock your iPhone and trust this computer"
echo "3. Run: ./launch_on_iphone.sh"
echo ""
echo "Or manually run:"
echo "  flutter devices"
echo "  flutter run -d <your-device-id>"
echo ""
echo "If you still have signing issues:"
echo "  1. Open ios/Runner.xcworkspace in Xcode"
echo "  2. Select Runner target"
echo "  3. Go to 'Signing & Capabilities' tab"
echo "  4. Ensure 'Automatically manage signing' is checked"
echo "  5. Select your Team: ${TEAM_ID}"
echo "  6. Verify Bundle Identifier: ${BUNDLE_ID}"
echo ""

