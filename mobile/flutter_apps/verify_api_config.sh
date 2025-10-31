#!/bin/bash

echo "=========================================="
echo "TSH ERP Flutter Apps API Configuration"
echo "Verification Script"
echo "=========================================="
echo ""
echo "Expected API URL: http://192.168.68.51:8000"
echo "Expected Database: PostgreSQL (central ERP)"
echo ""
echo "=========================================="
echo ""

CORRECT_URL="192.168.68.51:8000"
FAILED_COUNT=0
SUCCESS_COUNT=0

for app_dir in 0*_*/; do
  app="${app_dir%/}"
  echo "📱 Checking: $app"

  # Find all config and API service files
  config_files=$(find "$app_dir" -type f \( -name "app_config.dart" -o -name "api_service.dart" \) 2>/dev/null)

  if [ -z "$config_files" ]; then
    echo "  ⚠️  No configuration files found"
    FAILED_COUNT=$((FAILED_COUNT + 1))
  else
    # Check for correct API URL
    if echo "$config_files" | xargs grep -l "$CORRECT_URL" > /dev/null 2>&1; then
      echo "  ✅ Using correct API: http://$CORRECT_URL"
      SUCCESS_COUNT=$((SUCCESS_COUNT + 1))

      # Show the actual configuration
      api_line=$(echo "$config_files" | xargs grep -h "baseUrl.*$CORRECT_URL" 2>/dev/null | head -1)
      if [ -n "$api_line" ]; then
        echo "     $api_line"
      fi
    else
      echo "  ❌ NOT using correct API URL"
      FAILED_COUNT=$((FAILED_COUNT + 1))

      # Show what it's using instead
      wrong_urls=$(echo "$config_files" | xargs grep -h "baseUrl\|odooUrl\|apiUrl" 2>/dev/null | grep -v "192.168.68.51")
      if [ -n "$wrong_urls" ]; then
        echo "     Current config:"
        echo "$wrong_urls" | sed 's/^/       /'
      fi
    fi

    # Check for deprecated Odoo configuration
    if echo "$config_files" | xargs grep -l "odooUrl\|nootshitup" > /dev/null 2>&1; then
      echo "  ⚠️  Contains old Odoo configuration (should be deprecated/commented)"
    fi
  fi

  echo ""
done

echo "=========================================="
echo "Summary:"
echo "  ✅ Correct: $SUCCESS_COUNT apps"
echo "  ❌ Needs Fix: $FAILED_COUNT apps"
echo "=========================================="

if [ $FAILED_COUNT -eq 0 ]; then
  echo "✅ All apps are configured correctly!"
  exit 0
else
  echo "⚠️  Some apps need configuration updates"
  exit 1
fi
