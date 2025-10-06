# 🏢 TSH ERP System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![Flutter](https://img.shields.io/badge/Flutter-3.0+-blue.svg)](https://flutter.dev/)

A comprehensive **Enterprise Resource Planning (ERP)** system designed for trade and services management, featuring multi-platform support with web and mobile applications.

## 🌟 Features

### 🏗️ **Core Modules**
- **👥 User Management** - Multi-tenant authentication and authorization
- **🏪 Branch & Warehouse Management** - Multi-location inventory tracking
- **📦 Inventory Management** - Real-time stock tracking and management
- **💼 Sales & Purchase Management** - Complete order lifecycle management
- **💰 Financial Management** - Accounting, invoicing, and financial reporting
- **🛒 POS System** - Point-of-sale with real-time synchronization
- **💸 Cash Flow Management** - Cash tracking and transfer management
- **📊 Reporting & Analytics** - Comprehensive business intelligence

### 🌍 **Multi-Platform Support**
- **🌐 Web Application** - React-based admin dashboard
- **📱 Mobile Applications** - 17+ Flutter-based mobile apps including:
  - Admin Dashboard
  - Salesperson App
  - Inventory Management
  - HR Management
  - Travel Sales
  - Retail Sales
  - And more...

### 🔧 **Technical Features**
- **🌐 Multi-language Support** (Arabic/English)
- **🔐 Advanced Security** - JWT authentication, role-based permissions
- **📡 Real-time Updates** - WebSocket integration for live data
- **🗄️ Database Management** - PostgreSQL with Alembic migrations
- **🐳 Containerization** - Docker support for easy deployment
- **📋 Comprehensive Testing** - Unit and integration tests
- **📚 API Documentation** - Auto-generated OpenAPI/Swagger docs

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Flutter 3.0+ (for mobile development)

### 🖥️ Backend Setup (FastAPI)

```bash
# Clone the repository
git clone git@github.com:Qmop1967/tsh-erp-system.git
cd tsh-erp-system

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r config/requirements.txt

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

### 🌐 Frontend Setup (React)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The web application will be available at `http://localhost:5173`

### 📱 Mobile App Setup (Flutter)

```bash
# Navigate to specific mobile app
cd mobile/flutter_apps/admin_dashboard

# Get dependencies
flutter pub get

# Run the app
flutter run
```

## 📁 Project Structure

```
TSH ERP System/
├── 🖥️  app/                    # FastAPI Backend Application
│   ├── models/                # Database models
│   ├── routers/              # API route handlers
│   ├── services/             # Business logic
│   ├── schemas/              # Pydantic schemas
│   └── db/                   # Database configuration
├── 🌐 frontend/               # React Web Application
│   ├── src/                  # Source code
│   ├── public/               # Static assets
│   └── build/                # Production build
├── 📱 mobile/                 # Mobile Applications
│   ├── flutter_apps/         # Flutter applications
│   │   ├── admin_dashboard/
│   │   ├── salesperson/
│   │   ├── inventory_app/
│   │   ├── hr_app/
│   │   └── ...               # 17+ mobile apps
│   ├── ios/                  # iOS specific files
│   └── android/              # Android specific files
├── 🗄️  database/              # Database Schema & Migrations
├── ⚙️  config/                # Configuration Files
├── 🔧 scripts/               # Utility Scripts
├── 📚 docs/                  # Documentation
├── 🧪 tests/                 # Test Files
├── 🐳 docker/                # Docker Configuration
└── 🛠️  tools/                 # Development Tools
```

## 📱 Mobile Applications

The system includes 17+ specialized Flutter applications:

| App | Description |
|-----|-------------|
| **Admin Dashboard** | Complete system administration |
| **Salesperson App** | Mobile sales management |
| **Inventory App** | Stock management on-the-go |
| **HR App** | Human resources management |
| **Travel Sales** | Travel booking and management |
| **Retail Sales** | Retail point-of-sale |
| **Client App** | Customer portal |
| **Consumer App** | End-user interface |
| **Partners App** | Partner management |

## 🔐 Security Features

- **JWT Authentication** - Secure token-based authentication
- **Role-Based Access Control** - Granular permission system
- **Multi-tenant Architecture** - Data isolation between organizations
- **Audit Logging** - Complete activity tracking
- **Data Encryption** - Sensitive data protection
- **API Rate Limiting** - Protection against abuse

## 🌍 Internationalization

- **Arabic Language Support** - Complete RTL interface
- **English Language Support** - Full LTR interface
- **Multi-currency Support** - Handle multiple currencies
- **Localized Date/Time** - Regional formatting

## 📊 Database Schema

The system uses PostgreSQL with comprehensive models including:

- User Management (Users, Roles, Permissions)
- Inventory (Products, Categories, Stock Movements)
- Sales (Orders, Invoices, Payments)
- Accounting (Chart of Accounts, Journal Entries)
- POS (Terminals, Transactions, Sessions)
- And much more...

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t tsh-erp-system .
docker run -p 8000:8000 tsh-erp-system
```

## 📋 Testing

```bash
# Backend tests
python -m pytest tests/

# Frontend tests
cd frontend
npm test

# Mobile tests
cd mobile/flutter_apps/admin_dashboard
flutter test
```

## 📚 Documentation

- **[API Documentation](http://localhost:8000/docs)** - Auto-generated Swagger UI
- **[System Guides](docs/guides/)** - Setup and configuration guides
- **[Implementation Details](docs/implementation/)** - Technical documentation
- **[Deployment Guide](docs/deployment/)** - Production deployment instructions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔧 Development

### Environment Setup
```bash
# Backend development
source .venv/bin/activate
python -m uvicorn app.main:app --reload

# Frontend development
cd frontend && npm run dev

# Mobile development
cd mobile/flutter_apps/[app_name] && flutter run
```

### Code Style
- **Python**: Follow PEP 8, use Black formatter
- **JavaScript/TypeScript**: Use Prettier, ESLint
- **Flutter**: Follow Dart style guide

## 📞 Support

For support and questions, please open an issue in the GitHub repository.

---

**Last Updated:** September 2025
**Version:** 1.0.0
**Status:** Production Ready ✅
