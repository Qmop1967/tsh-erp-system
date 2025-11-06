"""
Unified Zoho API Client
=======================

Central client for all Zoho API interactions (Books, Inventory, CRM).
Consolidates zoho_service.py, zoho_inventory_client.py, and zoho_books_client.py.

عميل API موحد لجميع خدمات Zoho

Features:
- Async HTTP client with connection pooling
- Automatic token refresh
- Built-in rate limiting
- Retry logic with exponential backoff
- Request/response logging
- Error handling and recovery
- Batch operations support
- Pagination handling

Author: TSH ERP Team
Date: November 6, 2025
"""

import asyncio
import aiohttp
import time
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from urllib.parse import urlencode
from enum import Enum

from .auth import ZohoAuthManager
from .utils.rate_limiter import RateLimiter
from .utils.retry import RetryStrategy
from ...core.events import publish_event
from ....core.event_bus import EventBus

logger = logging.getLogger(__name__)


class ZohoAPI(str, Enum):
    """Zoho API types"""
    BOOKS = "books"
    INVENTORY = "inventory"
    CRM = "crm"


class ZohoAPIError(Exception):
    """Zoho API error with detailed information"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict] = None,
        api_type: Optional[ZohoAPI] = None
    ):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        self.api_type = api_type
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.message,
            "status_code": self.status_code,
            "api_type": self.api_type,
            "response": self.response_data,
            "timestamp": datetime.utcnow().isoformat()
        }


class UnifiedZohoClient:
    """
    Unified Zoho API Client
    عميل موحد لـ API Zoho

    Supports:
    - Zoho Books (accounting, invoices, bills)
    - Zoho Inventory (products, stock, orders)
    - Zoho CRM (customers, contacts, deals)
    """

    # API Base URLs
    API_BASES = {
        ZohoAPI.BOOKS: "https://www.zohoapis.com/books/v3",
        ZohoAPI.INVENTORY: "https://www.zohoapis.com/inventory/v1",
        ZohoAPI.CRM: "https://www.zohoapis.com/crm/v3"
    }

    def __init__(
        self,
        auth_manager: ZohoAuthManager,
        organization_id: str,
        rate_limit: int = 100,  # requests per minute
        max_retries: int = 3,
        timeout: int = 30,
        event_bus: Optional[EventBus] = None
    ):
        """
        Initialize Unified Zoho Client

        Args:
            auth_manager: ZohoAuthManager instance for authentication
            organization_id: Zoho organization ID
            rate_limit: Maximum requests per minute
            max_retries: Maximum retry attempts for failed requests
            timeout: Request timeout in seconds
            event_bus: Event bus for publishing events
        """
        self.auth_manager = auth_manager
        self.organization_id = organization_id
        self.rate_limiter = RateLimiter(rate_limit)
        self.retry_strategy = RetryStrategy(max_retries)
        self.timeout = timeout
        self.event_bus = event_bus
        self.session: Optional[aiohttp.ClientSession] = None

        # Statistics
        self.stats = {
            "requests_made": 0,
            "requests_failed": 0,
            "tokens_refreshed": 0,
            "rate_limit_hits": 0
        }

    async def __aenter__(self):
        """Context manager entry - create HTTP session"""
        await self.start_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close HTTP session"""
        await self.close_session()

    async def start_session(self):
        """Start HTTP session"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                connector=aiohttp.TCPConnector(limit=100, limit_per_host=10)
            )
            logger.info("Zoho HTTP session started")

    async def close_session(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("Zoho HTTP session closed")

    def _get_api_url(
        self,
        api_type: ZohoAPI,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Construct full API URL

        Args:
            api_type: Type of Zoho API (books, inventory, crm)
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            str: Full API URL
        """
        base_url = self.API_BASES[api_type]
        url = f"{base_url}/{endpoint.lstrip('/')}"

        # Add organization_id for Books and Inventory
        if api_type in [ZohoAPI.BOOKS, ZohoAPI.INVENTORY]:
            params = params or {}
            params['organization_id'] = self.organization_id

        if params:
            url = f"{url}?{urlencode(params)}"

        return url

    async def _make_request(
        self,
        method: str,
        api_type: ZohoAPI,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        retry: bool = True
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Zoho API with retry logic

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            api_type: Type of Zoho API
            endpoint: API endpoint
            params: Query parameters
            json_data: JSON payload for POST/PUT
            retry: Enable retry logic

        Returns:
            dict: API response data

        Raises:
            ZohoAPIError: If request fails after retries
        """
        if not self.session:
            await self.start_session()

        # Wait for rate limiter
        await self.rate_limiter.acquire()

        # Get access token
        access_token = await self.auth_manager.get_valid_token()
        headers = {
            'Authorization': f'Zoho-oauthtoken {access_token}',
            'Content-Type': 'application/json'
        }

        url = self._get_api_url(api_type, endpoint, params)

        attempt = 0
        last_error = None

        while attempt < self.retry_strategy.max_retries:
            try:
                self.stats["requests_made"] += 1

                async with self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data
                ) as response:
                    response_data = await response.json()

                    # Success
                    if response.status in [200, 201]:
                        logger.debug(
                            f"Zoho API success: {method} {endpoint} "
                            f"[{response.status}]"
                        )

                        # Publish success event
                        if self.event_bus:
                            await self.event_bus.publish({
                                "event_type": "tds.zoho.api.success",
                                "data": {
                                    "method": method,
                                    "endpoint": endpoint,
                                    "api_type": api_type,
                                    "status_code": response.status
                                }
                            })

                        return response_data

                    # Token expired - refresh and retry
                    if response.status == 401:
                        logger.warning("Access token expired, refreshing...")
                        await self.auth_manager.refresh_access_token()
                        self.stats["tokens_refreshed"] += 1
                        access_token = await self.auth_manager.get_valid_token()
                        headers['Authorization'] = f'Zoho-oauthtoken {access_token}'
                        continue

                    # Rate limit - wait and retry
                    if response.status == 429:
                        self.stats["rate_limit_hits"] += 1
                        wait_time = self.retry_strategy.get_wait_time(attempt)
                        logger.warning(
                            f"Rate limit hit, waiting {wait_time}s before retry"
                        )
                        await asyncio.sleep(wait_time)
                        attempt += 1
                        continue

                    # Other errors
                    error_msg = response_data.get('message', 'Unknown error')
                    raise ZohoAPIError(
                        message=error_msg,
                        status_code=response.status,
                        response_data=response_data,
                        api_type=api_type
                    )

            except aiohttp.ClientError as e:
                last_error = e
                if retry:
                    wait_time = self.retry_strategy.get_wait_time(attempt)
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}), "
                        f"retrying in {wait_time}s: {str(e)}"
                    )
                    await asyncio.sleep(wait_time)
                    attempt += 1
                else:
                    break

            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error in Zoho API request: {str(e)}")
                break

        # All retries exhausted
        self.stats["requests_failed"] += 1
        error_msg = f"Request failed after {attempt} attempts: {str(last_error)}"

        # Publish failure event
        if self.event_bus:
            await self.event_bus.publish({
                "event_type": "tds.zoho.api.failed",
                "data": {
                    "method": method,
                    "endpoint": endpoint,
                    "api_type": api_type,
                    "error": error_msg,
                    "attempts": attempt
                }
            })

        raise ZohoAPIError(
            message=error_msg,
            api_type=api_type
        )

    # Convenience methods for HTTP verbs

    async def get(
        self,
        api_type: ZohoAPI,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """GET request"""
        return await self._make_request("GET", api_type, endpoint, params=params)

    async def post(
        self,
        api_type: ZohoAPI,
        endpoint: str,
        data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """POST request"""
        return await self._make_request(
            "POST", api_type, endpoint, params=params, json_data=data
        )

    async def put(
        self,
        api_type: ZohoAPI,
        endpoint: str,
        data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """PUT request"""
        return await self._make_request(
            "PUT", api_type, endpoint, params=params, json_data=data
        )

    async def delete(
        self,
        api_type: ZohoAPI,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """DELETE request"""
        return await self._make_request("DELETE", api_type, endpoint, params=params)

    # Advanced operations

    async def paginated_fetch(
        self,
        api_type: ZohoAPI,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        page_size: int = 200,
        max_pages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch all pages of a paginated endpoint

        Args:
            api_type: Type of Zoho API
            endpoint: API endpoint
            params: Query parameters
            page_size: Items per page
            max_pages: Maximum pages to fetch (None = all)

        Returns:
            list: All items from all pages
        """
        params = params or {}
        params['per_page'] = page_size

        all_items = []
        page = 1

        while True:
            if max_pages and page > max_pages:
                break

            params['page'] = page
            response = await self.get(api_type, endpoint, params)

            # Extract items (different APIs have different response structures)
            items = self._extract_items_from_response(response, api_type)

            if not items:
                break

            all_items.extend(items)

            # Check if there are more pages
            has_more = self._has_more_pages(response, api_type)
            if not has_more:
                break

            page += 1

        logger.info(
            f"Paginated fetch complete: {len(all_items)} items "
            f"from {page} pages"
        )

        return all_items

    def _extract_items_from_response(
        self,
        response: Dict[str, Any],
        api_type: ZohoAPI
    ) -> List[Dict[str, Any]]:
        """Extract items from API response based on API type"""
        if api_type == ZohoAPI.BOOKS:
            # Books API structure varies by endpoint
            for key in ['items', 'invoices', 'bills', 'customers', 'contacts']:
                if key in response:
                    return response[key]

        elif api_type == ZohoAPI.INVENTORY:
            # Inventory API structure
            for key in ['items', 'salesorders', 'purchaseorders']:
                if key in response:
                    return response[key]

        elif api_type == ZohoAPI.CRM:
            return response.get('data', [])

        return []

    def _has_more_pages(
        self,
        response: Dict[str, Any],
        api_type: ZohoAPI
    ) -> bool:
        """Check if there are more pages to fetch"""
        page_context = response.get('page_context', {})
        return page_context.get('has_more_page', False)

    async def batch_request(
        self,
        requests: List[Dict[str, Any]],
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple requests concurrently with concurrency limit

        Args:
            requests: List of request definitions
            max_concurrent: Maximum concurrent requests

        Returns:
            list: Results from all requests
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def execute_request(request_def):
            async with semaphore:
                return await self._make_request(
                    method=request_def['method'],
                    api_type=request_def['api_type'],
                    endpoint=request_def['endpoint'],
                    params=request_def.get('params'),
                    json_data=request_def.get('data')
                )

        results = await asyncio.gather(
            *[execute_request(req) for req in requests],
            return_exceptions=True
        )

        return results

    async def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to all Zoho APIs

        Returns:
            dict: Connection test results
        """
        results = {}

        for api_type in ZohoAPI:
            try:
                # Test with a simple endpoint for each API
                test_endpoints = {
                    ZohoAPI.BOOKS: "organizations",
                    ZohoAPI.INVENTORY: "items",
                    ZohoAPI.CRM: "settings/modules"
                }

                endpoint = test_endpoints.get(api_type)
                if endpoint:
                    response = await self.get(api_type, endpoint, {'per_page': 1})
                    results[api_type] = {
                        "status": "success",
                        "message": "Connection successful"
                    }

            except Exception as e:
                results[api_type] = {
                    "status": "failed",
                    "error": str(e)
                }

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "results": results,
            "overall_status": "success" if all(
                r.get("status") == "success" for r in results.values()
            ) else "failed"
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        return {
            **self.stats,
            "rate_limiter": self.rate_limiter.get_stats(),
            "session_active": self.session and not self.session.closed
        }
