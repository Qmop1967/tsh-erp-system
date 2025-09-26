#!/bin/bash

# TSH ERP System Organization Script
# This script will clean up, organize, and remove duplicate/draft files

set -e  # Exit on any error

PROJECT_DIR="/Users/khaleelal-mulla/Desktop/TSH ERP System"
cd "$PROJECT_DIR"

echo "🏢 TSH ERP System - Organization & Cleanup"
echo "=========================================="
echo "📍 Working Directory: $PROJECT_DIR"
echo ""

# Function to safely remove files/directories
safe_remove() {
    local path="$1"
    if [ -e "$path" ]; then
        echo "🗑️  Removing: $path"
        rm -rf "$path"
    else
        echo "⚠️  Not found: $path"
    fi
}

# Function to safely move files/directories
safe_move() {
    local source="$1"
    local destination="$2"
    if [ -e "$source" ]; then
        echo "📦 Moving: $source → $destination"
        mkdir -p "$(dirname "$destination")"
        mv "$source" "$destination"
    else
        echo "⚠️  Source not found: $source"
    fi
}

# Create backup of current state before cleanup
echo "💾 Creating backup of current state..."
git add . 2>/dev/null || true
git commit -m "📦 Backup before system organization ($(date))" 2>/dev/null || true

echo ""
echo "🧹 Phase 1: Removing Backup Files"
echo "--------------------------------"

# Remove .backup files
safe_remove "frontend/src/App.tsx.backup"
safe_remove "frontend/src/App_backup_current.tsx"
safe_remove "frontend/src/App_backup.tsx"
safe_remove "frontend/tsh_admin_dashboard/lib/main.dart.backup"
safe_remove "frontend/tsh_admin_dashboard/lib/main.dart.backup_current"
safe_remove "frontend/tsh_salesperson/lib/features/dashboard/presentation/pages/dashboard_page_backup.dart"

echo ""
echo "🧪 Phase 2: Removing Test Files"
echo "------------------------------"

# Remove temporary test files
safe_remove "frontend/font-test.html"
safe_remove "frontend/test-minimal.html"
safe_remove "frontend/settings-test.html"
safe_remove "frontend/quick-login.html"
safe_remove "clear-auth.html"

echo ""
echo "🗂️  Phase 3: Removing Temporary Files"
echo "------------------------------------"

# Remove temporary directories and files
safe_remove "temp/"
safe_remove "frontend_debug.js"
safe_remove "untitled folder/"

# Remove .DS_Store files
find . -name ".DS_Store" -type f -delete 2>/dev/null || true
echo "🧹 Removed .DS_Store files"

echo ""
echo "📁 Phase 4: Creating New Directory Structure"
echo "-------------------------------------------"

# Create mobile directory structure
mkdir -p "mobile/flutter_apps"
mkdir -p "mobile/ios"
mkdir -p "mobile/android"
mkdir -p "backups/archive"

echo ""
echo "📱 Phase 5: Moving Mobile Applications"
echo "------------------------------------"

# Move Flutter apps to mobile directory
safe_move "frontend/tsh_admin_dashboard" "mobile/flutter_apps/admin_dashboard"
safe_move "frontend/tsh_client_app" "mobile/flutter_apps/client_app"
safe_move "frontend/tsh_consumer_app" "mobile/flutter_apps/consumer_app"
safe_move "frontend/tsh_hr_app_new" "mobile/flutter_apps/hr_app"
safe_move "frontend/tsh_inventory_app_new" "mobile/flutter_apps/inventory_app"
safe_move "frontend/tsh_partners_app" "mobile/flutter_apps/partners_app"
safe_move "frontend/tsh_retail_sales" "mobile/flutter_apps/retail_sales"
safe_move "frontend/tsh_salesperson" "mobile/flutter_apps/salesperson"
safe_move "frontend/tsh_travel_sales" "mobile/flutter_apps/travel_sales"

# Move core package if it exists
if [ -d "frontend/tsh_core_package" ]; then
    safe_move "frontend/tsh_core_package" "mobile/flutter_apps/core_package"
fi

# Move HR app (old version) if it exists
if [ -d "frontend/tsh_hr_app" ]; then
    safe_move "frontend/tsh_hr_app" "mobile/flutter_apps/hr_app_legacy"
fi

# Move inventory app (old version) if it exists  
if [ -d "frontend/tsh_inventory_app" ]; then
    safe_move "frontend/tsh_inventory_app" "mobile/flutter_apps/inventory_app_legacy"
fi

# Move iOS directory
if [ -d "ios" ]; then
    safe_move "ios" "mobile/ios"
fi

# Move large Flutter SDK if needed (optional - comment out if you want to keep it)
# safe_move "tsh_salesperson_app" "mobile/flutter_framework"

echo ""
echo "📦 Phase 6: Organizing Archives"
echo "-----------------------------"

# Move archive files
safe_move "tsh_salesperson_app_ios.tar.gz" "backups/archive/"

echo ""
echo "📚 Phase 7: Consolidating Documentation"
echo "--------------------------------------"

# Create comprehensive documentation directory structure
mkdir -p "docs/status_reports"
mkdir -p "docs/implementation" 
mkdir -p "docs/guides"

