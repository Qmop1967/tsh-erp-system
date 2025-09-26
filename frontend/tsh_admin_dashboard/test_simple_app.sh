#!/bin/bash

echo "Testing iOS app with simple Flutter test..."

cd "/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"

echo "Running simple test app on iPhone..."
flutter run -d 00008130-0004310C1ABA001C lib/main_simple.dart --debug

echo "Test completed!"
