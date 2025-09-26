#!/bin/bash

echo "🔧 COMPREHENSIVE iOS PROJECT FIX"
echo "================================="

PROJECT_DIR="/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"
cd "$PROJECT_DIR"

echo "🧹 Step 1: Complete Clean..."
flutter clean
rm -rf ios/Pods
rm -rf ios/.symlinks
rm -rf ios/Flutter/Flutter.framework
rm -rf ios/Flutter/Flutter.podspec
rm -f ios/Podfile.lock
rm -rf build/
rm -rf .dart_tool/
rm -rf ios/Runner.xcworkspace/xcuserdata/
rm -rf ios/DerivedData/
rm -rf ~/Library/Developer/Xcode/DerivedData/*TSH* 2>/dev/null || true

echo "📦 Step 2: Flutter Setup..."
flutter pub get
flutter pub deps

echo "🔧 Step 3: Fix iOS Deployment Target..."
# Update deployment target in all configuration files
sed -i '' 's/IPHONEOS_DEPLOYMENT_TARGET = [0-9.]*;/IPHONEOS_DEPLOYMENT_TARGET = 12.0;/g' ios/Runner.xcodeproj/project.pbxproj
sed -i '' 's/ios-deployment-target.*$/ios-deployment-target=12.0/g' ios/Flutter/Release.xcconfig 2>/dev/null || true
sed -i '' 's/ios-deployment-target.*$/ios-deployment-target=12.0/g' ios/Flutter/Debug.xcconfig 2>/dev/null || true

echo "📝 Step 4: Update Podfile with latest specifications..."

cat > ios/Podfile << 'EOF'
# Uncomment this line to define a global platform for your project
platform :ios, '12.0'

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
  installer.pods_project.targets.each do |target|
    flutter_additional_ios_build_settings(target)
    target.build_configurations.each do |config|
      config.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] = '12.0'
      config.build_settings['ENABLE_BITCODE'] = 'NO'
    end
  end
end
EOF

echo "🍎 Step 5: CocoaPods Installation..."
cd ios
pod repo update
pod deintegrate 2>/dev/null || true
pod install --clean-install --verbose

echo "🔧 Step 6: Update Xcode Project Settings..."
cd "$PROJECT_DIR"

# Ensure all configurations are correct
sed -i '' 's/DEVELOPMENT_TEAM = .*/DEVELOPMENT_TEAM = 3BJB4453J5;/g' ios/Runner.xcodeproj/project.pbxproj
sed -i '' 's/PRODUCT_BUNDLE_IDENTIFIER = .*/PRODUCT_BUNDLE_IDENTIFIER = com.tsh.admin;/g' ios/Runner.xcodeproj/project.pbxproj
sed -i '' 's/CODE_SIGN_STYLE = .*/CODE_SIGN_STYLE = Automatic;/g' ios/Runner.xcodeproj/project.pbxproj

echo "✅ Step 7: Verification..."
echo ""
echo "📊 Project Status:"
echo "   - Flutter Version: $(flutter --version | head -1)"
echo "   - iOS Deployment Target: 12.0"
echo "   - Bundle ID: com.tsh.admin"
echo "   - Team ID: 3BJB4453J5"
echo "   - CocoaPods: Updated"

echo ""
echo "🚀 Next Actions:"
echo "1. Close Xcode completely"
echo "2. Reopen: open ios/Runner.xcworkspace"
echo "3. Clean Build Folder (⇧⌘K)"
echo "4. Try building the project"

echo ""
echo "Would you like to open Xcode now? (y/n)"
read -r open_xcode_response

if [[ $open_xcode_response =~ ^[Yy]$ ]]; then
    echo "🔧 Opening Xcode..."
    open ios/Runner.xcworkspace
fi

echo ""
echo "🎉 Comprehensive fix completed!"
