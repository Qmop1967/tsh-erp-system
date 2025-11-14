# Codebase Indexes

**Purpose:** Quick reference indexes for navigating the TSH ERP codebase
**Last Updated:** 2025-11-14

These indexes provide quick lookup for common code locations without needing to search the entire codebase.

## Available Indexes

### api-endpoints.json
List of all API endpoints with:
- Path
- HTTP method
- Purpose
- Required authentication
- RBAC roles

### models.json
Database models (SQLAlchemy) with:
- Table name
- Primary fields
- Relationships
- Indexes

### services.json
Business logic services with:
- Service name
- Purpose
- Key methods
- Dependencies

### scripts.json
Utility scripts (82 total) with:
- Script name
- Purpose
- Usage instructions

## Usage

```python
# Load index
import json
with open('.claude/indexes/api-endpoints.json') as f:
    endpoints = json.load(f)

# Find specific endpoint
orders_endpoint = [e for e in endpoints if 'orders' in e['path']]
```

## Maintenance

These indexes should be updated when:
- New API endpoints added
- New database models created
- New services implemented
- New scripts added

**Auto-generation scripts coming soon**