# Move status files to organized location
if [ -f "IMPLEMENTATION_COMPLETE_FINAL.md" ]; then
    safe_move "IMPLEMENTATION_COMPLETE_FINAL.md" "docs/status_reports/"
fi

if [ -f "INTEGRATION_COMPLETE_SUMMARY.md" ]; then
    safe_move "INTEGRATION_COMPLETE_SUMMARY.md" "docs/status_reports/"
fi

if [ -f "FRONTEND_PERMISSIONS_CONFIRMED.md" ]; then
    safe_move "FRONTEND_PERMISSIONS_CONFIRMED.md" "docs/status_reports/"
fi

if [ -f "PERMISSIONS_IMPLEMENTATION_COMPLETE.md" ]; then
    safe_move "PERMISSIONS_IMPLEMENTATION_COMPLETE.md" "docs/status_reports/"
fi

if [ -f "LANGUAGE_IMPLEMENTATION_COMPLETE.md" ]; then
    safe_move "LANGUAGE_IMPLEMENTATION_COMPLETE.md" "docs/status_reports/"
fi

if [ -f "PROJECT_ORGANIZATION_SUMMARY.md" ]; then
    safe_move "PROJECT_ORGANIZATION_SUMMARY.md" "docs/status_reports/"
fi

# Move guide files
if [ -f "QUICK_DEPLOYMENT_GUIDE.md" ]; then
    safe_move "QUICK_DEPLOYMENT_GUIDE.md" "docs/guides/"
fi

if [ -f "DEPLOYMENT_READY.md" ]; then
    safe_move "DEPLOYMENT_READY.md" "docs/guides/"
fi

echo ""
echo "🗂️  Phase 8: Creating Updated README Structure"
echo "--------------------------------------------"

# Update main README with new structure
cat > "README_NEW.md" << 'EOF'
# 🏢 TSH ERP System

A comprehensive Enterprise Resource Planning system for trade and services management.

## 📁 Project Structure

```
TSH ERP System/
├── app/                    # 🖥️  Backend FastAPI Application
├── frontend/              # 🌐 Main React Web Application
├── mobile/                # 📱 Mobile Applications
│   ├── flutter_apps/     # Flutter Applications
│   │   ├── admin_dashboard/
│   │   ├── client_app/
│   │   ├── consumer_app/
│   │   ├── hr_app/
│   │   ├── inventory_app/
│   │   ├── partners_app/
│   │   ├── retail_sales/
│   │   ├── salesperson/
│   │   └── travel_sales/
│   ├── ios/              # iOS Specific Files
│   └── android/          # Android Specific Files
├── database/              # 🗄️  Database Schema & Migrations
├── config/                # ⚙️  Configuration Files
├── scripts/               # 🔧 Utility Scripts
├── docs/                  # 📚 Documentation
├── tests/                 # 🧪 Test Files
├── docker/                # 🐳 Docker Configuration
└── tools/                 # 🛠️  Development Tools
```

## 🚀 Quick Start

### Backend (FastAPI)
```bash
cd app
python -m uvicorn main:app --reload
```

### Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

### Mobile Apps (Flutter)
```bash
cd mobile/flutter_apps/[app_name]
flutter run
```

## 📖 Documentation

- **[System Status Reports](docs/status_reports/)** - Implementation status and progress
- **[Deployment Guides](docs/guides/)** - Setup and deployment instructions  
- **[API Documentation](http://localhost:8000/docs)** - Auto-generated API docs
- **[Implementation Details](docs/implementation/)** - Technical implementation details

## 🎯 Features

- **Multi-language Support** (Arabic/English)
- **Modular Architecture** (Web + Mobile)
- **Real-time Updates** 
- **Secure Authentication**
- **Comprehensive Backup System**
- **Multi-tenant Support**

## 🔧 Development

See individual README files in each directory for specific development instructions.

---
**Last Updated:** September 2025
EOF

echo "📝 Updated main README created (README_NEW.md)"

echo ""
echo "🧹 Phase 9: Cleaning Build Artifacts"
echo "-----------------------------------"

# Clean build artifacts in frontend
if [ -d "frontend/node_modules" ] && [ -f "frontend/package.json" ]; then
    echo "🧹 Keeping frontend/node_modules (has package.json)"
else
    safe_remove "frontend/node_modules"
fi

safe_remove "frontend/dist"
safe_remove "frontend/.vite"

echo ""
echo "✅ Phase 10: Final Verification"
echo "-----------------------------"

# Show directory structure
echo "📁 New directory structure:"
echo ""
find . -maxdepth 2 -type d | head -20 | sort

echo ""
echo "📊 Cleanup Summary:"
echo "=================="

# Calculate space saved (rough estimate)
echo "✅ Removed backup files"
echo "✅ Removed temporary test files"  
echo "✅ Organized mobile applications"
echo "✅ Consolidated documentation"
echo "✅ Cleaned build artifacts"
echo "✅ Created logical directory structure"

echo ""
echo "🎉 System Organization Complete!"
echo "==============================="
echo ""
echo "📍 Next Steps:"
echo "1. Review the new structure: ls -la"
echo "2. Test applications in new locations"  
echo "3. Replace old README: mv README_NEW.md README.md"
echo "4. Commit changes: git add . && git commit -m 'Organized system structure'"
echo ""
echo "📚 Documentation: see docs/ directory"
echo "🏃 Quick Start: see README_NEW.md"
echo ""
