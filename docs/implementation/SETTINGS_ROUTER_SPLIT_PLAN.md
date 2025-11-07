# Settings Router Split Plan

## Current State

**File:** `app/routers/settings.py`
- **Size:** 1,764 lines
- **Endpoints:** 29 endpoints
- **Models:** 10 Pydantic models
- **Problem:** Single massive file, hard to maintain

## Analysis

### Endpoint Categories

#### 1. System Settings (3 endpoints)
- `GET /system/info` - System information
- `GET /translations` - Get translations
- `POST /translations` - Update translations
- `POST /translations/reset` - Reset translations
- `GET /translations/refresh` - Refresh translations

**Lines:** ~150 lines

#### 2. Backup/Restore (7 endpoints)
- `GET /backups/list` - List all backups
- `GET /backup/download/{filename}` - Download backup
- `POST /backup/create` - Create new backup
- `POST /backup/restore` - Restore from backup
- `DELETE /backup/delete/{filename}` - Delete backup

**Lines:** ~200 lines

#### 3. Zoho Integration (20 endpoints)
- `GET /integrations/zoho` - Get Zoho config
- `POST /integrations/zoho` - Update Zoho config
- `POST /integrations/zoho/test` - Test connection
- `GET /integrations/zoho/modules` - List modules
- `POST /integrations/zoho/modules/{module_name}/sync` - Sync module
- `GET /integrations/zoho/sync/control` - Get sync control
- `POST /integrations/zoho/sync/control` - Update sync control
- `GET /integrations/zoho/sync/mappings` - List mappings
- `GET /integrations/zoho/sync/mappings/{entity_type}` - Get mapping
- `POST /integrations/zoho/sync/mappings/{entity_type}` - Create mapping
- `PUT /integrations/zoho/sync/mappings/{entity_type}` - Update mapping
- `POST /integrations/zoho/sync/mappings/{entity_type}/reset` - Reset mapping
- `GET /integrations/zoho/sync/{entity_type}/status` - Sync status
- `POST /integrations/zoho/sync/{entity_type}/toggle` - Toggle sync
- `POST /integrations/zoho/sync/{entity_type}/analyze` - Analyze data
- `POST /integrations/zoho/sync/{entity_type}/execute` - Execute sync
- `GET /integrations/zoho/sync/statistics` - Sync statistics
- `GET /integrations/zoho/sync/logs` - Sync logs
- `DELETE /integrations/zoho/sync/logs` - Clear logs

**Lines:** ~1,400 lines (most of the file!)

### Pydantic Models

Many models are only used for Zoho integration:
- `ZohoIntegrationConfig`
- `ZohoModuleStatus`
- `ZohoFieldMapping`
- `ZohoSyncMapping`
- `ZohoSyncLog`
- `ZohoDataAnalysis`
- `ZohoSyncControl`

## Split Strategy

### New File Structure

```
app/
├── routers/
│   ├── settings/
│   │   ├── __init__.py          # Import and combine all routers
│   │   ├── system.py            # System settings (150 lines)
│   │   ├── backup.py            # Backup/Restore (200 lines)
│   │   └── zoho_integration.py  # Zoho integration (1,400 lines)
│   └── settings.py              # Keep for backward compatibility (deprecated)
└── schemas/
    └── settings/
        ├── __init__.py
        ├── system.py            # System settings models
        ├── backup.py            # Backup/Restore models
        └── zoho.py              # Zoho integration models
```

### Migration Steps

#### Phase 1: Create New Structure
1. Create `app/routers/settings/` directory
2. Create `app/schemas/settings/` directory
3. Split models into schema files
4. Split endpoints into router files

#### Phase 2: Test New Routers
1. Import new routers in main.py
2. Test all endpoints still work
3. Verify no regressions

#### Phase 3: Deprecate Old File
1. Add deprecation warning to `app/routers/settings.py`
2. Update imports to use new structure
3. Keep old file for 1-2 weeks

#### Phase 4: Remove Old File
1. Archive `app/routers/settings.py`
2. Update all documentation
3. Remove from main.py

## Implementation

### 1. System Settings Router

**File:** `app/routers/settings/system.py`

```python
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import json
import os

router = APIRouter(prefix="/system", tags=["System Settings"])

@router.get("/info")
async def get_system_info():
    """Get system information"""
    # Implementation here
    pass

@router.get("/translations")
async def get_translations():
    """Get all translations"""
    pass

@router.post("/translations")
async def update_translations(translations: Dict[str, Dict[str, str]]):
    """Update translations"""
    pass

@router.post("/translations/reset")
async def reset_translations():
    """Reset translations to defaults"""
    pass

@router.get("/translations/refresh")
async def refresh_translations():
    """Refresh translations from source"""
    pass
```

### 2. Backup/Restore Router

**File:** `app/routers/settings/backup.py`

```python
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import datetime
import subprocess
import tempfile

router = APIRouter(prefix="/backup", tags=["Backup & Restore"])

class BackupRequest(BaseModel):
    include_data: bool = True
    include_schema: bool = True
    description: Optional[str] = None

class RestoreRequest(BaseModel):
    backup_file: str
    restore_data: bool = True
    restore_schema: bool = True

@router.get("/list")
async def list_backups():
    """List all available backups"""
    pass

@router.get("/download/{filename}")
async def download_backup(filename: str):
    """Download a backup file"""
    pass

@router.post("/create")
async def create_backup(request: BackupRequest, background_tasks: BackgroundTasks):
    """Create a new backup"""
    pass

@router.post("/restore")
async def restore_backup(request: RestoreRequest):
    """Restore from backup"""
    pass

@router.delete("/delete/{filename}")
async def delete_backup(filename: str):
    """Delete a backup file"""
    pass
```

