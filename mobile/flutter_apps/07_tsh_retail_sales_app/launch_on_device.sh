#!/bin/bash

echo "📱 Launching TSH Retail Sales"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check devices
flutter devices

echo ""
echo "Select mode:"
echo "  1) Debug (hot reload enabled)"
echo "  2) Release (optimized)"
echo "  3) Profile (performance testing)"
echo ""
read -p "Enter choice [1-3] (default: 1): " mode

mode=${mode:-1}

case $mode in
    2)
        echo "Building in RELEASE mode..."
        flutter run --release
        ;;
    3)
        echo "Building in PROFILE mode..."
        flutter run --profile
        ;;
    *)
        echo "Building in DEBUG mode..."
        flutter run
        ;;
esac
