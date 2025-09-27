#!/bin/bash

echo "🔧 TSH Admin Dashboard - iOS Build Issues Fix"
echo "============================================="

cd "/Users/khaleelal-mulla/TSH_ERP_System_Local/mobile/flutter_apps/admin_dashboard"

echo "🧹 Step 1: Complete Clean Build"
echo "==============================="

# Clean everything thoroughly
echo "Cleaning Flutter..."
flutter clean

echo "Removing iOS build cache..."
rm -rf ios/build
rm -rf ios/.symlinks
rm -rf ios/Flutter/Generated.xcconfig
rm -rf ios/Flutter/flutter_export_environment.sh
rm -rf build/

echo "Removing Pods..."
cd ios
rm -rf Pods
rm -rf Podfile.lock
rm -rf .symlinks
cd ..

echo ""
echo "🔄 Step 2: Update Flutter and Dependencies"
echo "========================================="

# Update Flutter
flutter upgrade
flutter pub get

echo ""
echo "📦 Step 3: Fix iOS Dependencies"
echo "==============================="

cd ios

echo "Updating CocoaPods repo..."
pod repo update

echo "Installing pods with clean slate..."
pod deintegrate
pod install --repo-update

cd ..

echo ""
echo "🛠️ Step 4: Fix iOS Build Configuration"
echo "======================================"

# Create a fix for the permission handler and other iOS issues
cat > ios/fix_ios_issues.rb << 'EOF'
# Fix for iOS build issues
post_install do |installer|
  installer.pods_project.targets.each do |target|
    target.build_configurations.each do |config|
      # Fix deployment target
      config.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] = '12.0'
      
      # Fix Swift version
      config.build_settings['SWIFT_VERSION'] = '5.0'
      
      # Fix other common issues
      config.build_settings['ENABLE_BITCODE'] = 'NO'
      config.build_settings['ONLY_ACTIVE_ARCH'] = 'YES'
      
      # Fix header search paths
      config.build_settings['HEADER_SEARCH_PATHS'] = [
        '$(inherited)',
        '$(SRCROOT)/Flutter',
        '$(SRCROOT)/Runner',
        '$(PROJECT_DIR)/Flutter'
      ]
    end
    
    # Fix specific issues for permission handler
    if target.name == 'permission_handler_apple'
      target.build_configurations.each do |config|
        config.build_settings['GCC_PREPROCESSOR_DEFINITIONS'] = [
          '$(inherited)',
          'PERMISSION_CAMERA=1',
          'PERMISSION_PHOTOS=1'
        ]
      end
    end
  end
end
EOF

# Update Podfile to include the fix
if ! grep -q "load 'fix_ios_issues.rb'" ios/Podfile; then
    echo "" >> ios/Podfile
    echo "load 'fix_ios_issues.rb'" >> ios/Podfile
fi

echo ""
echo "🔧 Step 5: Reinstall Pods with Fixes"
echo "===================================="

cd ios
pod install --clean-install
cd ..

echo ""
echo "🏗️ Step 6: Rebuild Flutter Configuration"
echo "========================================"

# Regenerate Flutter configuration
flutter pub get
flutter pub deps

echo ""
echo "📱 Step 7: Test Build"
echo "===================="

echo "Building for iOS (this may take a few minutes)..."
flutter build ios --debug --no-codesign

echo ""
echo "✅ Fix Complete!"
echo "==============="
echo ""
echo "🍎 Now try opening in Xcode:"
echo "   open ios/Runner.xcworkspace"
echo ""
echo "📋 If you still get errors:"
echo "   1. In Xcode: Product → Clean Build Folder"
echo "   2. Close Xcode completely"
echo "   3. Run this script again"
echo "   4. Reopen Xcode"
echo ""
echo "🚀 Or try direct Flutter run:"
echo "   flutter run --debug"
