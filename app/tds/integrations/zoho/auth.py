"""
Zoho OAuth Authentication Manager
==================================

Unified authentication and token management for Zoho APIs.
Consolidates zoho_auth_service.py, zoho_token_manager.py, and zoho_token_refresh_scheduler.py.

مدير مصادقة OAuth موحد لـ Zoho

Features:
- OAuth 2.0 authentication flow
- Automatic access token refresh
- Refresh token rotation
- Token expiry tracking
- Secure credential storage
- Multi-organization support
- Background token refresh scheduling

Author: TSH ERP Team
Date: November 6, 2025
"""

import asyncio
import aiohttp
import time
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

from ....core.events.event_bus import EventBus

logger = logging.getLogger(__name__)


@dataclass
class ZohoCredentials:
    """Zoho API credentials"""
    client_id: str
    client_secret: str
    refresh_token: str
    organization_id: str
    access_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None


class ZohoAuthError(Exception):
    """Zoho authentication error"""
    pass


class ZohoAuthManager:
    """
    Zoho OAuth Authentication Manager
    مدير مصادقة OAuth لـ Zoho

    Handles all authentication and token management for Zoho APIs.
    """

    TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"
    TOKEN_REFRESH_MARGIN = 300  # Refresh 5 minutes before expiry

    def __init__(
        self,
        credentials: ZohoCredentials,
        event_bus: Optional[EventBus] = None,
        auto_refresh: bool = True
    ):
        """
        Initialize Zoho Auth Manager

        Args:
            credentials: Zoho API credentials
            event_bus: Event bus for publishing auth events
            auto_refresh: Enable automatic token refresh
        """
        self.credentials = credentials
        self.event_bus = event_bus
        self.auto_refresh = auto_refresh

        self._access_token: Optional[str] = credentials.access_token
        self._token_expires_at: Optional[datetime] = credentials.token_expires_at
        self._refresh_lock = asyncio.Lock()
        self._refresh_task: Optional[asyncio.Task] = None

        # Statistics
        self.stats = {
            "tokens_refreshed": 0,
            "refresh_failures": 0,
            "last_refresh": None,
            "last_error": None
        }

    async def start(self):
        """Start auth manager and background refresh task"""
        # Get initial access token if not available
        if not self._access_token:
            await self.refresh_access_token()

        # Start background refresh task if auto_refresh enabled
        if self.auto_refresh:
            self._refresh_task = asyncio.create_task(self._background_refresh())
            logger.info("Zoho auth manager started with auto-refresh")
        else:
            logger.info("Zoho auth manager started without auto-refresh")

    async def stop(self):
        """Stop auth manager and cancel background tasks"""
        if self._refresh_task:
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except asyncio.CancelledError:
                pass
            logger.info("Zoho auth manager stopped")

    async def get_valid_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary

        Returns:
            str: Valid access token

        Raises:
            ZohoAuthError: If unable to get valid token
        """
        # Check if token needs refresh
        if self._needs_refresh():
            await self.refresh_access_token()

        if not self._access_token:
            raise ZohoAuthError("No valid access token available")

        return self._access_token

    def _needs_refresh(self) -> bool:
        """Check if token needs to be refreshed"""
        if not self._access_token:
            return True

        if not self._token_expires_at:
            return True

        # Refresh if token expires within the margin
        time_until_expiry = (self._token_expires_at - datetime.utcnow()).total_seconds()
        return time_until_expiry < self.TOKEN_REFRESH_MARGIN

    async def refresh_access_token(self) -> str:
        """
        Refresh access token using refresh token

        Returns:
            str: New access token

        Raises:
            ZohoAuthError: If refresh fails
        """
        async with self._refresh_lock:
            # Check again inside lock in case another coroutine refreshed it
            if not self._needs_refresh():
                return self._access_token

            logger.info("Refreshing Zoho access token...")

            try:
                # Prepare refresh request
                data = {
                    'refresh_token': self.credentials.refresh_token,
                    'client_id': self.credentials.client_id,
                    'client_secret': self.credentials.client_secret,
                    'grant_type': 'refresh_token'
                }

                # Make refresh request
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.TOKEN_URL,
                        data=data,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        response_data = await response.json()

                        if response.status != 200:
                            error_msg = response_data.get(
                                'error',
                                'Unknown error during token refresh'
                            )
                            raise ZohoAuthError(f"Token refresh failed: {error_msg}")

                        # Extract new token
                        new_access_token = response_data.get('access_token')
                        expires_in = response_data.get('expires_in', 3600)

                        if not new_access_token:
                            raise ZohoAuthError("No access token in refresh response")

                        # Update token and expiry
                        self._access_token = new_access_token
                        self._token_expires_at = datetime.utcnow() + timedelta(
                            seconds=expires_in
                        )

                        # Update credentials
                        self.credentials.access_token = new_access_token
                        self.credentials.token_expires_at = self._token_expires_at

                        # Update stats
                        self.stats["tokens_refreshed"] += 1
                        self.stats["last_refresh"] = datetime.utcnow().isoformat()

                        logger.info(
                            f"Access token refreshed successfully. "
                            f"Expires at: {self._token_expires_at}"
                        )

                        # Publish success event
                        if self.event_bus:
                            try:
                                await self.event_bus.publish({
                                    "event_type": "tds.zoho.token.refreshed",
                                    "data": {
                                        "expires_at": self._token_expires_at.isoformat(),
                                        "expires_in": expires_in
                                    }
                                })
                            except Exception as e:
                                logger.warning(f"Failed to publish token refresh event: {e}")

                        return self._access_token

            except aiohttp.ClientError as e:
                self.stats["refresh_failures"] += 1
                self.stats["last_error"] = str(e)
                error_msg = f"Network error during token refresh: {str(e)}"
                logger.error(error_msg)

                # Publish failure event
                if self.event_bus:
                    try:
                        await self.event_bus.publish({
                            "event_type": "tds.zoho.token.refresh_failed",
                            "data": {
                                "error": error_msg
                            }
                        })
                    except Exception as e:
                        logger.warning(f"Failed to publish token refresh failure event: {e}")

                raise ZohoAuthError(error_msg) from e

            except Exception as e:
                self.stats["refresh_failures"] += 1
                self.stats["last_error"] = str(e)
                error_msg = f"Unexpected error during token refresh: {str(e)}"
                logger.error(error_msg)
                raise ZohoAuthError(error_msg) from e

    async def _background_refresh(self):
        """
        Background task to refresh token before expiry

        Runs continuously and refreshes token proactively.
        """
        logger.info("Starting background token refresh task")

        while True:
            try:
                # Calculate wait time until next refresh
                if self._token_expires_at:
                    time_until_expiry = (
                        self._token_expires_at - datetime.utcnow()
                    ).total_seconds()

                    # Refresh 5 minutes before expiry
                    wait_time = max(
                        time_until_expiry - self.TOKEN_REFRESH_MARGIN,
                        60  # Check at least every minute
                    )
                else:
                    wait_time = 60

                logger.debug(f"Next token refresh in {wait_time} seconds")

                await asyncio.sleep(wait_time)

                # Refresh token if needed
                if self._needs_refresh():
                    await self.refresh_access_token()

            except asyncio.CancelledError:
                logger.info("Background refresh task cancelled")
                break

            except Exception as e:
                logger.error(f"Error in background refresh task: {str(e)}")
                # Wait a bit before retrying
                await asyncio.sleep(60)

    async def validate_token(self) -> bool:
        """
        Validate current access token

        Returns:
            bool: True if token is valid
        """
        if not self._access_token:
            return False

        try:
            # Make a simple API call to verify token
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://www.zohoapis.com/books/v3/organizations",
                    headers={
                        'Authorization': f'Zoho-oauthtoken {self._access_token}'
                    },
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200

        except Exception as e:
            logger.warning(f"Token validation failed: {str(e)}")
            return False

    def get_token_info(self) -> Dict[str, Any]:
        """
        Get information about current token

        Returns:
            dict: Token information
        """
        if not self._token_expires_at:
            time_until_expiry = None
            is_expired = None
        else:
            time_until_expiry = (
                self._token_expires_at - datetime.utcnow()
            ).total_seconds()
            is_expired = time_until_expiry <= 0

        return {
            "has_token": bool(self._access_token),
            "expires_at": self._token_expires_at.isoformat() if self._token_expires_at else None,
            "time_until_expiry_seconds": time_until_expiry,
            "is_expired": is_expired,
            "needs_refresh": self._needs_refresh(),
            "auto_refresh_enabled": self.auto_refresh
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get auth manager statistics"""
        return {
            **self.stats,
            "token_info": self.get_token_info()
        }

    async def revoke_token(self):
        """
        Revoke current access token

        Note: Zoho doesn't provide a revoke endpoint,
        so we just clear the local token.
        """
        self._access_token = None
        self._token_expires_at = None
        logger.info("Access token revoked locally")

        if self.event_bus:
            try:
                await self.event_bus.publish({
                    "event_type": "tds.zoho.token.revoked",
                    "data": {}
                })
            except Exception as e:
                logger.warning(f"Failed to publish token revoked event: {e}")

    async def update_credentials(self, new_credentials: ZohoCredentials):
        """
        Update Zoho credentials and refresh token

        Args:
            new_credentials: New credentials to use
        """
        self.credentials = new_credentials
        self._access_token = new_credentials.access_token
        self._token_expires_at = new_credentials.token_expires_at

        # Refresh token immediately with new credentials
        if not self._access_token or self._needs_refresh():
            await self.refresh_access_token()

        logger.info("Zoho credentials updated")

    def __repr__(self) -> str:
        return (
            f"ZohoAuthManager("
            f"org_id={self.credentials.organization_id}, "
            f"has_token={bool(self._access_token)}, "
            f"auto_refresh={self.auto_refresh})"
        )
