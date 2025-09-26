#!/bin/bash

# Enhanced iOS Plugin Fix Script
# Fixes Swift version conflicts and connectivity_plus module issues

set -e

APP_DIR="/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"
CORE_DIR="/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_core_package"

echo "🔧 Starting Enhanced iOS Plugin Fix..."

cd "$APP_DIR"

# Step 1: Clean everything
echo "🧹 Deep cleaning all artifacts..."
flutter clean
rm -rf .dart_tool/
rm -rf build/

# Clean iOS
cd ios
rm -rf Podfile.lock
rm -rf Pods/
rm -rf .symlinks/
rm -rf Flutter/App.framework
rm -rf Flutter/Flutter.framework
rm -rf Runner.xcworkspace
cd ..

# Clean core package
cd "$CORE_DIR"
flutter clean
rm -rf .dart_tool/
cd "$APP_DIR"

# Step 2: Fix Swift version in Podfile
echo "🔧 Fixing Swift version in Podfile..."
cd ios

# Create a new Podfile with explicit Swift version
cat > Podfile << 'EOF'
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

  flutter_install_all_ios_pods File.dirname(File.realpath(__FILE__))
  target 'RunnerTests' do
    inherit! :search_paths
  end
end

post_install do |installer|
  installer.pods_project.targets.each do |target|
    flutter_additional_ios_build_settings(target)
    # Force Swift 5.0 for all targets
    target.build_configurations.each do |config|
      config.build_settings['SWIFT_VERSION'] = '5.0'
    end
  end
end
EOF

cd ..

# Step 3: Get dependencies
echo "📥 Getting core package dependencies..."
cd "$CORE_DIR"
flutter pub get
cd "$APP_DIR"

echo "📥 Getting main app dependencies..."
flutter pub get

# Step 4: Manually add connectivity_plus to main app if needed
echo "🔧 Ensuring connectivity_plus is available..."
if ! grep -q "connectivity_plus:" pubspec.yaml; then
    echo "📦 Adding connectivity_plus directly to main app..."
    # Add connectivity_plus after tsh_core_package
    sed -i '' '/tsh_core_package:/a\
  \
  # Network connectivity\
  connectivity_plus: ^5.0.1' pubspec.yaml
    
    echo "📥 Re-getting dependencies after adding connectivity_plus..."
    flutter pub get
fi

# Step 5: Install pods with force
echo "🍎 Installing CocoaPods with forced settings..."
cd ios

# Force pod install to ignore Swift version warnings
export COCOAPODS_DISABLE_STATS=true
pod install --allow-warnings --verbose

cd ..

# Step 6: Verify the setup
echo "🔍 Verifying setup..."
echo "Checking if connectivity_plus pod was installed..."
if [ -d "ios/Pods/connectivity_plus" ]; then
    echo "✅ connectivity_plus pod found"
else
    echo "❌ connectivity_plus pod NOT found"
fi

echo "Checking GeneratedPluginRegistrant.m..."
if [ -f "ios/Runner/GeneratedPluginRegistrant.m" ]; then
    echo "✅ GeneratedPluginRegistrant.m exists"
    if grep -q "ConnectivityPlusPlugin" ios/Runner/GeneratedPluginRegistrant.m; then
        echo "✅ ConnectivityPlusPlugin found in GeneratedPluginRegistrant.m"
    else
        echo "❌ ConnectivityPlusPlugin NOT found in GeneratedPluginRegistrant.m"
    fi
else
    echo "❌ GeneratedPluginRegistrant.m NOT found"
fi

# Step 7: Try to build for iOS
echo "🔨 Building for iOS (debug, no codesign)..."
flutter build ios --no-codesign --debug

echo ""
echo "✅ Enhanced iOS Plugin Fix Complete!"
echo ""
echo "📋 What was fixed:"
echo "- All build artifacts cleaned"
echo "- Swift version forced to 5.0 in Podfile"
echo "- CocoaPods installed with --allow-warnings"
echo "- connectivity_plus added directly if needed"
echo "- iOS debug build completed"
echo ""
echo "🚀 Next steps:"
echo "1. Open the project: open ios/Runner.xcworkspace"
echo "2. Select your development team in Xcode"
echo "3. Build and run on your device"
echo ""
echo "🎯 The connectivity_plus module should now be available!"
