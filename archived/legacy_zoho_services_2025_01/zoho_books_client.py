"""
Zoho Books API Client
Handles all interactions with Zoho Books API with pagination support
"""
import httpx
import logging
from typing import Dict, List, Any, Optional, AsyncIterator
from .zoho_auth_service import ZohoAuthService

logger = logging.getLogger(__name__)


class ZohoBooksClient:
    """
    Client for Zoho Books API operations
    """

    BASE_URL = "https://www.zohoapis.com/books/v3"
    ORGANIZATION_ID = "748369814"

    def __init__(self, db_session=None):
        """
        Initialize Zoho Books client

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
        Make authenticated request to Zoho Books API

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
        url = f"{ZohoBooksClient.BASE_URL}/{endpoint}"
        headers = await self._get_headers()

        # Add organization_id to all requests
        if params is None:
            params = {}
        params["organization_id"] = ZohoBooksClient.ORGANIZATION_ID

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
                logger.error(f"Zoho Books API error: {e}")
                logger.error(f"Response: {e.response.text if hasattr(e, 'response') else 'No response'}")
                raise

    async def fetch_items_paginated(
        self,
        per_page: int = 200,
        filters: Optional[Dict] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Fetch all items from Zoho Books with pagination

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

            logger.info(f"Fetching Zoho Books items - Page {page}")

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

    async def fetch_item_details(self, item_id: str) -> Dict[str, Any]:
        """
        Fetch detailed information for a specific item

        Args:
            item_id: Zoho item ID

        Returns:
            Item details including stock, pricing, etc.
        """
        logger.debug(f"Fetching details for item {item_id}")

        data = await self._make_request("GET", f"items/{item_id}")
        return data.get("item", {})

    async def fetch_pricelists(self) -> List[Dict[str, Any]]:
        """
        Fetch all price lists from Zoho Books

        Returns:
            List of price list dictionaries
        """
        logger.info("Fetching Zoho Books price lists")

        data = await self._make_request("GET", "pricelists")
        pricelists = data.get("pricelists", [])

        logger.info(f"  Retrieved {len(pricelists)} price lists")
        return pricelists

    async def fetch_pricelist_details(self, pricelist_id: str) -> Dict[str, Any]:
        """
        Fetch detailed pricelist with all item prices

        Args:
            pricelist_id: Zoho pricelist ID

        Returns:
            Pricelist details with items
        """
        logger.debug(f"Fetching pricelist details: {pricelist_id}")

        data = await self._make_request("GET", f"pricelists/{pricelist_id}")
        return data.get("pricelist", {})

    async def fetch_customers_paginated(
        self,
        per_page: int = 200
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Fetch all customers from Zoho Books with pagination

        Args:
            per_page: Number of customers per page

        Yields:
            Individual customer dictionaries
        """
        page = 1
        has_more = True

        while has_more:
            params = {
                "page": page,
                "per_page": min(per_page, 200)
            }

            logger.info(f"Fetching Zoho Books customers - Page {page}")

            try:
                data = await self._make_request("GET", "contacts", params=params)

                customers = data.get("contacts", [])
                logger.info(f"  Retrieved {len(customers)} customers from page {page}")

                for customer in customers:
                    yield customer

                page_context = data.get("page_context", {})
                has_more = page_context.get("has_more_page", False)

                if has_more:
                    page += 1
                else:
                    break

            except Exception as e:
                logger.error(f"Error fetching customers page {page}: {e}")
                break

    async def fetch_invoices_paginated(
        self,
        per_page: int = 200,
        filters: Optional[Dict] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Fetch all invoices from Zoho Books with pagination

        Args:
            per_page: Number of invoices per page
            filters: Optional filters (status, date_range, etc.)

        Yields:
            Individual invoice dictionaries
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

            logger.info(f"Fetching Zoho Books invoices - Page {page}")

            try:
                data = await self._make_request("GET", "invoices", params=params)

                invoices = data.get("invoices", [])
                logger.info(f"  Retrieved {len(invoices)} invoices from page {page}")

                for invoice in invoices:
                    yield invoice

                page_context = data.get("page_context", {})
                has_more = page_context.get("has_more_page", False)

                if has_more:
                    page += 1
                else:
                    break

            except Exception as e:
                logger.error(f"Error fetching invoices page {page}: {e}")
                break
