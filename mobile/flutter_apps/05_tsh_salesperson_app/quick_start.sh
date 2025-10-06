#!/bin/bash

# TSH Salesperson App - Quick Start Script
# This script helps you quickly run the app

echo "🚀 TSH Salesperson App - Quick Start"
echo "===================================="
echo ""

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter is not installed. Please install Flutter first."
    echo "Visit: https://flutter.dev/docs/get-started/install"
    exit 1
fi

echo "✅ Flutter found: $(flutter --version | head -1)"
echo ""

# Navigate to project directory
cd "$(dirname "$0")"

echo "📦 Installing dependencies..."
flutter pub get

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"
echo ""

# Check for connected devices
echo "📱 Checking for connected devices..."
flutter devices

echo ""
echo "🎯 Select how you want to run the app:"
echo "1. iOS Simulator"
echo "2. Android Emulator"
echo "3. Connected Device"
echo "4. Chrome (Web)"
echo "5. Exit"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo "🍎 Launching on iOS Simulator..."
        flutter run -d iphone
        ;;
    2)
        echo "🤖 Launching on Android Emulator..."
        flutter run -d emulator
        ;;
    3)
        echo "📱 Launching on Connected Device..."
        flutter run
        ;;
    4)
        echo "🌐 Launching on Chrome..."
        flutter run -d chrome
        ;;
    5)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Running on default device..."
        flutter run
        ;;
esac
