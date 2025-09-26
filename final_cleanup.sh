#!/bin/bash

# Final cleanup script to remove remaining redundant files
# and complete the organization

set -e

PROJECT_DIR="/Users/khaleelal-mulla/Desktop/TSH ERP System"
cd "$PROJECT_DIR"

echo "🧹 Final TSH ERP System Cleanup"
echo "==============================="

# Function to safely remove files
safe_remove() {
    local path="$1"
    if [ -e "$path" ]; then
        echo "🗑️  Removing: $path"
        rm -rf "$path"
    fi
}

# Function to safely move files  
safe_move() {
    local source="$1"
    local destination="$2"
    if [ -e "$source" ]; then
        echo "📦 Moving: $source → $destination"
        mkdir -p "$(dirname "$destination")"
        mv "$source" "$destination"
    fi
}

echo ""
echo "📚 Moving Remaining Documentation Files"
echo "-------------------------------------"

# Move remaining status/documentation files to proper locations
safe_move "ACCOUNTING_MODULE_ENABLED_POSTGRESQL.md" "docs/modules/"
safe_move "CENTRAL_DATABASE_INTEGRATION_ANALYSIS.md" "docs/system/"
safe_move "FRONTEND_NAVIGATION_FIXES.md" "docs/status_reports/"
safe_move "INVENTORY_MODULE_PLAN.md" "docs/modules/"
safe_move "LANGUAGE_SYSTEM_DOCUMENTATION.md" "docs/system/"
safe_move "PROJECT_STATE_WORKING.md" "docs/status_reports/"
safe_move "ROUTER_NAVIGATION_ANALYSIS.md" "docs/system/"
safe_move "SYSTEM_STATUS_REPORT.md" "docs/status_reports/"
safe_move "TSH_ERP_MASTER_DEVELOPMENT_PLAN.md" "docs/project/"

echo ""
echo "🗂️  Moving Empty/Utility Files"
echo "-----------------------------"

# Move utility scripts to proper locations
safe_move "dev-start.sh" "scripts/dev/"
safe_move "setup-protection.sh" "scripts/setup/"
safe_move "status-check.sh" "scripts/dev/"
safe_move "test_auth_flow.sh" "scripts/dev/"

echo ""
echo "📁 Creating Final Directory Structure Documentation"
echo "-------------------------------------------------"

# Create comprehensive directory structure documentation
cat > "PROJECT_STRUCTURE.md" << 'EOF'
# TSH ERP System - Project Structure

## 📁 Complete Directory Layout

```
TSH ERP System/
├── 🖥️  app/                       # Backend FastAPI Application
│   ├── models/                    # Database models
│   ├── routers/                   # API route handlers  
│   ├── schemas/                   # Pydantic schemas
│   ├── services/                  # Business logic services
│   └── config/                    # App configuration
├── 🌐 frontend/                   # Main React Web Application
│   ├── src/                       # Source code
│   ├── public/                    # Static assets
│   └── build/                     # Production build
├── 📱 mobile/                     # Mobile Applications
│   ├── flutter_apps/              # Flutter Applications
│   │   ├── admin_dashboard/       # Admin Dashboard App
│   │   ├── client_app/            # Client Management App
│   │   ├── consumer_app/          # Consumer App
│   │   ├── hr_app/                # HR Management App
│   │   ├── inventory_app/         # Inventory Management App
│   │   ├── partners_app/          # Partners App
│   │   ├── retail_sales/          # Retail Sales App
│   │   ├── salesperson/           # Salesperson App
│   │   ├── travel_sales/          # Travel Sales App
│   │   └── core_package/          # Shared Flutter Components
│   ├── ios/                       # iOS specific files
│   └── android/                   # Android specific files
├── 🗄️  database/                 # Database Schema & Migrations
│   └── alembic/                   # Database migration files
├── ⚙️  config/                    # System Configuration Files
├── 🔧 scripts/                    # Utility Scripts
│   ├── setup/                     # Setup and installation scripts
│   ├── dev/                       # Development helper scripts
│   ├── maintenance/               # System maintenance scripts
│   └── data/                      # Data migration/seeding scripts
├── 📚 docs/                       # Documentation
│   ├── guides/                    # User and deployment guides
│   ├── implementation/            # Technical implementation docs
│   ├── modules/                   # Module-specific documentation
│   ├── project/                   # Project status and planning
│   ├── status_reports/            # Implementation status reports
│   └── system/                    # System architecture docs
├── 🧪 tests/                      # Test Files
├── 🐳 docker/                     # Docker Configuration
├── 🛠️  tools/                     # Development Tools
├── 💾 backups/                    # System Backups
│   └── archive/                   # Archived files
└── 📦 tsh_salesperson_app/        # Legacy Flutter Framework
```

## 🎯 Key Features by Directory

### Backend (`app/`)
- FastAPI REST API
- PostgreSQL database integration
- Authentication & authorization
- Multi-tenant architecture
- Comprehensive business logic

### Frontend (`frontend/`)
- React TypeScript application
- Modern UI with Tailwind CSS
- Multi-language support (Arabic/English)
- Responsive design
- Real-time updates

### Mobile (`mobile/`)
- **10 Specialized Flutter Apps**
- Native iOS and Android support
- Offline capabilities
- GPS tracking features
- Synchronized with web platform

### Documentation (`docs/`)
- Complete API documentation
- Deployment guides
- System architecture
- Implementation status
- User manuals

## 🚀 Development Workflow

1. **Backend Development**
   ```bash
   cd app && python -m uvicorn main:app --reload
   ```

2. **Frontend Development**  
   ```bash
   cd frontend && npm run dev
   ```

3. **Mobile Development**
   ```bash
   cd mobile/flutter_apps/[app_name] && flutter run
   ```

## 📈 System Benefits

✅ **Organized Structure** - Clear separation of concerns
✅ **Scalable Architecture** - Modular design for growth  
✅ **Multi-Platform** - Web + Mobile + API
✅ **Well Documented** - Comprehensive documentation
✅ **Production Ready** - Complete deployment setup

---
**Updated:** September 2025
EOF

echo "📝 Created PROJECT_STRUCTURE.md"

echo ""
echo "🎯 Final Cleanup Summary"
echo "======================="

# Show final directory count
echo "📊 Directory Statistics:"
echo "- Mobile Apps: $(ls mobile/flutter_apps/ | wc -l | xargs) Flutter applications"
echo "- Documentation: $(find docs/ -name "*.md" | wc -l | xargs) documentation files"  
echo "- Scripts: $(find scripts/ -name "*.sh" -o -name "*.py" | wc -l | xargs) utility scripts"
echo "- Tests: $(find tests/ -name "*.py" | wc -l | xargs) test files"

echo ""
echo "✅ Final Organization Complete!"
echo "============================="
echo ""
echo "🎉 TSH ERP System is now fully organized with:"
echo "   📱 10 Mobile applications in mobile/flutter_apps/"  
echo "   🌐 1 Main web application in frontend/"
echo "   🖥️  1 Backend API in app/"
echo "   📚 Comprehensive documentation in docs/"
echo "   🔧 Organized utility scripts in scripts/"
echo ""
echo "📍 Ready for development and deployment!"
echo ""
EOF
