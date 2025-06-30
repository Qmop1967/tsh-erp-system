# Database

This folder contains database-related files and migrations.

## Contents:
- `alembic/` - Database migration scripts and configuration
- `alembic.ini` - Alembic configuration file

## Usage:
```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```
