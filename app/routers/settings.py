from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Union, Optional, List
import json
import os
import subprocess
import datetime
import asyncio
import tempfile
import zipfile
import shutil
from pathlib import Path

router = APIRouter(tags=["settings"])

class TranslationUpdate(BaseModel):
    translations: Dict[str, Dict[str, str]]  # {language: {key: value}}

class BackupRequest(BaseModel):
    include_data: bool = True
    include_schema: bool = True
    description: Optional[str] = None

class RestoreRequest(BaseModel):
    backup_file: str
    restore_data: bool = True
    restore_schema: bool = True

# Translation JSON file paths
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

def ensure_translations_file():
    """Ensure the translations JSON file exists with default values"""
    if not os.path.exists(TRANSLATIONS_JSON_PATH):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(TRANSLATIONS_JSON_PATH), exist_ok=True)
        
        # Read current translations from TypeScript file if it exists
        ts_path = "frontend/src/lib/translations.ts"
        if os.path.exists(ts_path):
            try:
                with open(ts_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                # Parse existing translations from TypeScript file
                translations = parse_typescript_translations(content)
                if translations:
                    with open(TRANSLATIONS_JSON_PATH, 'w', encoding='utf-8') as file:
                        json.dump(translations, file, ensure_ascii=False, indent=2)
                    return translations
            except Exception as e:
                print(f"Error parsing existing translations: {e}")
        
        # Use default translations if parsing fails
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

def parse_typescript_translations(content: str) -> Optional[Dict[str, Dict[str, str]]]:
    """Parse translations from TypeScript file content"""
    import re
    
    try:
        # Extract the translations object
        translations = {"en": {}, "ar": {}}
        
        # Find the English translations section
        en_match = re.search(r'en:\s*{([^}]*(?:{[^}]*}[^}]*)*)}', content, re.DOTALL)
        if en_match:
            en_section = en_match.group(1)
            # Extract key-value pairs
            pairs = re.findall(r"(\w+):\s*['\"]([^'\"]*)['\"]", en_section)
            for key, value in pairs:
                translations["en"][key] = value
        
        # Find the Arabic translations section  
        ar_match = re.search(r'ar:\s*{([^}]*(?:{[^}]*}[^}]*)*)}', content, re.DOTALL)
        if ar_match:
            ar_section = ar_match.group(1)
            # Extract key-value pairs
            pairs = re.findall(r"(\w+):\s*['\"]([^'\"]*)['\"]", ar_section)
            for key, value in pairs:
                translations["ar"][key] = value
                
        return translations if translations["en"] or translations["ar"] else None
    except Exception as e:
        print(f"Error parsing TypeScript: {e}")
        return None

def save_translations(translations: Dict[str, Dict[str, str]]):
    """Save translations to JSON file"""
    try:
        with open(TRANSLATIONS_JSON_PATH, 'w', encoding='utf-8') as file:
            json.dump(translations, file, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving translations: {e}")
        return False

@router.get("/translations")
async def get_translations():
    """Get current translations"""
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
    """Update translations"""
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
    """Reset translations to default values"""
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
    """Force refresh translations from file"""
    try:
        translations = ensure_translations_file()
        return {
            "translations": translations,
            "status": "success",
            "message": "Translations refreshed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing translations: {str(e)}")

# ===== BACKUP AND RESTORE FUNCTIONALITY =====

# Backup directory
BACKUP_DIR = "backups"
os.makedirs(BACKUP_DIR, exist_ok=True)

def get_database_url():
    """Get database URL from environment"""
    from dotenv import load_dotenv
    load_dotenv()
    return os.getenv("DATABASE_URL", "postgresql://khaleelal-mulla:@localhost:5432/erp_db")

async def create_database_backup(backup_name: str, include_data: bool = True, include_schema: bool = True) -> str:
    """Create a database backup using pg_dump"""
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{backup_name}_{timestamp}.sql"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        # Parse database URL
        db_url = get_database_url()
        if "postgresql://" in db_url:
            # Extract database components
            url_parts = db_url.replace("postgresql://", "").split("/")
            db_name = url_parts[-1]
            host_user = url_parts[0].split("@")
            if len(host_user) == 2:
                user_pass = host_user[0].split(":")
                user = user_pass[0]
                password = user_pass[1] if len(user_pass) > 1 else ""
                host = host_user[1].split(":")[0]
                port = host_user[1].split(":")[1] if ":" in host_user[1] else "5432"
            else:
                user = "khaleelal-mulla"
                password = ""
                host = "localhost"
                port = "5432"
        else:
            raise ValueError("Unsupported database URL format")
        
        # Build pg_dump command
        cmd = ["pg_dump"]
        
        if user:
            cmd.extend(["-U", user])
        if host:
            cmd.extend(["-h", host])
        if port:
            cmd.extend(["-p", port])
        
        # Add options based on what to include
        if include_schema and include_data:
            pass  # Default behavior
        elif include_schema and not include_data:
            cmd.append("--schema-only")
        elif not include_schema and include_data:
            cmd.append("--data-only")
        else:
            raise ValueError("Must include either schema, data, or both")
        
        cmd.extend(["-f", backup_path, db_name])
        
        # Set environment for password if needed
        env = os.environ.copy()
        if password:
            env["PGPASSWORD"] = password
        
        # Execute pg_dump
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            return backup_path
        else:
            raise Exception(f"pg_dump failed: {result.stderr}")
            
    except Exception as e:
        raise Exception(f"Failed to create database backup: {str(e)}")

async def restore_database_backup(backup_path: str, restore_data: bool = True, restore_schema: bool = True) -> bool:
    """Restore database from backup using psql"""
    try:
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        # Parse database URL
        db_url = get_database_url()
        if "postgresql://" in db_url:
            url_parts = db_url.replace("postgresql://", "").split("/")
            db_name = url_parts[-1]
            host_user = url_parts[0].split("@")
            if len(host_user) == 2:
                user_pass = host_user[0].split(":")
                user = user_pass[0]
                password = user_pass[1] if len(user_pass) > 1 else ""
                host = host_user[1].split(":")[0]
                port = host_user[1].split(":")[1] if ":" in host_user[1] else "5432"
            else:
                user = "khaleelal-mulla"
                password = ""
                host = "localhost"
                port = "5432"
        else:
            raise ValueError("Unsupported database URL format")
        
        # Build psql command
        cmd = ["psql"]
        
        if user:
            cmd.extend(["-U", user])
        if host:
            cmd.extend(["-h", host])
        if port:
            cmd.extend(["-p", port])
        
        cmd.extend(["-d", db_name, "-f", backup_path])
        
        # Set environment for password if needed
        env = os.environ.copy()
        if password:
            env["PGPASSWORD"] = password
        
        # Execute psql
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True
        else:
            raise Exception(f"psql restore failed: {result.stderr}")
            
    except Exception as e:
        raise Exception(f"Failed to restore database backup: {str(e)}")

@router.post("/backup/create")
async def create_backup(backup_request: BackupRequest, background_tasks: BackgroundTasks):
    """Create a database backup"""
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"tsh_erp_backup_{timestamp}"
        
        if backup_request.description:
            # Sanitize description for filename
            safe_desc = "".join(c for c in backup_request.description if c.isalnum() or c in (' ', '-', '_')).rstrip()
            backup_name = f"tsh_erp_{safe_desc}_{timestamp}"
        
        backup_path = await create_database_backup(
            backup_name, 
            backup_request.include_data, 
            backup_request.include_schema
        )
        
        # Get file size
        file_size = os.path.getsize(backup_path)
        
        return {
            "status": "success",
            "message": "Backup created successfully",
            "backup_path": backup_path,
            "backup_name": os.path.basename(backup_path),
            "file_size": file_size,
            "created_at": datetime.datetime.now().isoformat(),
            "includes_data": backup_request.include_data,
            "includes_schema": backup_request.include_schema
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create backup: {str(e)}")

@router.get("/backups/list")
async def list_backups():
    """List all available backups"""
    try:
        backups = []
        
        if os.path.exists(BACKUP_DIR):
            for filename in os.listdir(BACKUP_DIR):
                if filename.endswith('.sql'):
                    file_path = os.path.join(BACKUP_DIR, filename)
                    file_stat = os.stat(file_path)
                    
                    backups.append({
                        "filename": filename,
                        "path": file_path,
                        "size": file_stat.st_size,
                        "created_at": datetime.datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                        "modified_at": datetime.datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                    })
        
        # Sort by creation time, newest first
        backups.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "status": "success",
            "backups": backups,
            "total_count": len(backups)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list backups: {str(e)}")

@router.post("/backup/restore")
async def restore_backup(restore_request: RestoreRequest):
    """Restore database from backup"""
    try:
        backup_path = restore_request.backup_file
        
        # If only filename provided, assume it's in the backup directory
        if not os.path.sep in backup_path:
            backup_path = os.path.join(BACKUP_DIR, backup_path)
        
        if not os.path.exists(backup_path):
            raise HTTPException(status_code=404, detail=f"Backup file not found: {backup_path}")
        
        # Perform the restore
        success = await restore_database_backup(
            backup_path,
            restore_request.restore_data,
            restore_request.restore_schema
        )
        
        if success:
            return {
                "status": "success",
                "message": "Database restored successfully",
                "backup_file": backup_path,
                "restored_at": datetime.datetime.now().isoformat(),
                "restored_data": restore_request.restore_data,
                "restored_schema": restore_request.restore_schema
            }
        else:
            raise HTTPException(status_code=500, detail="Database restore failed")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restore backup: {str(e)}")

@router.get("/backup/download/{filename}")
async def download_backup(filename: str):
    """Download a backup file"""
    try:
        backup_path = os.path.join(BACKUP_DIR, filename)
        
        if not os.path.exists(backup_path):
            raise HTTPException(status_code=404, detail="Backup file not found")
        
        return FileResponse(
            path=backup_path,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download backup: {str(e)}")

@router.delete("/backup/delete/{filename}")
async def delete_backup(filename: str):
    """Delete a backup file"""
    try:
        backup_path = os.path.join(BACKUP_DIR, filename)
        
        if not os.path.exists(backup_path):
            raise HTTPException(status_code=404, detail="Backup file not found")
        
        os.remove(backup_path)
        
        return {
            "status": "success",
            "message": f"Backup {filename} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete backup: {str(e)}")

@router.get("/system/info")
async def get_system_info():
    """Get system information for settings dashboard"""
    try:
        # Database info
        from app.db.database import engine
        from sqlalchemy import text
        
        db_info = {}
        try:
            with engine.connect() as connection:
                result = connection.execute(text('SELECT version()'))
                db_info["version"] = result.fetchone()[0]
                
                result = connection.execute(text('''
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                '''))
                db_info["table_count"] = result.fetchone()[0]
                
                result = connection.execute(text('''
                    SELECT pg_size_pretty(pg_database_size(current_database()))
                '''))
                db_info["size"] = result.fetchone()[0]
        except Exception as e:
            db_info["error"] = str(e)
        
        # Backup info
        backup_count = 0
        backup_total_size = 0
        if os.path.exists(BACKUP_DIR):
            for filename in os.listdir(BACKUP_DIR):
                if filename.endswith('.sql'):
                    backup_count += 1
                    backup_total_size += os.path.getsize(os.path.join(BACKUP_DIR, filename))
        
        return {
            "status": "success",
            "system_info": {
                "database": db_info,
                "backups": {
                    "count": backup_count,
                    "total_size": backup_total_size,
                    "backup_dir": BACKUP_DIR
                },
                "application": {
                    "name": "TSH ERP System",
                    "version": "1.0.0",
                    "last_checked": datetime.datetime.now().isoformat()
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system info: {str(e)}")