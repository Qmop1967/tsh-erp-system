# TSH ERP System

A comprehensive Enterprise Resource Planning (ERP) system for TSH Company, featuring multi-platform support with Flutter mobile apps and React web frontend.

## 📁 Project Structure

```
TSH_ERP_System_Local/
├── app/                    # FastAPI Backend (Python)
├── frontend/               # React Frontend (Web)
├── mobile/                 # Mobile Apps Directory
│   └── flutter_apps/       # All Flutter Mobile Applications
│       ├── 01_tsh_admin_app              # Admin Dashboard (with MFA)
│       ├── 02_tsh_hr_app                 # HR Management
│       ├── 03_tsh_inventory_app          # Inventory Management
│       ├── 04_tsh_retail_sales_app       # Retail Sales
│       ├── 05_tsh_salesperson_app        # Salesperson App
│       ├── 06_tsh_partner_network_app    # Partner Network
│       ├── 07_tsh_wholesale_client_app   # Wholesale Client
│       └── 08_tsh_consumer_app           # Consumer App
├── docs/                   # Documentation
│   ├── guides/            # User and developer guides
│   ├── reports/           # Status reports and summaries
│   ├── setup/             # Setup and installation guides
│   ├── architecture/      # Architecture documentation
│   ├── testing/           # Testing documentation
│   └── zoho/              # Zoho integration documentation
├── scripts/               # Utility Scripts
│   ├── testing/          # Test scripts
│   ├── zoho/             # Zoho integration scripts
│   └── utils/            # Utility scripts
├── database/              # Database files and migrations
├── config/                # Configuration files
├── tests/                 # Test suite
├── tools/                 # Development tools
├── backups/               # System backups
├── screenshots/           # Application screenshots
└── logs/                  # Application logs
```

## 🚀 Quick Start

### Backend (FastAPI)
```bash
cd TSH_ERP_System_Local
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

### Mobile Apps (Flutter)
```bash
cd mobile/flutter_apps/05_tsh_salesperson_app
flutter run -d <device-id>
```

## 📱 Mobile Applications

- **Admin App**: Full system control with MFA security
- **HR App**: Employee management and payroll
- **Inventory App**: Stock and warehouse management
- **Retail Sales App**: POS and retail operations
- **Salesperson App**: Sales team mobile interface
- **Partner Network App**: Partner and supplier management
- **Wholesale Client App**: Wholesale customer portal
- **Consumer App**: End-customer mobile app

## 🔧 Tech Stack

- **Backend**: FastAPI (Python), PostgreSQL
- **Frontend**: React, TypeScript, Vite
- **Mobile**: Flutter (Dart)
- **Integration**: Zoho Inventory, ChatGPT
- **Authentication**: JWT with RBAC
- **Security**: MFA, Session Management

## 📚 Documentation

All documentation is organized in the `/docs` directory:
- See `/docs/setup/` for installation guides
- See `/docs/guides/` for user guides
- See `/docs/reports/` for system status reports

## 🔗 Important Links

- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173
- Admin Dashboard: http://localhost:5173/admin

## 📝 License

Proprietary - TSH Company
