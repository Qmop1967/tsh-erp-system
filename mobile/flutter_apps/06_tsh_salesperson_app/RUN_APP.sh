#!/bin/bash

# TSH Salesperson App - Quick Run Script
# Purpose: Build and run the app on connected device

echo "🚀 TSH Salesperson App - Quick Run"
echo "=================================="
echo ""

# Check Flutter installation
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter not found. Please install Flutter first."
    exit 1
fi

echo "✅ Flutter found"
echo ""

# Navigate to app directory
cd "$(dirname "$0")" || exit

# Flutter doctor
echo "📋 Checking Flutter setup..."
flutter doctor
echo ""

# Get dependencies
echo "📦 Getting dependencies..."
flutter pub get
echo ""

# Generate code
echo "🔨 Generating JSON serialization code..."
flutter pub run build_runner build --delete-conflicting-outputs
echo ""

# List devices
echo "📱 Available devices:"
flutter devices
echo ""

# Ask user to select device
echo "Please connect your device and press Enter to continue..."
read -r

# Run app
echo "🎯 Running app..."
flutter run

echo ""
echo "✅ Done!"
