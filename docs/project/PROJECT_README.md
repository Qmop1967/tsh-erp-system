# TSH ERP System

A comprehensive ERP system built with FastAPI and PostgreSQL, supporting accounting, point of sale, and multi-language/currency operations.

## 🗂️ Project Organization

The project has been organized into logical folders for better maintainability:

### 📁 Core Application
- **`app/`** - Main FastAPI application (models, routers, services, schemas)
- **`frontend/`** - Vue.js frontend application with multiple modules and build files

### 📁 Configuration & Dependencies
- **`config/`** - Configuration files, credentials, and dependencies
  - Environment templates and Python requirements
  - Encrypted credentials and security keys
  - ⚠️ Contains sensitive files - handle with care

### 📁 Mobile Applications  
- **`mobile/`** - Flutter/Dart mobile applications
  - iOS Admin App
  - Shared libraries, configurations, and Dart toolchain

### 📁 Development & Operations
- **`docker/`** - Docker configuration files (Dockerfile, docker-compose.yml)
- **`database/`** - Database migrations and Alembic configuration
- **`scripts/`** - Utility scripts organized by purpose:
  - `setup/` - System initialization scripts
  - `data/` - Data management and sample data scripts
  - Migration scripts for system updates

### 📁 Quality Assurance
- **`tests/`** - All test files (API tests, integration tests, unit tests)

### 📁 Documentation & Tools
- **`docs/`** - All documentation, status reports, and guides
- **`tools/`** - Development tools, debug scripts, and utilities

## 🚀 Quick Start

### Using Docker (Recommended)
```bash
# Build and run the application
cd docker/
docker-compose up --build

# Run in background
docker-compose up -d
```

### Local Development
```bash
# Install dependencies
pip install -r config/requirements.txt

# Set up environment
cp config/env.example .env
# Edit .env with your configuration

# Initialize database
python scripts/setup/init_user_system.py
python scripts/setup/init_accounting_data.py

# Run the application
cd app/
python main.py
```

## 📊 Features

### 🧮 Accounting System
- Multi-currency support (IQD, USD, RMB)
- Multi-language support (Arabic, English)  
- Chart of accounts management
- Journal entries and financial periods
- Financial reports (Trial Balance, Balance Sheet, Income Statement)
- Exchange rate management

### 🛒 Point of Sale (POS)
- Multi-device POS management
- Session and cash management
- Sales transactions and returns
- Multiple payment methods
- Discount and promotion system
- Real-time inventory checking
- Comprehensive reporting

### 👥 Customer & Inventory Management
- Customer relationship management
- Product and inventory management
- Zoho integration for external data
- Multi-location inventory tracking

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test category
python -m pytest tests/test_auth.py
python -m pytest tests/test_inventory_api.py
```

## 📖 Documentation

All documentation is organized in the `docs/` folder:
- Setup guides and installation instructions
- API documentation and user manuals
- System status reports and completion summaries
- Feature enhancement documentation

## 🛠️ Development Tools

The `tools/` folder contains:
- Debug scripts for troubleshooting
- Development utilities and helpers
- Test HTML files for frontend testing
- System startup scripts

## 🔧 Scripts

Use the organized scripts in the `scripts/` folder:

### Setup Scripts (`scripts/setup/`)
```bash
python scripts/setup/init_user_system.py    # Initialize user system
python scripts/setup/init_accounting_data.py # Set up accounting data
python scripts/setup/init_items_data.py      # Initialize inventory items
```

### Data Management (`scripts/data/`)
```bash
python scripts/data/add_sample_customers.py   # Add sample customers
python scripts/data/setup_tsh_data.py         # Set up TSH-specific data
python scripts/data/verify_tsh_data.py        # Verify data integrity
```

## 🏗️ Technology Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: Vue.js, TypeScript, Tailwind CSS
- **Mobile**: Flutter, Dart
- **Database**: PostgreSQL with Alembic migrations
- **Containerization**: Docker, Docker Compose
- **Testing**: pytest, API testing frameworks

## 📝 Environment Configuration

Copy `config/env.example` to `.env` and configure:
```env
DATABASE_URL=postgresql://user:password@localhost/tsh_erp
SECRET_KEY=your-secret-key
ZOHO_CLIENT_ID=your-zoho-client-id
ZOHO_CLIENT_SECRET=your-zoho-client-secret
```

⚠️ **Security Note**: The `config/` folder contains sensitive files including encryption keys and credentials. Ensure proper file permissions and never commit actual credentials to version control.

## 🤝 Contributing

1. Follow the organized folder structure
2. Place new files in appropriate directories
3. Update documentation in the `docs/` folder
4. Add tests in the `tests/` folder
5. Use scripts in `scripts/` for automation

## 📞 Support

For support and questions, refer to the documentation in the `docs/` folder or check the specific README files in each organized directory.
