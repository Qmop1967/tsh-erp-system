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