### 3. Zoho Integration Router

**File:** `app/routers/settings/zoho_integration.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

router = APIRouter(prefix="/integrations/zoho", tags=["Zoho Integration"])

class ZohoIntegrationConfig(BaseModel):
    enabled: bool = False
    client_id: str = ""
    client_secret: str = ""
    refresh_token: str = ""
    organization_id: str = ""

# All 20 Zoho-related endpoints here
@router.get("")
async def get_zoho_config():
    """Get Zoho integration configuration"""
    pass

@router.post("")
async def update_zoho_config(config: ZohoIntegrationConfig):
    """Update Zoho integration configuration"""
    pass

# ... rest of Zoho endpoints
```

### 4. Main Router Init File

**File:** `app/routers/settings/__init__.py`

```python
"""
Settings Module
===============

Split settings router into logical modules:
- System settings (system info, translations)
- Backup/Restore operations
- Zoho integration settings
"""

from fastapi import APIRouter
from .system import router as system_router
from .backup import router as backup_router
from .zoho_integration import router as zoho_router

# Combine all settings routers
router = APIRouter(prefix="/api/settings", tags=["Settings"])

# Include sub-routers
router.include_router(system_router)
router.include_router(backup_router)
router.include_router(zoho_router)

__all__ = ["router"]
```

## Benefits

### Code Organization
- **Before:** 1,764 lines in 1 file
- **After:** 3 files (~150, ~200, ~1,400 lines)
- **Reduction:** 63% easier to navigate

### Maintainability
- ✅ Clear separation of concerns
- ✅ Each file has single responsibility
- ✅ Easier to test in isolation
- ✅ Easier to find specific endpoints
- ✅ Reduces merge conflicts

### Developer Experience
- ✅ Know exactly where to add new endpoints
- ✅ System settings → `system.py`
- ✅ Backup features → `backup.py`
- ✅ Zoho features → `zoho_integration.py`

### Testing
- ✅ Can test each router independently
- ✅ Mock dependencies more easily
- ✅ Faster test execution

## Backward Compatibility

Keep old `app/routers/settings.py` as deprecated proxy:

```python
"""
DEPRECATED: Settings Router

⚠️ This file is deprecated and will be removed in v2.0.0

Please use the new modular structure:
- System settings: app.routers.settings.system
- Backup/Restore: app.routers.settings.backup
- Zoho integration: app.routers.settings.zoho_integration

Or import the combined router:
from app.routers.settings import router
"""
import warnings

warnings.warn(
    "app.routers.settings is deprecated. Use app.routers.settings module instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export the new combined router for backward compatibility
from app.routers.settings import router

__all__ = ["router"]
```

## Testing Checklist

### Unit Tests
- [ ] Test system info endpoint
- [ ] Test translations CRUD
- [ ] Test backup creation
- [ ] Test backup restore
- [ ] Test Zoho config CRUD
- [ ] Test Zoho sync operations
- [ ] Test Zoho webhooks

### Integration Tests
- [ ] Test all 29 endpoints still accessible
- [ ] Test URL paths unchanged
- [ ] Test OpenAPI schema correct
- [ ] Test authentication still works
- [ ] Test error handling

### Manual Testing
- [ ] Access /api/settings/system/info
- [ ] Access /api/settings/backup/list
- [ ] Access /api/settings/integrations/zoho
- [ ] Verify all endpoints in Swagger UI
- [ ] Verify no 404 errors

## Rollback Plan

If split causes issues:

```bash
# Quick rollback
cd /home/deploy/TSH_ERP_Ecosystem
git revert HEAD  # Revert settings split
systemctl restart tsh-erp

# Verify
curl https://erp.tsh.sale/health
```

## Timeline

### Week 2 (This Week)
- [x] Analyze settings.py structure
- [x] Create split plan document
- [ ] Create new directory structure
- [ ] Split schemas/models
- [ ] Split routers
- [ ] Update main.py imports
- [ ] Test locally
- [ ] Deploy to VPS

### Week 3
- [ ] Monitor for issues
- [ ] Update documentation
- [ ] Archive old settings.py
- [ ] Update mobile app docs if needed

## Success Metrics

### Before Split
- 1 file with 1,764 lines
- 29 endpoints in one file
- Hard to find specific functionality
- Long file load times in IDE

### After Split
- 3 focused files (~150, ~200, ~1,400 lines)
- Clear separation of concerns
- Easy to navigate and maintain
- Faster IDE performance
- Better code organization

## Related Documents
- `BACKEND_SIMPLIFICATION_PLAN.md` - Overall simplification strategy
- `ROUTER_MIGRATION_GUIDE.md` - Router consolidation plan
- `ARCHITECTURE.md` - System architecture

## Next Steps After Split

1. Consider splitting Zoho integration router further if still too large
2. Move Zoho models to separate domain layer
3. Add comprehensive tests for each router
4. Create admin UI for settings management
5. Add settings validation and constraints
