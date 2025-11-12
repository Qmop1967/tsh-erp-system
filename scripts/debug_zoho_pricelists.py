#!/usr/bin/env python3
"""
Debug script to inspect Zoho Books pricebooks API response structure.
"""
import asyncio
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.tds.integrations.zoho.client import UnifiedZohoClient, ZohoAPI
from app.tds.integrations.zoho.auth import ZohoAuthManager, ZohoCredentials


async def main():
    """Fetch and print raw pricelist data from Zoho."""
    import os

    # Initialize Zoho client
    creds = ZohoCredentials(
        client_id=os.getenv('ZOHO_CLIENT_ID'),
        client_secret=os.getenv('ZOHO_CLIENT_SECRET'),
        refresh_token=os.getenv('ZOHO_REFRESH_TOKEN'),
        organization_id=os.getenv('ZOHO_ORGANIZATION_ID')
    )
    auth_manager = ZohoAuthManager(creds)
    await auth_manager.start()

    zoho_client = UnifiedZohoClient(
        auth_manager=auth_manager,
        organization_id=creds.organization_id,
        rate_limit=100
    )

    try:
        print("Fetching price lists from Zoho Books...")
        response = await zoho_client.get(
            api_type=ZohoAPI.BOOKS,
            endpoint="pricebooks",
            params={"per_page": 200, "page": 1}
        )

        print(f"\n{'='*70}")
        print("FULL RESPONSE:")
        print(f"{'='*70}")
        print(json.dumps(response, indent=2, ensure_ascii=False))

        pricelists = response.get('pricebooks', [])
        print(f"\n{'='*70}")
        print(f"Found {len(pricelists)} price lists")
        print(f"{'='*70}")

        if pricelists:
            print("\nFIRST PRICELIST STRUCTURE:")
            print(json.dumps(pricelists[0], indent=2, ensure_ascii=False))

            print("\n\nALL PRICELIST NAMES:")
            for i, pl in enumerate(pricelists, 1):
                name = pl.get('pricebook_name', pl.get('name', 'NO NAME'))
                pricebook_id = pl.get('pricebook_id', pl.get('id', 'NO ID'))
                print(f"{i}. {name} (ID: {pricebook_id})")
                print(f"   Keys: {list(pl.keys())}")

    finally:
        await zoho_client.close_session()


if __name__ == "__main__":
    asyncio.run(main())
