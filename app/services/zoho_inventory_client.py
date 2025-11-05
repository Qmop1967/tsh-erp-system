"""
Zoho Inventory API Client
Handles all interactions with Zoho Inventory API with pagination support
Focuses on stock management, warehouses, and inventory-specific operations
"""
import httpx
import logging
from typing import Dict, List, Any, Optional, AsyncIterator
from .zoho_auth_service import ZohoAuthService

logger = logging.getLogger(__name__)


class ZohoInventoryClient:
    """
    Client for Zoho Inventory API operations
    """

    BASE_URL = "https://www.zohoapis.com/inventory/v1"
    ORGANIZATION_ID = "748369814"

    def __init__(self, db_session=None):
        """
        Initialize Zoho Inventory client

        Args:
            db_session: Optional database session for token storage
        """
        self.db_session = db_session
        self.auth_service = ZohoAuthService

    async def _get_headers(self) -> Dict[str, str]:
        """Get authenticated headers for API requests"""
        access_token = await self.auth_service.get_access_token(self.db_session)
        return self.auth_service.get_headers(access_token)

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to Zoho Inventory API

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data

        Returns:
            Response JSON data

        Raises:
            Exception on API errors
        """
        url = f"{self.BASE_URL}/{endpoint}"
        headers = await self._get_headers()

        # Add organization_id to all requests
        if params is None:
            params = {}
        params["organization_id"] = self.ORGANIZATION_ID

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=data
                )

                response.raise_for_status()
                return response.json()

            except httpx.HTTPError as e:
                logger.error(f"Zoho Inventory API error: {e}")
                logger.error(f"Response: {e.response.text if hasattr(e, 'response') else 'No response'}")
                raise

    async def fetch_items_paginated(
        self,
        per_page: int = 200,
        filters: Optional[Dict] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Fetch all items from Zoho Inventory with pagination

        Args:
            per_page: Number of items per page (max 200)
            filters: Optional filters to apply

        Yields:
            Individual item dictionaries
        """
        page = 1
        has_more = True

        while has_more:
            params = {
                "page": page,
                "per_page": min(per_page, 200)  # Max 200
            }

            if filters:
                params.update(filters)

            logger.info(f"Fetching Zoho Inventory items - Page {page}")

            try:
                data = await self._make_request("GET", "items", params=params)

                items = data.get("items", [])
                logger.info(f"  Retrieved {len(items)} items from page {page}")

                for item in items:
                    yield item

                # Check if more pages exist
                page_context = data.get("page_context", {})
                has_more = page_context.get("has_more_page", False)

                if has_more:
                    page += 1
                else:
                    logger.info(f"  No more pages - completed at page {page}")
                    break

            except Exception as e:
                logger.error(f"Error fetching items page {page}: {e}")
                break

    async def fetch_item_stock(self, item_id: str) -> Dict[str, Any]:
        """
        Fetch stock information for a specific item

        Args:
            item_id: Zoho item ID

        Returns:
            Item stock details including warehouses, available stock, etc.
        """
        logger.debug(f"Fetching stock for item {item_id}")

        data = await self._make_request("GET", f"items/{item_id}")
        return data.get("item", {})

    async def fetch_warehouses(self) -> List[Dict[str, Any]]:
        """
        Fetch all warehouses from Zoho Inventory

        Returns:
            List of warehouse dictionaries
        """
        logger.info("Fetching Zoho Inventory warehouses")

        data = await self._make_request("GET", "warehouses")
        warehouses = data.get("warehouses", [])

        logger.info(f"  Retrieved {len(warehouses)} warehouses")
        return warehouses

    async def fetch_item_image_url(self, item_id: str) -> Optional[str]:
        """
        Get the image URL for an item

        Args:
            item_id: Zoho item ID

        Returns:
            Image URL or None if no image exists
        """
        try:
            item = await self.fetch_item_stock(item_id)

            # Check for image document ID
            image_doc_id = item.get("image_document_id")
            if image_doc_id:
                # Construct image URL
                return f"{self.BASE_URL}/items/{item_id}/image?organization_id={self.ORGANIZATION_ID}"

            # Alternative: Check for direct image URL
            image_url = item.get("image_url")
            if image_url:
                return image_url

            return None

        except Exception as e:
            logger.warning(f"Could not fetch image URL for item {item_id}: {e}")
            return None

    async def download_item_image(self, item_id: str) -> Optional[bytes]:
        """
        Download image data for an item

        Args:
            item_id: Zoho item ID

        Returns:
            Image bytes or None if download fails
        """
        image_url = await self.fetch_item_image_url(item_id)
        if not image_url:
            return None

        headers = await self._get_headers()

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(image_url, headers=headers)
                response.raise_for_status()

                logger.debug(f"Downloaded image for item {item_id} ({len(response.content)} bytes)")
                return response.content

            except Exception as e:
                logger.warning(f"Failed to download image for item {item_id}: {e}")
                return None

    async def fetch_composite_items_paginated(
        self,
        per_page: int = 200
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Fetch all composite/bundle items from Zoho Inventory with pagination

        Args:
            per_page: Number of items per page

        Yields:
            Individual composite item dictionaries
        """
        page = 1
        has_more = True

        while has_more:
            params = {
                "page": page,
                "per_page": min(per_page, 200)
            }

            logger.info(f"Fetching Zoho Inventory composite items - Page {page}")

            try:
                data = await self._make_request("GET", "compositeitems", params=params)

                items = data.get("composite_items", [])
                logger.info(f"  Retrieved {len(items)} composite items from page {page}")

                for item in items:
                    yield item

                page_context = data.get("page_context", {})
                has_more = page_context.get("has_more_page", False)

                if has_more:
                    page += 1
                else:
                    break

            except Exception as e:
                logger.error(f"Error fetching composite items page {page}: {e}")
                break

    async def fetch_stock_adjustments_paginated(
        self,
        per_page: int = 200,
        filters: Optional[Dict] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Fetch stock adjustments from Zoho Inventory with pagination

        Args:
            per_page: Number of adjustments per page
            filters: Optional filters (date_range, etc.)

        Yields:
            Individual stock adjustment dictionaries
        """
        page = 1
        has_more = True

        while has_more:
            params = {
                "page": page,
                "per_page": min(per_page, 200)
            }

            if filters:
                params.update(filters)

            logger.info(f"Fetching Zoho Inventory stock adjustments - Page {page}")

            try:
                data = await self._make_request("GET", "inventoryadjustments", params=params)

                adjustments = data.get("inventoryadjustments", [])
                logger.info(f"  Retrieved {len(adjustments)} adjustments from page {page}")

                for adjustment in adjustments:
                    yield adjustment

                page_context = data.get("page_context", {})
                has_more = page_context.get("has_more_page", False)

                if has_more:
                    page += 1
                else:
                    break

            except Exception as e:
                logger.error(f"Error fetching stock adjustments page {page}: {e}")
                break
