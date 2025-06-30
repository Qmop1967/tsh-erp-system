# TSH ERP System - Backend Application

This is the main FastAPI backend application for the TSH ERP System.

## Structure:
```
app/
├── main.py              # FastAPI application entry point
├── init_data.py         # Data initialization utilities
├── config/              # Application configuration
├── db/                  # Database connection and utilities
├── models/              # SQLAlchemy ORM models
├── routers/             # API route handlers
├── schemas/             # Pydantic request/response schemas
└── services/            # Business logic and service layer
```

## Running the Application:
```bash
# From the project root
cd app/
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation:
When running, access the automatic API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key Features:
- **Authentication & Authorization**: JWT-based auth with role management
- **Multi-language Support**: Arabic and English localization
- **Multi-currency**: Support for IQD, USD, RMB
- **Accounting System**: Complete accounting with journal entries
- **POS System**: Point of sale with inventory management
- **Zoho Integration**: External data synchronization
