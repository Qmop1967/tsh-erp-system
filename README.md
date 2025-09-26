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
