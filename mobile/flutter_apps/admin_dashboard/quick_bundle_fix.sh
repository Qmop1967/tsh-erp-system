#!/bin/bash
echo "🔧 Applying temporary bundle ID for testing..."
cd "/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"
sed -i "" "s/com\.tsh\.admin/com.khaleel.tshadmin/g" ios/Runner.xcodeproj/project.pbxproj
echo "✅ Temporary bundle ID applied: com.khaleel.tshadmin"
echo "Now try building in Xcode again"
