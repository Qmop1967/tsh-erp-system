"""Base HTTP client for integrations"""
import httpx
from prss.config import settings


class BaseClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    async def post(self, endpoint: str, data: dict):
        """POST request"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}{endpoint}",
                json=data,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def get(self, endpoint: str, params: dict = None):
        """GET request"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}{endpoint}",
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
