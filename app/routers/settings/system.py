"""
System Settings Router
=====================

System information and translation management endpoints.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict
import json
import os

from app.schemas.settings.system import TranslationUpdate

router = APIRouter(prefix="/system", tags=["System Settings"])

# Translation JSON file path
TRANSLATIONS_JSON_PATH = "frontend/src/lib/translations.json"

# Default translations to ensure the system always works
DEFAULT_TRANSLATIONS = {
    "en": {
        "dashboard": "Dashboard",
        "sales": "Sales",
        "customers": "Customers",
        "allies": "Allies",
        "allEmployees": "All Employees",
        "travelSalespersons": "Travel Salespersons",
        "partnerSalesmen": "Partner Salesmen",
        "retailermen": "Retailermen",
        "settings": "Settings",
        "translationManagement": "Translation Management",
        "save": "Save",
        "reset": "Reset",
        "search": "Search",
        "translationsSaved": "Translations saved successfully",
        "translationsReset": "Translations reset successfully"
    },
    "ar": {
        "dashboard": "لوحة التحكم",
        "sales": "المبيعات",
        "customers": "العملاء",
        "allies": "الحلفاء",
        "allEmployees": "جميع الموظفين",
        "travelSalespersons": "مندوبي السفر",
        "partnerSalesmen": "مندوبي الشركاء",
        "retailermen": "مندوبي التجزئة",
        "settings": "الإعدادات",
        "translationManagement": "إدارة الترجمات",
        "save": "حفظ",
        "reset": "إعادة تعيين",
        "search": "بحث",
        "translationsSaved": "تم حفظ الترجمات بنجاح",
        "translationsReset": "تم إعادة تعيين الترجمات بنجاح"
    }
}


def ensure_translations_file() -> Dict[str, Dict[str, str]]:
    """Ensure the translations JSON file exists with default values"""
    if not os.path.exists(TRANSLATIONS_JSON_PATH):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(TRANSLATIONS_JSON_PATH), exist_ok=True)

        # Use default translations
        with open(TRANSLATIONS_JSON_PATH, 'w', encoding='utf-8') as file:
            json.dump(DEFAULT_TRANSLATIONS, file, ensure_ascii=False, indent=2)
        return DEFAULT_TRANSLATIONS

    # Load existing translations
    try:
        with open(TRANSLATIONS_JSON_PATH, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading translations: {e}")
        return DEFAULT_TRANSLATIONS


def save_translations(translations: Dict[str, Dict[str, str]]) -> bool:
    """Save translations to JSON file"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(TRANSLATIONS_JSON_PATH), exist_ok=True)

        with open(TRANSLATIONS_JSON_PATH, 'w', encoding='utf-8') as file:
            json.dump(translations, file, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving translations: {e}")
        return False


@router.get("/info")
async def get_system_info():
    """
    Get system information for settings dashboard.

    Returns system details like database connection, version, etc.
    """
    try:
        # Basic system info
        system_info = {
            "app_name": "TSH ERP",
            "version": "1.0.0",
            "status": "healthy",
            "environment": "production"
        }

        # Try to get database info
        try:
            from app.db.database import engine
            from sqlalchemy import text

            with engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                db_version = result.fetchone()[0]
                system_info["database"] = {
                    "connected": True,
                    "version": db_version
                }
        except Exception as e:
            system_info["database"] = {
                "connected": False,
                "error": str(e)
            }

        return system_info

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system info: {str(e)}")


@router.get("/translations")
async def get_translations():
    """
    Get current translations for all languages.

    Returns translations JSON with all language keys.
    """
    try:
        translations = ensure_translations_file()
        return {
            "translations": translations,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading translations: {str(e)}")


@router.post("/translations")
async def update_translations(translation_update: TranslationUpdate):
    """
    Update translations for one or more languages.

    Merges provided translations with existing ones.
    """
    try:
        # Load current translations
        current_translations = ensure_translations_file()

        # Update with new values
        for language, updates in translation_update.translations.items():
            if language not in current_translations:
                current_translations[language] = {}

            for key, value in updates.items():
                current_translations[language][key] = value

        # Save updated translations
        if save_translations(current_translations):
            return {
                "message": "Translations updated successfully",
                "status": "success",
                "updated_keys": list(translation_update.translations.keys())
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save translations")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating translations: {str(e)}")


@router.post("/translations/reset")
async def reset_translations():
    """
    Reset translations to default values.

    Overwrites current translations with system defaults.
    """
    try:
        if save_translations(DEFAULT_TRANSLATIONS):
            return {
                "message": "Translations reset to default values",
                "status": "success"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to reset translations")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting translations: {str(e)}")


@router.get("/translations/refresh")
async def refresh_translations():
    """
    Force refresh translations from file.

    Reloads translations from disk, useful after manual edits.
    """
    try:
        translations = ensure_translations_file()
        return {
            "translations": translations,
            "status": "success",
            "message": "Translations refreshed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing translations: {str(e)}")
