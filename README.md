# TSH ERP System

A comprehensive Enterprise Resource Planning (ERP) system built with FastAPI, React, and Flutter for multi-platform support.

## 📁 Project Structure

```
TSH ERP System/
├── app/                    # Backend API (FastAPI)
│   ├── config/            # Application configuration
│   ├── models/            # Database models
│   ├── routers/           # API routes
│   ├── schemas/           # Pydantic schemas
│   └── services/          # Business logic services
├── frontend/              # Frontend applications
│   ├── src/              # React/TypeScript web app
│   ├── tsh_admin_dashboard/     # Flutter admin app
│   ├── tsh_client_app/          # Flutter client app
│   ├── tsh_consumer_app/        # Flutter consumer app
│   ├── tsh_partners_app/        # Flutter partners app
│   ├── tsh_retail_sales/        # Flutter retail app
│   ├── tsh_salesperson/         # Flutter salesperson app
│   └── tsh_core_package/        # Shared Flutter package
├── database/              # Database management
│   ├── alembic/          # Database migrations
│   └── README.md         # Database setup guide
├── docs/                  # Documentation (organized by category)
│   ├── modules/          # Module-specific documentation
│   ├── implementation/   # Implementation guides
│   ├── system/          # System documentation
│   ├── deployment/      # Deployment guides
│   └── project/         # Project status and overview
├── scripts/              # Utility scripts (organized by purpose)
│   ├── dev/             # Development scripts
│   ├── maintenance/     # Maintenance scripts
│   ├── setup/           # Setup scripts
│   └── data/            # Data management scripts
├── config/               # Configuration files
│   ├── env.example      # Environment variables template
│   ├── requirements.txt # Python dependencies
│   └── README.md        # Configuration guide
├── docker/               # Docker configuration
├── tools/                # Development tools
└── tests/                # Test suites
```

## 🚀 Quick Start

### Development Environment
```bash
# Start development server
./scripts/dev/dev-start.sh

# Check system status
./scripts/dev/status-check.sh
```

### Database Setup
```bash
# Initialize database
./scripts/setup/init_accounting_data.py

# Run migrations
cd database && alembic upgrade head
```

### System Maintenance
```bash
# Create backup
./scripts/maintenance/backup.sh

# Setup protection
./scripts/setup/setup-protection.sh
```

## 📚 Documentation

- **[System Documentation](docs/system/)** - Core system documentation
- **[Module Documentation](docs/modules/)** - Individual module guides
- **[Implementation Guides](docs/implementation/)** - Step-by-step implementation
- **[Deployment Guide](docs/deployment/)** - Deployment instructions
- **[Project Status](docs/project/)** - Current project state and roadmap

## 🛠️ Technology Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: React, TypeScript, Vite
- **Mobile**: Flutter (Multi-app ecosystem)
- **Database**: PostgreSQL with Alembic migrations
- **Authentication**: JWT-based authentication
- **Containerization**: Docker

## 🏗️ Architecture

The system follows a modular architecture with:
- **Multi-tenant support** with branch-based data isolation
- **Multi-language support** with dynamic translations
- **Multi-platform frontend** (Web + Flutter apps)
- **RESTful API** with comprehensive documentation
- **Database migrations** with Alembic

## 📱 Applications

1. **Web Dashboard** - Main administrative interface
2. **Admin Dashboard** - Flutter-based admin app
3. **Client App** - Customer-facing application
4. **Consumer App** - End-consumer interface
5. **Partners App** - Partner management
6. **Retail Sales** - Point-of-sale system
7. **Salesperson App** - Mobile sales interface

## 🔧 Development

### Prerequisites
- Python 3.8+
- Node.js 16+
- Flutter SDK
- PostgreSQL
- Docker (optional)

### Setup
1. Clone the repository
2. Install dependencies: `pip install -r config/requirements.txt`
3. Configure environment: `cp config/env.example .env`
4. Initialize database: `./scripts/setup/init_accounting_data.py`
5. Start development server: `./scripts/dev/dev-start.sh`

## 📄 License

This project is proprietary software developed for TSH ERP System.

## 🤝 Contributing

Please refer to the project documentation in `docs/` for contribution guidelines and development workflows. 