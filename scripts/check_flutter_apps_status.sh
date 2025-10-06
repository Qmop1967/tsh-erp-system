#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║         TSH ERP SYSTEM - FLUTTER APPS STATUS CHECK                ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Base directory
BASE_DIR="/Users/khaleelal-mulla/TSH_ERP_System_Local"

# Array to store app information
declare -a APP_NAMES=()
declare -a APP_PATHS=()
declare -a APP_VERSIONS=()
declare -a APP_STATUSES=()

# Function to check if an app has pubspec.yaml
check_app_status() {
    local app_path=$1
    local app_name=$(basename "$app_path")
    
    if [ ! -f "$app_path/pubspec.yaml" ]; then
        return 1
    fi
    
    # Read app name and version from pubspec.yaml
    local yaml_name=$(grep "^name:" "$app_path/pubspec.yaml" | head -1 | awk '{print $2}' | tr -d '"' | tr -d "'")
    local yaml_version=$(grep "^version:" "$app_path/pubspec.yaml" | head -1 | awk '{print $2}')
    
    # Check if it has lib/main.dart
    local has_main=""
    if [ -f "$app_path/lib/main.dart" ]; then
        has_main="✓"
    else
        has_main="✗"
    fi
    
    # Check if it has ios folder
    local has_ios=""
    if [ -d "$app_path/ios" ]; then
        has_ios="✓"
    else
        has_ios="✗"
    fi
    
    # Check if it has android folder
    local has_android=""
    if [ -d "$app_path/android" ]; then
        has_android="✓"
    else
        has_android="✗"
    fi
    
    # Check if dependencies are installed
    local has_deps=""
    if [ -d "$app_path/.dart_tool" ] || [ -f "$app_path/pubspec.lock" ]; then
        has_deps="✓"
    else
        has_deps="✗"
    fi
    
    # Determine overall status
    local status="INCOMPLETE"
    if [[ "$has_main" == "✓" && "$has_ios" == "✓" && "$has_android" == "✓" ]]; then
        status="COMPLETE"
    fi
    
    # Store information
    APP_NAMES+=("$yaml_name")
    APP_PATHS+=("$app_path")
    APP_VERSIONS+=("${yaml_version:-N/A}")
    APP_STATUSES+=("$status|$has_main|$has_ios|$has_android|$has_deps")
}

echo -e "${BLUE}Scanning for Flutter apps...${NC}"
echo ""

# Check root level apps
for dir in "$BASE_DIR"/tsh_*_app "$BASE_DIR"/tsh_*_sales; do
    if [ -d "$dir" ]; then
        check_app_status "$dir"
    fi
done

# Check mobile/flutter_apps
if [ -d "$BASE_DIR/mobile/flutter_apps" ]; then
    for dir in "$BASE_DIR/mobile/flutter_apps"/*; do
        if [ -d "$dir" ]; then
            check_app_status "$dir"
        fi
    done
fi

# Print results
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                    FLUTTER APPS INVENTORY                          ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

total_apps=${#APP_NAMES[@]}
complete_apps=0
incomplete_apps=0

for i in "${!APP_NAMES[@]}"; do
    name="${APP_NAMES[$i]}"
    path="${APP_PATHS[$i]}"
    version="${APP_VERSIONS[$i]}"
    status_info="${APP_STATUSES[$i]}"
    
    # Parse status
    IFS='|' read -r status has_main has_ios has_android has_deps <<< "$status_info"
    
    # Count complete/incomplete
    if [[ "$status" == "COMPLETE" ]]; then
        ((complete_apps++))
        status_color="${GREEN}"
    else
        ((incomplete_apps++))
        status_color="${YELLOW}"
    fi
    
    # Make path relative for display
    rel_path="${path#$BASE_DIR/}"
    
    echo -e "${CYAN}[$((i+1))/$total_apps]${NC} ${status_color}$status${NC} - $name"
    echo "     📁 Location: $rel_path"
    echo "     📦 Version: $version"
    echo -e "     ✓/✗ Status: Main:$has_main iOS:$has_ios Android:$has_android Deps:$has_deps"
    echo ""
done

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                         SUMMARY                                    ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "Total Apps Found:       ${CYAN}$total_apps${NC}"
echo -e "Complete Apps:          ${GREEN}$complete_apps${NC}"
echo -e "Incomplete/Legacy Apps: ${YELLOW}$incomplete_apps${NC}"
echo ""

# Detect duplicates
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                    DUPLICATE DETECTION                             ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

declare -A name_counts
for name in "${APP_NAMES[@]}"; do
    ((name_counts[$name]++))
done

duplicates_found=0
for name in "${!name_counts[@]}"; do
    if [ "${name_counts[$name]}" -gt 1 ]; then
        echo -e "${YELLOW}⚠ DUPLICATE FOUND:${NC} '$name' appears ${name_counts[$name]} times"
        duplicates_found=1
        
        # Show locations
        for i in "${!APP_NAMES[@]}"; do
            if [[ "${APP_NAMES[$i]}" == "$name" ]]; then
                rel_path="${APP_PATHS[$i]#$BASE_DIR/}"
                echo "   → $rel_path"
            fi
        done
        echo ""
    fi
done

if [ $duplicates_found -eq 0 ]; then
    echo -e "${GREEN}✓ No duplicates found${NC}"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                    RECOMMENDED STRUCTURE                           ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""
echo "Based on your business requirements (8 mobile apps):"
echo ""
echo "mobile/"
echo "├── flutter_apps/"
echo "│   ├── 01_tsh_admin_app/              # Owner - Complete project control"
echo "│   ├── 02_tsh_hr_app/                 # HR Director - HR management"
echo "│   ├── 03_tsh_inventory_app/          # Multi-location inventory"
echo "│   ├── 04_tsh_retailer_shop_app/      # Retailer shop operations"
echo "│   ├── 05_tsh_travel_salesperson_app/ # Travel sales - GPS & fraud prevention"
echo "│   ├── 06_tsh_partner_salesman_app/   # Partner salesmen (100+ across Iraq)"
echo "│   ├── 07_tsh_wholesale_client_app/   # B2B wholesale clients (500+ clients)"
echo "│   ├── 08_tsh_consumer_app/           # Direct consumers (B2C)"
echo "│   └── shared/                        # Shared packages, utilities"
echo "│       └── tsh_core_package/          # Core shared code"
echo ""

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                    NEXT STEPS                                      ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""
echo "1. Review this status report"
echo "2. Decide which apps to keep vs archive"
echo "3. Run reorganization script to restructure"
echo "4. Update all bundle identifiers and configurations"
echo ""
echo "Would you like me to generate a reorganization script? (manual execution)"
echo ""

