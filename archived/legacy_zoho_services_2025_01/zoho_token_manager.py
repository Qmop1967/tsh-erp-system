"""
Zoho Token Manager - Automatic Token Refresh Service
Manages Zoho OAuth tokens and automatically refreshes them before expiration
"""

import os
import time
import logging
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)


class ZohoTokenManager:
    """Manages Zoho API tokens with automatic refresh"""

    def __init__(self):
        # Load credentials from environment
        self.client_id = os.getenv("ZOHO_CLIENT_ID")
        self.client_secret = os.getenv("ZOHO_CLIENT_SECRET")
        self.refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")
        self.organization_id = os.getenv("ZOHO_ORGANIZATION_ID")

        # Token state
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._token_refresh_buffer = 300  # Refresh 5 minutes before expiration

        # API endpoints
        self.token_url = "https://accounts.zoho.com/oauth/v2/token"
        self.inventory_api_base = "https://www.zohoapis.com/inventory/v1"

        logger.info("ZohoTokenManager initialized")

    def _reload_token_from_env(self):
        """Reload access token from environment (reads updated .env file)"""
        # Force reload environment variables
        from dotenv import load_dotenv
        load_dotenv(override=True)
        return os.getenv("ZOHO_ACCESS_TOKEN")

    def _is_token_valid(self) -> bool:
        """Check if current access token is still valid"""
        if not self._access_token:
            return False

        if not self._token_expires_at:
            # If we don't know expiration, assume it might be invalid
            return False

        # Check if token will expire within buffer time
        now = datetime.now()
        buffer_time = timedelta(seconds=self._token_refresh_buffer)

        return now + buffer_time < self._token_expires_at

    async def _refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token"""
        if not self.refresh_token or not self.client_id or not self.client_secret:
            logger.error("Missing required credentials for token refresh")
            return False

        try:
            logger.info("Refreshing Zoho access token...")

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.token_url,
                    data={
                        "grant_type": "refresh_token",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "refresh_token": self.refresh_token,
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    self._access_token = data.get("access_token")
                    expires_in = data.get("expires_in", 3600)  # Default to 1 hour

                    # Calculate expiration time
                    self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)

                    # Update .env file with new token
                    await self._update_env_file(self._access_token)

                    logger.info(f"✅ Access token refreshed successfully. Expires at: {self._token_expires_at}")
                    return True
                else:
                    logger.error(f"Failed to refresh token: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            logger.error(f"Error refreshing access token: {str(e)}", exc_info=True)
            return False

    async def _update_env_file(self, new_token: str):
        """Update .env file with new access token"""
        try:
            # Determine the path based on environment
            if os.path.exists("/home/deploy/TSH_ERP_Ecosystem/.env"):
                env_path = Path("/home/deploy/TSH_ERP_Ecosystem/.env")
            else:
                # For local development
                env_path = Path(".env")

            if not env_path.exists():
                logger.warning(f".env file not found at {env_path}")
                return

            # Read current .env content
            content = env_path.read_text()

            # Replace ZOHO_ACCESS_TOKEN line
            lines = content.split('\n')
            updated_lines = []
            token_updated = False

            for line in lines:
                if line.startswith('ZOHO_ACCESS_TOKEN='):
                    updated_lines.append(f'ZOHO_ACCESS_TOKEN={new_token}')
                    token_updated = True
                else:
                    updated_lines.append(line)

            # If token line wasn't found, add it
            if not token_updated:
                updated_lines.append(f'ZOHO_ACCESS_TOKEN={new_token}')

            # Write back to file
            env_path.write_text('\n'.join(updated_lines))
            logger.info(f"✅ Updated .env file with new access token")

        except Exception as e:
            logger.error(f"Failed to update .env file: {str(e)}", exc_info=True)

    async def get_valid_token(self) -> Optional[str]:
        """Get a valid access token, refreshing if necessary"""
        # Always reload from .env file first (in case another process updated it)
        current_token = self._reload_token_from_env()

        if current_token and current_token != self._access_token:
            logger.info("Loaded updated token from .env file")
            self._access_token = current_token
            # Assume it's valid for now (will refresh if Zoho returns 401)
            return self._access_token

        if self._is_token_valid():
            logger.debug("Current token is still valid")
            return self._access_token

        logger.info("Token expired or invalid, refreshing...")
        success = await self._refresh_access_token()

        if success:
            return self._access_token
        else:
            logger.error("Failed to get valid token")
            return None

    async def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers with valid token"""
        token = await self.get_valid_token()

        if not token:
            raise Exception("Unable to obtain valid Zoho access token")

        return {
            "Authorization": f"Zoho-oauthtoken {token}",
            "Content-Type": "application/json"
        }

    async def test_token(self) -> bool:
        """Test if current token works by making a simple API call"""
        try:
            headers = await self.get_auth_headers()

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.inventory_api_base}/items",
                    headers=headers,
                    params={
                        "organization_id": self.organization_id,
                        "per_page": 1
                    }
                )

                if response.status_code == 200:
                    logger.info("✅ Token test successful")
                    return True
                elif response.status_code == 401:
                    logger.warning("⚠️ Token test failed with 401 - token invalid")
                    return False
                else:
                    logger.warning(f"⚠️ Token test returned status {response.status_code}")
                    return False

        except Exception as e:
            logger.error(f"Error testing token: {str(e)}")
            return False

    async def ensure_valid_token(self) -> bool:
        """Ensure we have a valid token, refresh if needed"""
        # First try to get a valid token
        token = await self.get_valid_token()

        if not token:
            return False

        # Test the token
        is_valid = await self.test_token()

        if not is_valid:
            # Force refresh
            logger.info("Token test failed, forcing refresh...")
            success = await self._refresh_access_token()
            return success

        return True


# Global instance
_token_manager: Optional[ZohoTokenManager] = None


def get_token_manager() -> ZohoTokenManager:
    """Get or create global token manager instance"""
    global _token_manager

    if _token_manager is None:
        _token_manager = ZohoTokenManager()

    return _token_manager


async def start_token_refresh_scheduler():
    """Background task to periodically refresh tokens"""
    manager = get_token_manager()

    logger.info("🔄 Starting Zoho token refresh scheduler...")

    while True:
        try:
            # Check and refresh token if needed every 30 minutes
            await manager.ensure_valid_token()

            # Sleep for 30 minutes
            await asyncio.sleep(1800)

        except Exception as e:
            logger.error(f"Error in token refresh scheduler: {str(e)}", exc_info=True)
            # Sleep for 5 minutes before retrying
            await asyncio.sleep(300)
