"""
Zoho API Configuration Management
إدارة إعدادات Zoho API

Secure configuration management for Zoho API credentials
"""

import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from cryptography.fernet import Fernet
import json
import base64

class ZohoCredentials(BaseModel):
    """Zoho API credentials"""
    organization_id: str = Field(..., description="Zoho Organization ID")
    access_token: str = Field(..., description="Access Token")
    refresh_token: str = Field(..., description="Refresh Token")
    client_id: str = Field(..., description="Client ID")
    client_secret: str = Field(..., description="Client Secret")
    books_api_base: str = Field(default="https://books.zoho.com/api/v3", description="Books API Base URL")
    inventory_api_base: str = Field(default="https://inventory.zoho.com/api/v1", description="Inventory API Base URL")
    
class ZohoConfigManager:
    """Zoho configuration manager with encryption support"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.fernet = Fernet(self.encryption_key)
        self.config_file = "zoho_config.enc"
        
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = ".zoho_key"
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def save_credentials(self, credentials: ZohoCredentials) -> bool:
        """Save encrypted credentials to file"""
        try:
            # Convert to JSON
            credentials_json = credentials.model_dump_json()
            
            # Encrypt and save
            encrypted_data = self.fernet.encrypt(credentials_json.encode())
            
            with open(self.config_file, 'wb') as f:
                f.write(encrypted_data)
            
            return True
            
        except Exception as e:
            print(f"Error saving credentials: {e}")
            return False
    
    def load_credentials(self) -> Optional[ZohoCredentials]:
        """Load and decrypt credentials from file"""
        try:
            if not os.path.exists(self.config_file):
                return None
                
            with open(self.config_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt
            decrypted_data = self.fernet.decrypt(encrypted_data)
            credentials_dict = json.loads(decrypted_data.decode())
            
            return ZohoCredentials(**credentials_dict)
            
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return None
    
    def get_credentials(self) -> Optional[ZohoCredentials]:
        """Get credentials (from file or environment variables)"""
        # Try loading from encrypted file first
        credentials = self.load_credentials()
        if credentials:
            return credentials
        
        # Fallback to environment variables
        try:
            return ZohoCredentials(
                organization_id=os.getenv("ZOHO_ORGANIZATION_ID", ""),
                access_token=os.getenv("ZOHO_ACCESS_TOKEN", ""),
                refresh_token=os.getenv("ZOHO_REFRESH_TOKEN", ""),
                client_id=os.getenv("ZOHO_CLIENT_ID", ""),
                client_secret=os.getenv("ZOHO_CLIENT_SECRET", "")
            )
        except Exception:
            return None
    
    def delete_credentials(self) -> bool:
        """Delete saved credentials"""
        try:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
            return True
        except Exception as e:
            print(f"Error deleting credentials: {e}")
            return False
    
    def test_credentials(self, credentials: ZohoCredentials) -> Dict[str, Any]:
        """Test Zoho API credentials"""
        import asyncio
        from ..services.zoho_service import ZohoAsyncService
        from ..schemas.migration import ZohoConfigCreate
        
        try:
            # Convert to config format
            config = ZohoConfigCreate(
                organization_id=credentials.organization_id,
                access_token=credentials.access_token,
                refresh_token=credentials.refresh_token,
                client_id=credentials.client_id,
                client_secret=credentials.client_secret,
                books_api_base=credentials.books_api_base,
                inventory_api_base=credentials.inventory_api_base
            )
            
            # Test connection
            async def test_connection():
                async with ZohoAsyncService(config) as service:
                    return await service.test_connection()
            
            return asyncio.run(test_connection())
            
        except Exception as e:
            return {
                "error": str(e),
                "books_api": False,
                "inventory_api": False
            }

# Global config manager instance
zoho_config_manager = ZohoConfigManager()
