#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║         TSH ERP SYSTEM - APP LAUNCHER                             ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# App list
declare -a APPS=(
    "01_tsh_admin_app:TSH Admin"
    "02_tsh_hr_app:TSH HR"
    "03_tsh_inventory_app:TSH Inventory"
    "04_tsh_retail_sales_app:TSH Retail Sales"
    "05_tsh_salesperson_app:TSH Salesperson (Unified)"
    "06_tsh_partner_network_app:TSH Partner Network"
    "07_tsh_wholesale_client_app:TSH Wholesale Client"
    "08_tsh_consumer_app:TSH Consumer"
)

echo "Select app to launch:"
echo ""

for i in "${!APPS[@]}"; do
    IFS=':' read -r folder name <<< "${APPS[$i]}"
    echo "  $((i+1))) $name"
done

echo ""
read -p "Enter number (1-8): " selection

if [[ "$selection" -ge 1 && "$selection" -le 8 ]]; then
    IFS=':' read -r folder name <<< "${APPS[$((selection-1))]}"
    
    echo ""
    echo "Launching: $name"
    echo "Location: mobile/flutter_apps/$folder"
    echo ""
    
    cd "mobile/flutter_apps/$folder" || exit 1
    
    # Check for connected devices
    flutter devices
    
    echo ""
    read -p "Device ID (or press Enter for default): " device_id
    
    if [ -z "$device_id" ]; then
        flutter run
    else
        flutter run -d "$device_id"
    fi
else
    echo "Invalid selection"
    exit 1
fi
