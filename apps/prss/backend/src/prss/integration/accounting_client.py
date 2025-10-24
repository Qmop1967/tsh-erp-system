"""Accounting system integration client"""
from .base_client import BaseClient
from prss.config import settings


class AccountingClient(BaseClient):
    def __init__(self):
        super().__init__(
            settings.accounting_api_base,
            settings.accounting_api_token
        )

    async def post_transaction(self, data: dict):
        """Post accounting transaction"""
        return await self.post("/transactions", data)
