"""Sales system integration client"""
from .base_client import BaseClient
from prss.config import settings


class SalesClient(BaseClient):
    def __init__(self):
        super().__init__(
            settings.sales_api_base,
            settings.sales_api_token
        )

    async def create_credit_note(self, data: dict):
        """Create credit note"""
        return await self.post("/credit-notes", data)

    async def get_order(self, order_id: int):
        """Get sales order"""
        return await self.get(f"/orders/{order_id}")
