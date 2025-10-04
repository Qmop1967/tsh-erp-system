"""
Zoho to TSH ERP Sync Service
Handles synchronization with duplicate prevention and image syncing
"""

import json
import os
import hashlib
import requests
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import shutil

class ZohoSyncService:
    """Service to handle Zoho to TSH ERP synchronization"""
    
    def __init__(self):
        # Base dir is the project root (two levels up from services/)
        self.base_dir = Path(__file__).parent.parent.parent
        self.app_dir = self.base_dir / "app"
        self.data_dir = self.app_dir / "data"
        self.images_dir = self.data_dir / "images"
        self.sync_log_file = self.data_dir / "settings" / "zoho_sync_logs.json"
        
        # Create directories if they don't exist
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        self.mappings = self._load_mappings()
        self.control = self._load_control()
        
    def _load_config(self) -> Dict:
        """Load Zoho configuration"""
        config_file = self.app_dir / "data" / "settings" / "zoho_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_mappings(self) -> Dict:
        """Load sync mappings"""
        mappings_file = self.app_dir / "data" / "settings" / "zoho_sync_mappings.json"
        if mappings_file.exists():
            with open(mappings_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_control(self) -> Dict:
        """Load sync control settings"""
        control_file = self.app_dir / "data" / "settings" / "zoho_sync_control.json"
        if control_file.exists():
            with open(control_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_zoho_data(self, entity_type: str) -> List[Dict]:
        """Load Zoho data from JSON files"""
        file_map = {
            "item": "all_zoho_inventory_items.json",
            "customer": "all_zoho_customers.json",
            "vendor": "all_zoho_vendors.json"
        }
        
        file_path = self.base_dir / file_map.get(entity_type, "")
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _generate_unique_id(self, record: Dict, entity_type: str) -> str:
        """Generate unique identifier for duplicate detection"""
        # Use Zoho ID if available - try multiple field name variations
        id_fields = {
            "item": ["item_id", "zoho_item_id", "sku", "code", "name_en", "name"],
            "customer": ["contact_id", "zoho_contact_id", "email", "phone", "name_en", "name"],
            "vendor": ["vendor_id", "zoho_vendor_id", "email", "name_en", "name"]
        }
        
        fields = id_fields.get(entity_type, ["name"])
        values = []
        
        for field in fields:
            if field in record and record[field]:
                values.append(str(record[field]).lower().strip())
                # Only use first available identifier
                break
        
        # If no ID found, try name fields
        if not values:
            name_fields = ["name_en", "name_ar", "name"]
            for field in name_fields:
                if field in record and record[field]:
                    values.append(str(record[field]).lower().strip())
                    break
        
        # Create hash from values
        unique_string = "|".join(values) if values else f"unknown_{datetime.now().timestamp()}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def _load_existing_records(self, entity_type: str) -> Dict[str, Dict]:
        """Load existing TSH records to check for duplicates"""
        existing_file = self.app_dir / "data" / f"tsh_{entity_type}_records.json"
        
        if existing_file.exists():
            with open(existing_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
                # Create index by unique_id
                return {self._generate_unique_id(r, entity_type): r for r in records}
        return {}
    
    def _save_tsh_records(self, entity_type: str, records: List[Dict]):
        """Save records to TSH database file"""
        existing_file = self.app_dir / "data" / f"tsh_{entity_type}_records.json"
        
        # Create directory if it doesn't exist
        existing_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(existing_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    
    def _download_image(self, image_url: str, entity_type: str, entity_id: str) -> Optional[str]:
        """Download and save image from URL"""
        if not image_url or not image_url.startswith('http'):
            return None
        
        try:
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                # Get file extension from URL or content-type
                ext = image_url.split('.')[-1].split('?')[0]
                if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                    ext = 'jpg'
                
                # Create entity-specific directory
                entity_dir = self.images_dir / entity_type
                entity_dir.mkdir(exist_ok=True)
                
                # Save image
                filename = f"{entity_id}.{ext}"
                filepath = entity_dir / filename
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                return f"images/{entity_type}/{filename}"
            
        except Exception as e:
            print(f"Error downloading image: {str(e)}")
        
        return None
    
    def _map_fields(self, zoho_record: Dict, entity_type: str) -> Dict:
        """Map Zoho fields to TSH fields based on mapping configuration"""
        mapping = self.mappings.get(entity_type, {})
        field_mappings = mapping.get('field_mappings', [])
        
        tsh_record = {}
        
        # Use direct field mapping for items (always)
        if entity_type == "item":
            # Direct mapping for items
            tsh_record = {
                "zoho_item_id": zoho_record.get("zoho_item_id"),
                "code": zoho_record.get("code"),
                "name": zoho_record.get("name_en") or zoho_record.get("name"),
                "name_ar": zoho_record.get("name_ar"),
                "description": zoho_record.get("description_en") or zoho_record.get("description"),
                "description_ar": zoho_record.get("description_ar"),
                "brand": zoho_record.get("brand"),
                "model": zoho_record.get("model"),
                "unit": zoho_record.get("unit_of_measure"),
                "cost_price": float(zoho_record.get("cost_price_usd", 0) or 0),
                "selling_price": float(zoho_record.get("selling_price_usd", 0) or 0),
                "track_inventory": zoho_record.get("track_inventory", True),
                "reorder_level": float(zoho_record.get("reorder_level", 0) or 0),
                "is_active": zoho_record.get("is_active", True),
                "specifications": zoho_record.get("specifications", {})
            }
            return tsh_record
        
        for field_map in field_mappings:
            zoho_field = field_map['zoho_field']
            tsh_field = field_map['tsh_field']
            transformation = field_map.get('transformation_rule')
            
            # Get value from Zoho record
            value = zoho_record.get(zoho_field)
            
            # Apply transformation if specified
            if value and transformation:
                if transformation == 'lowercase':
                    value = str(value).lower()
                elif transformation == 'uppercase':
                    value = str(value).upper()
                elif transformation == 'trim':
                    value = str(value).strip()
            
            # Set TSH field
            tsh_record[tsh_field] = value
        
        return tsh_record
    
    def _log_sync_operation(self, sync_id: str, entity_type: str, operation: str, 
                           status: str, records_processed: int, errors: List[str] = None):
        """Log sync operation to file"""
        log_entry = {
            "sync_id": sync_id,
            "entity_type": entity_type,
            "operation": operation,
            "status": status,
            "records_processed": records_processed,
            "errors": errors or [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Load existing logs
        logs = []
        if self.sync_log_file.exists():
            with open(self.sync_log_file, 'r') as f:
                data = json.load(f)
                # Handle both list and dict formats
                if isinstance(data, list):
                    logs = data
                elif isinstance(data, dict):
                    logs = data.get('logs', [])
                else:
                    logs = []
        
        # Add new log
        logs.insert(0, log_entry)
        
        # Keep only last 1000 logs
        logs = logs[:1000]
        
        # Save logs
        with open(self.sync_log_file, 'w') as f:
            json.dump({"logs": logs}, f, indent=2)
    
    def sync_items(self, sync_images: bool = True) -> Dict:
        """
        Sync items from Zoho to TSH with duplicate prevention
        
        Args:
            sync_images: Whether to download and sync images
            
        Returns:
            Dict with sync statistics
        """
        sync_id = f"sync_items_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        entity_type = "item"
        
        print(f"🔄 Starting item sync (ID: {sync_id})")
        print(f"📷 Image sync: {'Enabled' if sync_images else 'Disabled'}")
        
        try:
            # Load Zoho data
            zoho_items = self._load_zoho_data(entity_type)
            print(f"📦 Loaded {len(zoho_items)} items from Zoho")
            
            # Load existing TSH records
            existing_records = self._load_existing_records(entity_type)
            print(f"💾 Found {len(existing_records)} existing items in TSH")
            
            # Check if sync is enabled
            mapping = self.mappings.get(entity_type, {})
            if not mapping.get('enabled', False):
                return {
                    "status": "skipped",
                    "message": "Item sync is not enabled",
                    "sync_id": sync_id
                }
            
            # Statistics
            stats = {
                "total": len(zoho_items),
                "new": 0,
                "updated": 0,
                "skipped": 0,
                "errors": 0,
                "images_downloaded": 0
            }
            
            errors = []
            all_records = []
            max_images_to_download = 20  # Limit to 20 images per sync
            
            # Process each Zoho item
            for idx, zoho_item in enumerate(zoho_items, 1):
                try:
                    # Generate unique ID
                    unique_id = self._generate_unique_id(zoho_item, entity_type)
                    
                    # Check if already exists
                    existing = existing_records.get(unique_id)
                    
                    # Map fields
                    tsh_item = self._map_fields(zoho_item, entity_type)
                    tsh_item['unique_id'] = unique_id
                    tsh_item['zoho_sync_date'] = datetime.now().isoformat()
                    tsh_item['sync_source'] = 'zoho'
                    
                    # Download images if enabled (limit to 20 per sync)
                    if sync_images and stats['images_downloaded'] < max_images_to_download:
                        image_url = zoho_item.get('image_url') or zoho_item.get('image')
                        if image_url:
                            # Only download if not already downloaded
                            if not existing or not existing.get('image_path'):
                                item_id = zoho_item.get('zoho_item_id') or zoho_item.get('item_id', unique_id)
                                image_path = self._download_image(image_url, entity_type, item_id)
                                if image_path:
                                    tsh_item['image_path'] = image_path
                                    stats['images_downloaded'] += 1
                                    print(f"  📷 Downloaded image {stats['images_downloaded']}/{max_images_to_download}: {zoho_item.get('name_en', '')[:40]}")
                            else:
                                # Keep existing image path
                                tsh_item['image_path'] = existing.get('image_path')
                    
                    if existing:
                        # Update existing record
                        tsh_item['id'] = existing.get('id')
                        tsh_item['created_at'] = existing.get('created_at')
                        tsh_item['updated_at'] = datetime.now().isoformat()
                        stats['updated'] += 1
                    else:
                        # New record
                        tsh_item['id'] = len(all_records) + 1
                        tsh_item['created_at'] = datetime.now().isoformat()
                        tsh_item['updated_at'] = datetime.now().isoformat()
                        stats['new'] += 1
                    
                    all_records.append(tsh_item)
                    
                    # Progress indicator
                    if idx % 100 == 0:
                        print(f"  ⏳ Processed {idx}/{len(zoho_items)} items...")
                    
                except Exception as e:
                    error_msg = f"Error processing item {idx}: {str(e)}"
                    errors.append(error_msg)
                    stats['errors'] += 1
                    print(f"  ❌ {error_msg}")
            
            # Save all records to TSH
            self._save_tsh_records(entity_type, all_records)
            print(f"💾 Saved {len(all_records)} items to TSH database")
            
            # Log operation
            self._log_sync_operation(
                sync_id, entity_type, "sync", 
                "success" if stats['errors'] == 0 else "completed_with_errors",
                len(all_records), errors
            )
            
            print(f"\n✅ Sync completed!")
            print(f"   📊 Statistics:")
            print(f"      - Total: {stats['total']}")
            print(f"      - New: {stats['new']}")
            print(f"      - Updated: {stats['updated']}")
            print(f"      - Images: {stats['images_downloaded']}")
            print(f"      - Errors: {stats['errors']}")
            
            return {
                "status": "success",
                "sync_id": sync_id,
                "statistics": stats,
                "errors": errors
            }
            
        except Exception as e:
            error_msg = f"Fatal error during sync: {str(e)}"
            print(f"❌ {error_msg}")
            
            self._log_sync_operation(
                sync_id, entity_type, "sync", "failed", 0, [error_msg]
            )
            
            return {
                "status": "failed",
                "sync_id": sync_id,
                "error": error_msg
            }
    
    def sync_customers(self) -> Dict:
        """Sync customers from Zoho to TSH with duplicate prevention"""
        sync_id = f"sync_customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        entity_type = "customer"
        
        print(f"🔄 Starting customer sync (ID: {sync_id})")
        
        try:
            # Load Zoho data
            zoho_customers = self._load_zoho_data(entity_type)
            print(f"👥 Loaded {len(zoho_customers)} customers from Zoho")
            
            # Load existing TSH records
            existing_records = self._load_existing_records(entity_type)
            print(f"💾 Found {len(existing_records)} existing customers in TSH")
            
            # Check if sync is enabled
            mapping = self.mappings.get(entity_type, {})
            if not mapping.get('enabled', False):
                return {
                    "status": "skipped",
                    "message": "Customer sync is not enabled",
                    "sync_id": sync_id
                }
            
            # Statistics
            stats = {
                "total": len(zoho_customers),
                "new": 0,
                "updated": 0,
                "skipped": 0,
                "errors": 0
            }
            
            errors = []
            all_records = []
            
            # Process each customer
            for idx, zoho_customer in enumerate(zoho_customers, 1):
                try:
                    unique_id = self._generate_unique_id(zoho_customer, entity_type)
                    existing = existing_records.get(unique_id)
                    
                    tsh_customer = self._map_fields(zoho_customer, entity_type)
                    tsh_customer['unique_id'] = unique_id
                    tsh_customer['zoho_sync_date'] = datetime.now().isoformat()
                    tsh_customer['sync_source'] = 'zoho'
                    
                    if existing:
                        tsh_customer['id'] = existing.get('id')
                        tsh_customer['created_at'] = existing.get('created_at')
                        tsh_customer['updated_at'] = datetime.now().isoformat()
                        stats['updated'] += 1
                    else:
                        tsh_customer['id'] = len(all_records) + 1
                        tsh_customer['created_at'] = datetime.now().isoformat()
                        tsh_customer['updated_at'] = datetime.now().isoformat()
                        stats['new'] += 1
                    
                    all_records.append(tsh_customer)
                    
                    if idx % 100 == 0:
                        print(f"  ⏳ Processed {idx}/{len(zoho_customers)} customers...")
                    
                except Exception as e:
                    error_msg = f"Error processing customer {idx}: {str(e)}"
                    errors.append(error_msg)
                    stats['errors'] += 1
            
            self._save_tsh_records(entity_type, all_records)
            print(f"💾 Saved {len(all_records)} customers to TSH database")
            
            self._log_sync_operation(
                sync_id, entity_type, "sync",
                "success" if stats['errors'] == 0 else "completed_with_errors",
                len(all_records), errors
            )
            
            print(f"\n✅ Sync completed!")
            print(f"   📊 Statistics:")
            print(f"      - Total: {stats['total']}")
            print(f"      - New: {stats['new']}")
            print(f"      - Updated: {stats['updated']}")
            print(f"      - Errors: {stats['errors']}")
            
            return {
                "status": "success",
                "sync_id": sync_id,
                "statistics": stats,
                "errors": errors
            }
            
        except Exception as e:
            error_msg = f"Fatal error during sync: {str(e)}"
            print(f"❌ {error_msg}")
            
            self._log_sync_operation(
                sync_id, entity_type, "sync", "failed", 0, [error_msg]
            )
            
            return {
                "status": "failed",
                "sync_id": sync_id,
                "error": error_msg
            }
    
    def sync_vendors(self) -> Dict:
        """Sync vendors from Zoho to TSH with duplicate prevention"""
        sync_id = f"sync_vendors_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        entity_type = "vendor"
        
        print(f"🔄 Starting vendor sync (ID: {sync_id})")
        
        try:
            zoho_vendors = self._load_zoho_data(entity_type)
            print(f"🏭 Loaded {len(zoho_vendors)} vendors from Zoho")
            
            existing_records = self._load_existing_records(entity_type)
            print(f"💾 Found {len(existing_records)} existing vendors in TSH")
            
            mapping = self.mappings.get(entity_type, {})
            if not mapping.get('enabled', False):
                return {
                    "status": "skipped",
                    "message": "Vendor sync is not enabled",
                    "sync_id": sync_id
                }
            
            stats = {
                "total": len(zoho_vendors),
                "new": 0,
                "updated": 0,
                "skipped": 0,
                "errors": 0
            }
            
            errors = []
            all_records = []
            
            for idx, zoho_vendor in enumerate(zoho_vendors, 1):
                try:
                    unique_id = self._generate_unique_id(zoho_vendor, entity_type)
                    existing = existing_records.get(unique_id)
                    
                    tsh_vendor = self._map_fields(zoho_vendor, entity_type)
                    tsh_vendor['unique_id'] = unique_id
                    tsh_vendor['zoho_sync_date'] = datetime.now().isoformat()
                    tsh_vendor['sync_source'] = 'zoho'
                    
                    if existing:
                        tsh_vendor['id'] = existing.get('id')
                        tsh_vendor['created_at'] = existing.get('created_at')
                        tsh_vendor['updated_at'] = datetime.now().isoformat()
                        stats['updated'] += 1
                    else:
                        tsh_vendor['id'] = len(all_records) + 1
                        tsh_vendor['created_at'] = datetime.now().isoformat()
                        tsh_vendor['updated_at'] = datetime.now().isoformat()
                        stats['new'] += 1
                    
                    all_records.append(tsh_vendor)
                    
                except Exception as e:
                    error_msg = f"Error processing vendor {idx}: {str(e)}"
                    errors.append(error_msg)
                    stats['errors'] += 1
            
            self._save_tsh_records(entity_type, all_records)
            print(f"💾 Saved {len(all_records)} vendors to TSH database")
            
            self._log_sync_operation(
                sync_id, entity_type, "sync",
                "success" if stats['errors'] == 0 else "completed_with_errors",
                len(all_records), errors
            )
            
            print(f"\n✅ Sync completed!")
            print(f"   📊 Statistics:")
            print(f"      - Total: {stats['total']}")
            print(f"      - New: {stats['new']}")
            print(f"      - Updated: {stats['updated']}")
            print(f"      - Errors: {stats['errors']}")
            
            return {
                "status": "success",
                "sync_id": sync_id,
                "statistics": stats,
                "errors": errors
            }
            
        except Exception as e:
            error_msg = f"Fatal error during sync: {str(e)}"
            print(f"❌ {error_msg}")
            
            self._log_sync_operation(
                sync_id, entity_type, "sync", "failed", 0, [error_msg]
            )
            
            return {
                "status": "failed",
                "sync_id": sync_id,
                "error": error_msg
            }
