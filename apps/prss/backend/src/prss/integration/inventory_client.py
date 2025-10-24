"""Inventory system integration client"""
from .base_client import BaseClient
from prss.config import settings


class InventoryClient(BaseClient):
    def __init__(self):
        super().__init__(
            settings.inventory_api_base,
            settings.inventory_api_token
        )

    async def create_transfer(self, data: dict):
        """Create inventory transfer"""
        return await self.post("/transfers", data)

    async def get_product(self, product_id: int):
        """Get product details"""
        return await self.get(f"/products/{product_id}")
