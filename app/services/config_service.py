"""
Secure Configuration Service for TSH ERP System
خدمة الإعدادات الآمنة لنظام TSH ERP

Manages secure storage and retrieval of API credentials and configuration.
"""

import os
import json
import base64
from cryptography.fernet import Fernet
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ZohoCredentials:
    """Zoho API credentials"""
    organization_id: str
    access_token: str
    refresh_token: str
    client_id: str
    client_secret: str
    books_api_base: str = "https://www.zohoapis.com/books/v3"
    inventory_api_base: str = "https://www.zohoapis.com/inventory/v1"


class SecureConfigService:
    """خدمة الإعدادات الآمنة"""
    
    def __init__(self):
        self.config_dir = os.path.join(os.getcwd(), ".config")
        self.credentials_file = os.path.join(self.config_dir, "zoho_credentials.enc")
        self.key_file = os.path.join(self.config_dir, "encryption.key")
        self._ensure_config_dir()
        self._encryption_key = self._get_or_create_key()
    
    def _ensure_config_dir(self):
        """إنشاء مجلد الإعدادات إذا لم يكن موجوداً"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            logger.info(f"Created config directory: {self.config_dir}")
    
    def _get_or_create_key(self) -> bytes:
        """الحصول على مفتاح التشفير أو إنشاؤه"""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            logger.info("Generated new encryption key")
            return key
    
    def _encrypt_data(self, data: str) -> bytes:
        """تشفير البيانات"""
        f = Fernet(self._encryption_key)
        return f.encrypt(data.encode())
    
    def _decrypt_data(self, encrypted_data: bytes) -> str:
        """فك تشفير البيانات"""
        f = Fernet(self._encryption_key)
        return f.decrypt(encrypted_data).decode()
    
    def save_zoho_credentials(self, credentials: ZohoCredentials) -> bool:
        """حفظ بيانات اعتماد Zoho بشكل آمن"""
        try:
            # تحويل البيانات إلى JSON
            credentials_dict = asdict(credentials)
            credentials_json = json.dumps(credentials_dict)
            
            # تشفير البيانات
            encrypted_data = self._encrypt_data(credentials_json)
            
            # حفظ البيانات المشفرة
            with open(self.credentials_file, 'wb') as f:
                f.write(encrypted_data)
            
            logger.info("Zoho credentials saved securely")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save Zoho credentials: {str(e)}")
            return False
    
    def load_zoho_credentials(self) -> Optional[ZohoCredentials]:
        """تحميل بيانات اعتماد Zoho"""
        try:
            if not os.path.exists(self.credentials_file):
                logger.warning("Zoho credentials file not found")
                return None
            
            # قراءة البيانات المشفرة
            with open(self.credentials_file, 'rb') as f:
                encrypted_data = f.read()
            
            # فك التشفير
            credentials_json = self._decrypt_data(encrypted_data)
            credentials_dict = json.loads(credentials_json)
            
            # تحويل إلى كائن ZohoCredentials
            return ZohoCredentials(**credentials_dict)
            
        except Exception as e:
            logger.error(f"Failed to load Zoho credentials: {str(e)}")
            return None
    
    def delete_zoho_credentials(self) -> bool:
        """حذف بيانات اعتماد Zoho"""
        try:
            if os.path.exists(self.credentials_file):
                os.remove(self.credentials_file)
                logger.info("Zoho credentials deleted")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete Zoho credentials: {str(e)}")
            return False
    
    def test_credentials(self, credentials: ZohoCredentials) -> Dict[str, Any]:
        """اختبار صحة بيانات الاعتماد"""
        import requests
        
        test_results = {
            "books_api": False,
            "inventory_api": False,
            "organization_valid": False,
            "token_valid": False,
            "error_messages": []
        }
        
        headers = {
            'Authorization': f'Zoho-oauthtoken {credentials.access_token}',
            'Content-Type': 'application/json'
        }
        
        # اختبار Books API
        try:
            books_url = f"{credentials.books_api_base}/organizations"
            books_response = requests.get(books_url, headers=headers, timeout=10)
            
            if books_response.status_code == 200:
                test_results["books_api"] = True
                test_results["token_valid"] = True
                
                # التحقق من المؤسسة
                orgs_data = books_response.json()
                if orgs_data.get('organizations'):
                    org_ids = [org.get('organization_id') for org in orgs_data['organizations']]
                    if credentials.organization_id in org_ids:
                        test_results["organization_valid"] = True
                    else:
                        test_results["error_messages"].append(f"Organization ID {credentials.organization_id} not found")
            else:
                test_results["error_messages"].append(f"Books API failed: {books_response.status_code}")
                
        except Exception as e:
            test_results["error_messages"].append(f"Books API error: {str(e)}")
        
        # اختبار Inventory API
        try:
            inventory_url = f"{credentials.inventory_api_base}/items"
            inventory_params = {
                'organization_id': credentials.organization_id,
                'per_page': 1
            }
            inventory_response = requests.get(
                inventory_url, 
                headers=headers, 
                params=inventory_params, 
                timeout=10
            )
            
            if inventory_response.status_code == 200:
                test_results["inventory_api"] = True
            else:
                test_results["error_messages"].append(f"Inventory API failed: {inventory_response.status_code}")
                
        except Exception as e:
            test_results["error_messages"].append(f"Inventory API error: {str(e)}")
        
        return test_results
    
    def has_zoho_config(self) -> bool:
        """Check if Zoho configuration exists"""
        return os.path.exists(self.credentials_file)
    
    def get_zoho_config(self) -> Optional[Dict[str, str]]:
        """Get Zoho configuration as dictionary"""
        credentials = self.load_zoho_credentials()
        if credentials:
            return asdict(credentials)
        return None
    
    def save_zoho_config(self, config_dict: Dict[str, str]) -> bool:
        """Save Zoho configuration from dictionary"""
        try:
            credentials = ZohoCredentials(**config_dict)
            return self.save_zoho_credentials(credentials)
        except Exception as e:
            logger.error(f"Failed to save config from dict: {str(e)}")
            return False
    
    def delete_zoho_config(self) -> bool:
        """Delete Zoho configuration (alias for delete_zoho_credentials)"""
        return self.delete_zoho_credentials()
    
    def get_zoho_credentials(self) -> Optional[ZohoCredentials]:
        """Get ZohoCredentials object (alias for load_zoho_credentials)"""
        return self.load_zoho_credentials()
    
    def test_connection(self, credentials: Optional[ZohoCredentials] = None) -> Dict[str, Any]:
        """Test Zoho connection"""
        if credentials is None:
            credentials = self.load_zoho_credentials()
            if not credentials:
                return {"error": "No credentials found"}
        
        return self.test_credentials(credentials)


def get_default_zoho_credentials() -> ZohoCredentials:
    """الحصول على بيانات اعتماد Zoho الافتراضية"""
    return ZohoCredentials(
        organization_id="748369814",
        access_token="1000.59eafd02beb2e1cbd4cdf87c747b0601.768d90dbc626ded7a0b3b8b57207121b",
        refresh_token="1000.985755ded2b2f6895cd79646156b5645.6615420a2d485e15134c8f34d6850d6c",
        client_id="1000.N0JZMZLGJXYCNEU5EU0EHT6R8CVAXO",
        client_secret="1e30344528e278bb63036d53c8990e63340e9c83dd",
        books_api_base="https://www.zohoapis.com/books/v3",
        inventory_api_base="https://www.zohoapis.com/inventory/v1"
    )


# إنشاء مثيل عام للخدمة
config_service = SecureConfigService()

# حفظ بيانات الاعتماد الافتراضية عند التشغيل لأول مرة
if not config_service.load_zoho_credentials():
    default_creds = get_default_zoho_credentials()
    config_service.save_zoho_credentials(default_creds)
    logger.info("Default Zoho credentials saved")
