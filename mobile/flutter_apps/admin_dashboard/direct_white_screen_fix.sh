#!/bin/bash

# Direct White Screen Fix - Focus on Framework Generation
echo "🚀 DIRECT WHITE SCREEN FIX"
echo ""

APP_DIR="/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"
cd "$APP_DIR"

echo "🎯 The issue: Flutter.framework and App.framework are missing"
echo "   This causes the white screen because Flutter engine can't initialize"
echo ""

echo "📱 Creating minimal test to verify the fix works..."

# Create a minimal main.dart to test
cat > lib/main_test.dart << 'EOF'
import 'package:flutter/material.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TSH Admin Test',
      home: Scaffold(
        appBar: AppBar(
          title: Text('TSH Admin Dashboard'),
          backgroundColor: Colors.blue,
        ),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.admin_panel_settings,
                size: 100,
                color: Colors.blue,
              ),
              SizedBox(height: 20),
              Text(
                'TSH Admin Dashboard',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 10),
              Text(
                'Loading successful!',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.green,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
EOF

echo "✅ Created minimal test app"

echo ""
echo "🔧 Method 1: Force framework generation with clean slate..."

# Remove problematic files
rm -rf ios/Flutter/ephemeral
rm -rf ios/.symlinks
rm -rf build/

# Force regenerate Flutter configuration
flutter create --org com.tsh --project-name tsh_admin_dashboard --ios-language swift --android-language kotlin .

echo "✅ Regenerated Flutter project structure"

echo ""
echo "🔨 Method 2: Build with explicit target..."

# Build with explicit simulator target first
flutter build ios --simulator --debug --target lib/main_test.dart --no-codesign

if [ -d "ios/Flutter/App.framework" ]; then
    echo "✅ SUCCESS! App.framework generated"
else
    echo "❌ Still no App.framework - trying alternative method..."
    
    # Alternative: Use flutter run to generate frameworks
    echo "🔄 Using flutter run method..."
    timeout 30s flutter run --debug --target lib/main_test.dart || true
fi

echo ""
echo "🔍 Checking frameworks after fix..."
if [ -d "ios/Flutter/Flutter.framework" ]; then
    echo "✅ Flutter.framework: FOUND"
else
    echo "❌ Flutter.framework: MISSING"
fi

if [ -d "ios/Flutter/App.framework" ]; then
    echo "✅ App.framework: FOUND"
else
    echo "❌ App.framework: MISSING"
fi

echo ""
echo "📱 DEPLOYMENT INSTRUCTIONS:"
echo ""
echo "1. Open Xcode: open ios/Runner.xcworkspace"
echo "2. Select 'Any iOS Device (arm64)' or your iPhone"
echo "3. Product → Clean Build Folder (⌘⇧K)"
echo "4. Change target from lib/main_test.dart back to lib/main.dart in:"
echo "   - Build Settings → Flutter Target"
echo "   - Or just build normally - Xcode will use main.dart"
echo "5. Build and Run (⌘R)"
echo ""
echo "💡 IF STILL WHITE SCREEN:"
echo "   - Check Xcode Console for errors"
echo "   - Look for Flutter engine messages"
echo "   - Try running on iOS Simulator first"
echo ""
echo "🎯 The frameworks should now be generated and white screen resolved!"
