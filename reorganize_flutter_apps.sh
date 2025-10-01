#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║     TSH ERP SYSTEM - FLUTTER APPS REORGANIZATION SCRIPT           ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""
echo "⚠️  WARNING: This script will reorganize your Flutter apps structure"
echo ""
echo "What this script does:"
echo "  1. Creates a complete backup of mobile/ directory"
echo "  2. Creates mobile/legacy/ for archived apps"
echo "  3. Renames apps with numbered prefixes"
echo "  4. Moves legacy apps to archive"
echo "  5. Creates shared/ folder for core package"
echo "  6. Generates a reorganization report"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Do you want to proceed? (yes/no): " confirm

if [[ ! $confirm =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Reorganization cancelled."
    exit 0
fi

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BASE_DIR="/Users/khaleelal-mulla/TSH_ERP_System_Local"
cd "$BASE_DIR"

# Log file
LOG_FILE="$BASE_DIR/reorganization_log_$(date +%Y%m%d_%H%M%S).txt"

log() {
    echo "$1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}✗${NC} $1" | tee -a "$LOG_FILE"
}

log ""
log "╔═══════════════════════════════════════════════════════════════════╗"
log "║                    PHASE 1: BACKUP                                 ║"
log "╚═══════════════════════════════════════════════════════════════════╝"
log ""

# Create backup
BACKUP_DIR="mobile_backup_$(date +%Y%m%d_%H%M%S)"
log "Creating backup: $BACKUP_DIR"

if cp -R mobile "$BACKUP_DIR"; then
    log_success "Backup created successfully"
    log "Backup location: $BASE_DIR/$BACKUP_DIR"
else
    log_error "Backup failed! Aborting reorganization."
    exit 1
fi

# Also backup root-level Flutter apps
log "Backing up root-level Flutter apps..."
if [ -d "tsh_salesperson_app" ]; then
    cp -R tsh_salesperson_app "$BACKUP_DIR/tsh_salesperson_app_root"
    log_success "Backed up tsh_salesperson_app"
fi
if [ -d "tsh_travel_app" ]; then
    cp -R tsh_travel_app "$BACKUP_DIR/tsh_travel_app_root"
    log_success "Backed up tsh_travel_app"
fi

log ""
log "╔═══════════════════════════════════════════════════════════════════╗"
log "║                    PHASE 2: CREATE STRUCTURE                       ║"
log "╚═══════════════════════════════════════════════════════════════════╝"
log ""

# Create legacy folder
mkdir -p mobile/legacy
log_success "Created mobile/legacy/ directory"

# Create shared folder
mkdir -p mobile/flutter_apps/shared
log_success "Created mobile/flutter_apps/shared/ directory"

log ""
log "╔═══════════════════════════════════════════════════════════════════╗"
log "║                    PHASE 3: MOVE LEGACY APPS                       ║"
log "╚═══════════════════════════════════════════════════════════════════╝"
log ""

# Move legacy apps
if [ -d "mobile/flutter_apps/inventory_app_legacy" ]; then
    mv mobile/flutter_apps/inventory_app_legacy mobile/legacy/
    log_success "Moved inventory_app_legacy to archive"
fi

if [ -d "mobile/flutter_apps/hr_app_legacy" ]; then
    mv mobile/flutter_apps/hr_app_legacy mobile/legacy/
    log_success "Moved hr_app_legacy to archive"
fi

# Archive duplicate salesperson app
if [ -d "mobile/flutter_apps/salesperson" ]; then
    mv mobile/flutter_apps/salesperson mobile/legacy/salesperson_old
    log_success "Archived duplicate salesperson app"
fi

log ""
log "╔═══════════════════════════════════════════════════════════════════╗"
log "║                    PHASE 4: RENAME APPS                            ║"
log "╚═══════════════════════════════════════════════════════════════════╝"
log ""

cd mobile/flutter_apps

# Rename apps with numbered prefixes (only if not already renamed)
rename_app() {
    local old_name=$1
    local new_name=$2
    
    if [ -d "$old_name" ] && [ ! -d "$new_name" ]; then
        mv "$old_name" "$new_name"
        log_success "Renamed: $old_name → $new_name"
        return 0
    elif [ -d "$new_name" ]; then
        log_warning "Target already exists: $new_name (skipping)"
        return 1
    else
        log_warning "Source not found: $old_name (skipping)"
        return 1
    fi
}

# Rename each app
rename_app "admin_dashboard" "01_tsh_admin_app"
rename_app "hr_app" "02_tsh_hr_app"
rename_app "inventory_app" "03_tsh_inventory_app"
rename_app "retail_sales" "04_tsh_retail_sales_app"
rename_app "partners_app" "06_tsh_partner_salesman_app"
rename_app "client_app" "07_tsh_wholesale_client_app"
rename_app "consumer_app" "08_tsh_consumer_app"

# Move core package to shared
if [ -d "core_package" ]; then
    mv core_package shared/tsh_core_package
    log_success "Moved core_package to shared/tsh_core_package"
fi

cd "$BASE_DIR"

log ""
log "╔═══════════════════════════════════════════════════════════════════╗"
log "║                    PHASE 5: HANDLE ROOT APPS                       ║"
log "╚═══════════════════════════════════════════════════════════════════╝"
log ""

# Handle tsh_travel_app (move to mobile/flutter_apps)
if [ -d "tsh_travel_app" ] && [ ! -d "mobile/flutter_apps/05_tsh_travel_salesperson_app" ]; then
    mv tsh_travel_app mobile/flutter_apps/05_tsh_travel_salesperson_app
    log_success "Moved tsh_travel_app → mobile/flutter_apps/05_tsh_travel_salesperson_app"
elif [ -d "mobile/flutter_apps/05_tsh_travel_salesperson_app" ]; then
    log_warning "Travel app already in target location"
fi

# Handle tsh_salesperson_app (keep in root for now - iOS configured)
if [ -d "tsh_salesperson_app" ]; then
    log_warning "tsh_salesperson_app kept in root (iOS configured - production ready)"
    log "         Consider using as: 04_tsh_retailer_shop_app OR salesperson app"
fi

# Check for any temp files
if [ -e "tsh_travel_sales_temp" ]; then
    rm -rf tsh_travel_sales_temp
    log_success "Removed temp directory: tsh_travel_sales_temp"
fi

log ""
log "╔═══════════════════════════════════════════════════════════════════╗"
log "║                    PHASE 6: CREATE DOCUMENTATION                   ║"
log "╚═══════════════════════════════════════════════════════════════════╝"
log ""

# Create README for mobile directory
cat > mobile/README.md << 'EOF'
# 📱 TSH ERP System - Mobile Applications

## Directory Structure

```
mobile/
├── flutter_apps/          # All production Flutter applications
│   ├── 01_tsh_admin_app/
│   ├── 02_tsh_hr_app/
│   ├── 03_tsh_inventory_app/
│   ├── 04_tsh_retail_sales_app/
│   ├── 05_tsh_travel_salesperson_app/
│   ├── 06_tsh_partner_salesman_app/
│   ├── 07_tsh_wholesale_client_app/
│   ├── 08_tsh_consumer_app/
│   └── shared/
│       └── tsh_core_package/
│
├── legacy/                # Archived/deprecated apps
│   └── ...
│
├── ios/                   # Shared iOS configurations
└── android/               # Shared Android configurations
```

## App Descriptions

### 01 - TSH Admin App
**Purpose:** Owner/admin dashboard with complete project control  
**Users:** Business owner, system administrators  
**Bundle ID:** `com.tsh.admin`

### 02 - TSH HR App
**Purpose:** HR management system for payroll, attendance, performance  
**Users:** HR Director, HR team  
**Bundle ID:** `com.tsh.hr`

### 03 - TSH Inventory App
**Purpose:** Multi-location inventory tracking and management  
**Users:** Inventory managers, warehouse staff  
**Bundle ID:** `com.tsh.inventory`

### 04 - TSH Retail Sales App
**Purpose:** Retail shop operations and customer management  
**Users:** Retail shop staff  
**Bundle ID:** `com.tsh.retailsales`

### 05 - TSH Travel Salesperson App
**Purpose:** Travel salesperson app with GPS tracking and fraud prevention  
**Users:** 12 travel salespersons  
**Bundle ID:** `com.tsh.travelsales`

### 06 - TSH Partner Salesman App
**Purpose:** App for partner salesmen network (100+ across Iraq)  
**Users:** Partner salesmen, social media sellers  
**Bundle ID:** `com.tsh.partnersales`

### 07 - TSH Wholesale Client App
**Purpose:** B2B app for wholesale clients (500+ clients)  
**Users:** Wholesale business clients  
**Bundle ID:** `com.tsh.wholesaleclient`

### 08 - TSH Consumer App
**Purpose:** B2C app for direct consumers  
**Users:** End consumers  
**Bundle ID:** `com.tsh.consumer`

### Shared - TSH Core Package
**Purpose:** Shared utilities, models, widgets, and business logic  
**Type:** Flutter package (not a standalone app)

## Development Guidelines

1. **Naming Convention:** All apps use prefix `##_tsh_<purpose>_app`
2. **Bundle IDs:** Use `com.tsh.<purpose>` format
3. **Versioning:** Semantic versioning (MAJOR.MINOR.PATCH+BUILD)
4. **Shared Code:** Place in `shared/tsh_core_package/`

## Deployment

Each app can be built for:
- 📱 iOS (iPhone/iPad)
- 🤖 Android
- 🌐 Web (Progressive Web App)

## Quick Commands

```bash
# Navigate to specific app
cd mobile/flutter_apps/01_tsh_admin_app

# Install dependencies
flutter pub get

# Run on connected device
flutter run

# Build for iOS
flutter build ios

# Build for Android
flutter build apk
```

## iOS Deployment

For iOS deployment on each app:
1. Open `ios/Runner.xcworkspace` in Xcode
2. Configure signing & capabilities
3. Select your Apple Developer team
4. Deploy to device or App Store

See individual app README files for specific deployment instructions.

---

**Last Updated:** September 30, 2025  
**System:** TSH ERP System Local
EOF

log_success "Created mobile/README.md"

# Create README for legacy directory
cat > mobile/legacy/README.md << 'EOF'
# 🗑️ Legacy / Archived Flutter Apps

This directory contains deprecated or archived Flutter apps that are no longer in active development.

## Archived Apps

- **inventory_app_legacy** - Old inventory app (replaced by inventory_app_new)
- **hr_app_legacy** - Old HR app (replaced by current hr_app)
- **salesperson_old** - Duplicate salesperson app from mobile/flutter_apps

## Why Archived?

These apps were archived for one or more reasons:
- Replaced by newer versions
- Duplicate of existing apps
- Incomplete/broken implementations
- No longer needed for business requirements

## Important

- **Do NOT delete** without reviewing
- May contain useful code for reference
- Keep for historical purposes
- Can restore if needed from here

## Restore Process

If you need to restore an archived app:
1. Review the app structure and dependencies
2. Copy from legacy/ to flutter_apps/
3. Update dependencies (`flutter pub get`)
4. Fix any compatibility issues
5. Test thoroughly before deployment

---

**Archived:** September 30, 2025
EOF

log_success "Created mobile/legacy/README.md"

log ""
log "╔═══════════════════════════════════════════════════════════════════╗"
log "║                    PHASE 7: GENERATE REPORT                        ║"
log "╚═══════════════════════════════════════════════════════════════════╝"
log ""

# Generate final structure report
log "Final Directory Structure:"
log ""
log "mobile/"
log "├── flutter_apps/"

if [ -d "mobile/flutter_apps" ]; then
    for dir in mobile/flutter_apps/*; do
        if [ -d "$dir" ]; then
            basename_dir=$(basename "$dir")
            if [ -f "$dir/pubspec.yaml" ]; then
                app_name=$(grep "^name:" "$dir/pubspec.yaml" | head -1 | awk '{print $2}' | tr -d '"' | tr -d "'")
                log "│   ├── $basename_dir/ ($app_name)"
            else
                log "│   ├── $basename_dir/"
            fi
        fi
    done
fi

log "│"
log "├── legacy/"
if [ -d "mobile/legacy" ]; then
    for dir in mobile/legacy/*; do
        if [ -d "$dir" ]; then
            log "│   ├── $(basename "$dir")/"
        fi
    done
fi
log "│"
log "└── README.md"
log ""

# Check root-level apps
if [ -d "tsh_salesperson_app" ]; then
    log ""
    log "Root-level apps (outside mobile/):"
    log "├── tsh_salesperson_app/ (iOS configured - production ready)"
fi

log ""
log "╔═══════════════════════════════════════════════════════════════════╗"
log "║                    REORGANIZATION COMPLETE!                        ║"
log "╚═══════════════════════════════════════════════════════════════════╝"
log ""
log_success "All apps reorganized successfully!"
log ""
log "Summary:"
log "  ✓ Backup created: $BACKUP_DIR"
log "  ✓ Legacy apps archived to: mobile/legacy/"
log "  ✓ Apps renamed with numbered prefixes"
log "  ✓ Shared code moved to: mobile/flutter_apps/shared/"
log "  ✓ Documentation created"
log ""
log "Next Steps:"
log "  1. Review the new structure: cd mobile/flutter_apps"
log "  2. Test each app builds: flutter pub get && flutter build"
log "  3. Update bundle IDs in iOS/Android configs"
log "  4. Update any hardcoded paths in scripts"
log "  5. Configure iOS signing for apps needing deployment"
log ""
log "Log file: $LOG_FILE"
log "Backup: $BACKUP_DIR"
log ""

echo ""
echo -e "${GREEN}✅ Reorganization completed successfully!${NC}"
echo ""
echo "Review the log file for details: $LOG_FILE"
echo ""

