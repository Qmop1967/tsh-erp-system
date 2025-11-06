"""
Zoho OAuth Token Management Service
Handles token refresh and provides valid access tokens for Zoho API calls
"""
import os
import httpx
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

class ZohoAuthService:
    """
    Manages Zoho OAuth tokens with automatic refresh
    """

    # Zoho OAuth endpoints
    TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"

    # Credentials from environment
    CLIENT_ID = os.getenv("ZOHO_CLIENT_ID", "1000.RYRPK7578ZRKN6K4HKNF4LKL2CC9IQ")
    CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET", "a39a5dcdc057a8490cb7960d1400f62ce14edd6455")
    REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN", "1000.46b59c983826f1ac35a620f243c490f2.8417561af04f558a86cc412eb58ba0e9")

    # In-memory cache
    _cached_token: Optional[str] = None
    _token_expiry: Optional[datetime] = None

    @classmethod
    async def get_access_token(cls, db: Optional[AsyncSession] = None) -> str:
        """
        Get a valid access token, refreshing if necessary

        Args:
            db: Optional database session for persistent storage

        Returns:
            Valid Zoho access token
        """
        # Check if cached token is still valid
        if cls._cached_token and cls._token_expiry:
            if datetime.now() < cls._token_expiry - timedelta(minutes=5):
                logger.debug("Using cached access token")
                return cls._cached_token

        # Token expired or not cached, refresh it
        logger.info("Refreshing Zoho access token")
        new_token = await cls._refresh_access_token()

        # Update cache
        cls._cached_token = new_token
        # Tokens typically valid for 1 hour
        cls._token_expiry = datetime.now() + timedelta(minutes=55)

        # Optionally store in database
        if db:
            await cls._store_token_in_db(db, new_token)

        return new_token

    @classmethod
    async def _refresh_access_token(cls) -> str:
        """
        Refresh the access token using refresh token

        Returns:
            New access token

        Raises:
            Exception if refresh fails
        """
        if not cls.REFRESH_TOKEN:
            raise ValueError("ZOHO_REFRESH_TOKEN not configured")

        params = {
            "refresh_token": cls.REFRESH_TOKEN,
            "client_id": cls.CLIENT_ID,
            "client_secret": cls.CLIENT_SECRET,
            "grant_type": "refresh_token"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(cls.TOKEN_URL, params=params, timeout=30.0)
                response.raise_for_status()

                data = response.json()

                if "access_token" not in data:
                    raise ValueError(f"No access token in response: {data}")

                access_token = data["access_token"]
                logger.info("Successfully refreshed Zoho access token")

                return access_token

            except httpx.HTTPError as e:
                logger.error(f"Failed to refresh Zoho token: {e}")
                raise Exception(f"Zoho token refresh failed: {e}")

    @classmethod
    async def _store_token_in_db(cls, db: AsyncSession, token: str) -> None:
        """
        Store the access token in database for persistence across restarts

        Args:
            db: Database session
            token: Access token to store
        """
        try:
            await db.execute(
                text("""
                    INSERT INTO zoho_tokens (service, access_token, expires_at, updated_at)
                    VALUES ('zoho_api', :token, :expires_at, NOW())
                    ON CONFLICT (service)
                    DO UPDATE SET
                        access_token = EXCLUDED.access_token,
                        expires_at = EXCLUDED.expires_at,
                        updated_at = NOW()
                """),
                {
                    "token": token,
                    "expires_at": datetime.now() + timedelta(minutes=55)
                }
            )
            await db.commit()
            logger.debug("Stored access token in database")
        except Exception as e:
            logger.warning(f"Failed to store token in database: {e}")
            # Non-critical, continue without DB storage

    @classmethod
    def get_headers(cls, access_token: str) -> dict:
        """
        Get HTTP headers for Zoho API requests

        Args:
            access_token: Valid Zoho access token

        Returns:
            Dictionary of headers
        """
        return {
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Content-Type": "application/json"
        }

    @classmethod
    async def validate_token(cls, access_token: str) -> bool:
        """
        Validate if an access token is still valid

        Args:
            access_token: Token to validate

        Returns:
            True if valid, False otherwise
        """
        # Try a simple API call to check token validity
        test_url = "https://www.zohoapis.com/inventory/v1/organizations"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    test_url,
                    headers=cls.get_headers(access_token),
                    timeout=10.0
                )
                return response.status_code == 200
            except:
                return False
