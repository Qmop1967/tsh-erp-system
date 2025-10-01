#!/bin/bash

echo "🛠️ Quick Fix for Xcode Build Errors"
echo "=================================="

cd "/Users/khaleelal-mulla/TSH_ERP_System_Local/mobile/flutter_apps/admin_dashboard"

echo "🔧 Fixing permission_handler_apple issues..."

# Fix the permission handler framework issues
cd ios

# Create a temporary fix for the double-quoted include issues
# This is a common issue with newer Xcode versions

echo "Updating Podfile with build fixes..."

cat > pod_fixes.txt << 'EOF'

post_install do |installer|
  installer.pods_project.targets.each do |target|
    target.build_configurations.each do |config|
      config.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] = '12.0'
      config.build_settings['SWIFT_VERSION'] = '5.0'
      config.build_settings['ENABLE_BITCODE'] = 'NO'
      
      # Fix for permission handler and other framework issues
      if target.name.include?('permission_handler') || target.name.include?('sqflite') || target.name.include?('shared_preferences')
        config.build_settings['CLANG_ALLOW_NON_MODULAR_INCLUDES_IN_FRAMEWORK_MODULES'] = 'YES'
        config.build_settings['CLANG_ENABLE_MODULES'] = 'YES'
      end
    end
  end
end
EOF

# Add the post_install hook to Podfile if not present
if ! grep -q "post_install" Podfile; then
    cat pod_fixes.txt >> Podfile
    echo "✅ Added build fixes to Podfile"
else
    echo "⚠️ post_install hook already exists, please add the fixes manually"
fi

echo "🔄 Reinstalling pods with fixes..."
pod install --clean-install

cd ..

echo ""
echo "✅ Quick fixes applied!"
echo ""
echo "🍎 Now try in Xcode:"
echo "   1. Close Xcode completely if open"
echo "   2. Open: open ios/Runner.xcworkspace"
echo "   3. Clean Build Folder: Product → Clean Build Folder (Cmd+Shift+K)"
echo "   4. Try building again"
echo ""
echo "🚀 Or try Flutter command line:"
echo "   flutter run --debug"
