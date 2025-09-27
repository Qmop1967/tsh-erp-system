#!/bin/bash

# iOS Build Script with Extended Attributes Fix
echo "🚀 Building iOS app with extended attributes fix..."

cd "/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"

# Build the app
echo "📱 Building iOS app..."
flutter build ios --device-id 00008130-0004310C1ABA001C --no-codesign

# Find and fix Flutter.framework extended attributes
FLUTTER_FRAMEWORK=$(find build -name "Flutter.framework" -type d 2>/dev/null | head -1)

if [ -n "$FLUTTER_FRAMEWORK" ]; then
    echo "🔧 Fixing extended attributes on $FLUTTER_FRAMEWORK"
    
    # Remove extended attributes recursively
    find "$FLUTTER_FRAMEWORK" -exec xattr -c {} \; 2>/dev/null || true
    
    # Manually codesign the Flutter.framework
    echo "✍️ Manually codesigning Flutter.framework..."
    codesign --force --sign "325FE347A0CCEF503AD8C6A774D674292305CC7C" "$FLUTTER_FRAMEWORK"
    
    # Now try to build and sign the complete app
    echo "🔨 Final build and sign..."
    flutter build ios --device-id 00008130-0004310C1ABA001C
else
    echo "❌ Flutter.framework not found"
    exit 1
fi
