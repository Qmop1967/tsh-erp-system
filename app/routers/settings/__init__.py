"""
Settings Module
===============

Modular settings router split into logical components:
- System settings (system info, translations) - IMPLEMENTED
- Backup/Restore operations - TODO: Extract from main settings.py
- Zoho integration settings - TODO: Extract from main settings.py

This module demonstrates the modular approach. Currently imports system settings
and re-exports the main settings router for backward compatibility.

Full migration will happen in phases to avoid breaking changes.
"""

from fastapi import APIRouter

# Import system settings router (completed)
from .system import router as system_router

# Create combined settings router
router = APIRouter(prefix="/settings", tags=["Settings"])

# Include modular sub-routers
router.include_router(system_router)

# TODO Phase 2: Add backup router
# from .backup import router as backup_router
# router.include_router(backup_router)

# TODO Phase 3: Add zoho integration router
# from .zoho_integration import router as zoho_router
# router.include_router(zoho_router)

__all__ = ["router"]
