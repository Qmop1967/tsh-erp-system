# 🏢 TSH ERP Ecosystem

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![Flutter](https://img.shields.io/badge/Flutter-3.0+-blue.svg)](https://flutter.dev/)

A comprehensive **Enterprise Resource Planning (ERP)** ecosystem designed for trade and services management, featuring multi-platform support with web and mobile applications.

## 🌟 Overview

The TSH ERP Ecosystem is a complete business management solution designed for import-distribution-retail operations, supporting:
- **500+ wholesale clients** with 30 daily wholesale orders
- **30 daily retail customers** with 1M IQD average transaction
- **100+ partner salesmen** across all Iraq cities
- **12 travel salespersons** handling $35K USD weekly
- **Multi-location inventory** with dual supply chain (China + local vendors)
- **8 specialized mobile applications** for different user roles

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Flutter 3.0+ (for mobile development)

### Backend Setup

```bash
# Clone the repository
git clone <repository-url>
cd TSH_ERP_Ecosystem

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp config/env.example .env
# Edit .env with your database credentials

# Run database migrations
cd database
alembic upgrade head

# Start the backend server
cd ..
python -m uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

### Frontend Setup

```bash
# Navigate to frontend directory
cd app

# Install dependencies
npm install

# Start development server
npm run dev
```

## 📁 Project Structure

```
TSH_ERP_Ecosystem/
├── app/                    # FastAPI Backend Application
│   ├── models/            # Database models
│   ├── routers/           # API route handlers
│   ├── services/          # Business logic
│   └── schemas/           # Pydantic schemas
├── apps/                  # Web Applications
├── mobile/                # Mobile Applications (Flutter)
├── database/              # Database Schema & Migrations
├── config/                # Configuration Files
├── scripts/               # Utility Scripts
├── docs/                  # Comprehensive Documentation
│   ├── architecture/      # Architecture documentation
│   ├── deployment/        # Deployment guides
│   ├── guides/            # Setup and quick start guides
│   ├── integrations/      # Integration documentation (Zoho, TDS)
│   ├── implementation/    # Implementation details
│   ├── migrations/        # Migration guides
│   ├── security/          # Security documentation
│   └── status/            # Project status and reports
├── tests/                 # Test Files
├── deployment/            # Deployment configurations
├── tools/                 # Development Tools
└── archived/              # Archived files
```

## 📱 Mobile Applications

The ecosystem includes 8 specialized Flutter applications:

1. **TSH Admin App** - Complete project control for owner
2. **Admin Mobile App** - Full permissions for on-the-go management
3. **TSH HR Mobile App** - Complete HR management (payroll, attendance, performance)
4. **TSH Retailer Shop App** - Specialized for retailer shop operations
5. **TSH Inventory Management App** - Multi-location inventory tracking
6. **Travel Salesperson App** - Money tracking and GPS
7. **Wholesale Client App** - B2B operations
8. **TSH Consumer App** - Direct consumer interface
9. **Partner Salesman App** - Social media sellers

## 🔧 Key Features

### Core Modules
- **User Management** - Multi-tenant authentication and authorization
- **Inventory Management** - Real-time stock tracking with dual supply chain support
- **Sales & Purchase** - Complete order lifecycle management
- **Financial Management** - Accounting, invoicing, and financial reporting
- **POS System** - Point-of-sale with real-time synchronization
- **Cash Flow Management** - Money transfer tracking (ALTaif, ZAIN Cash, SuperQi)
- **Reporting & Analytics** - Comprehensive business intelligence

### Technical Features
- **Multi-language Support** - Arabic/English with RTL support
- **Advanced Security** - JWT authentication, role-based permissions
- **Real-time Updates** - WebSocket integration for live data
- **API Integration** - Zoho Books, TDS Core integrations
- **GPS Tracking** - All-day tracking for travel salespersons
- **WhatsApp Integration** - Customer communication and notifications
- **AI Customer Assistant** - 24/7 bilingual AI assistant

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Architecture](docs/architecture/)** - System architecture and design decisions
- **[Deployment](docs/deployment/)** - Production deployment guides
- **[Guides](docs/guides/)** - Setup and quick start guides
- **[Integrations](docs/integrations/)** - Zoho and TDS integration documentation
- **[Implementation](docs/implementation/)** - Technical implementation details
- **[Security](docs/security/)** - Security features and best practices
- **[Status Reports](docs/status/)** - Project status and completion reports

See [docs/README.md](docs/README.md) for complete documentation index.

## 🔐 Security

- JWT Authentication
- Role-Based Access Control (RBAC)
- Multi-tenant Architecture
- Audit Logging
- Data Encryption
- API Rate Limiting
- Fraud Prevention System

## 🌍 Internationalization

- **Arabic Language Support** - Complete RTL interface
- **English Language Support** - Full LTR interface
- **Multi-currency Support** - Handle multiple currencies (IQD, USD)
- **Localized Date/Time** - Regional formatting

## 🧪 Testing

```bash
# Backend tests
python -m pytest tests/

# Frontend tests
cd app && npm test

# Mobile tests
cd mobile/[app_name] && flutter test
```

## 🚀 Production Deployment

### Direct Deployment (Primary Method)

TSH ERP uses **direct deployment** from development to production, bypassing GitHub for faster and more reliable deployments.

```bash
# One-command deployment to production
./scripts/deploy_direct_to_production.sh
```

**What happens:**
1. ✅ Validates SSH connection to production server
2. ✅ Shows what will be deployed and asks for confirmation
3. ✅ Syncs files directly using rsync over SSH
4. ✅ Rebuilds Docker containers on production
5. ✅ Restarts services and verifies health

**Complete documentation:** See `docs/DIRECT_DEPLOYMENT_WORKFLOW.md` for full workflow, troubleshooting, and rollback procedures.

### Why Direct Deployment?

- **⚡ Speed**: Deploy in seconds, not minutes
- **🎯 Simplicity**: One command, automatic verification
- **🔒 Control**: Full visibility into deployment process
- **💪 Reliability**: No dependency on external services
- **🔄 Flexibility**: Easy rollback and testing

### Prerequisites for Production Deployment

```bash
# 1. Configure SSH access (one-time setup)
./scripts/setup_local_ssh_config.sh

# 2. Test SSH connection
ssh tsh-vps

# 3. Ready to deploy!
./scripts/deploy_direct_to_production.sh
```

## 🐳 Docker Deployment

```bash
# Local development (hot reload + pgAdmin)
APP_ENV_FILE=.env.dev docker compose --profile dev -f docker-compose.yml -f docker-compose.dev.yml up

# Production-style (with Nginx reverse proxy)
docker compose --profile proxy up -d
```

See `docs/docker/README.md` for full container orchestration guidance.

## 📋 Development Guidelines

### Code Style
- **Python**: Follow PEP 8, use Black formatter
- **JavaScript/TypeScript**: Use Prettier, ESLint
- **Flutter**: Follow Dart style guide

### Before Writing New Code
1. **Search the codebase** for similar functionality
2. **Enhance existing code** rather than creating duplicates
3. **Check** `/scripts/`, `/mobile/`, and integration directories
4. **Follow** the established architecture patterns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](docs/LICENSE) file for details.

## 📞 Support

For support and questions, please open an issue in the repository.

---

**Last Updated:** November 2025  
**Version:** 2.0.0  
**Status:** Production Ready ✅

