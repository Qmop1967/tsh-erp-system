#!/usr/bin/env python3
"""Quick check of Zoho contact structure"""

import asyncio
import aiohttp
import json
import os

ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID", "1000.RYRPK7578ZRKN6K4HKNF4LKL2CC9IQ")
ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET", "a39a5dcdc057a8490cb7960d1400f62ce14edd6455")
ZOHO_REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN", "1000.2e358f3c53d3e22ac2d134c5c93d9c5b.118c5e88cd0a4ed2a1143056f2d09e68")
ZOHO_ORGANIZATION_ID = os.getenv("ZOHO_ORGANIZATION_ID", "748369814")


async def main():
    # Get token
    async with aiohttp.ClientSession() as session:
        url = "https://accounts.zoho.com/oauth/v2/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": ZOHO_CLIENT_ID,
            "client_secret": ZOHO_CLIENT_SECRET,
            "refresh_token": ZOHO_REFRESH_TOKEN
        }
        async with session.post(url, data=data) as response:
            result = await response.json()
            token = result["access_token"]

        # Fetch first contact with full details
        url = f"https://www.zohoapis.com/books/v3/contacts"
        headers = {"Authorization": f"Zoho-oauthtoken {token}"}
        params = {"organization_id": ZOHO_ORGANIZATION_ID, "page": 1, "per_page": 3}

        async with session.get(url, headers=headers, params=params) as response:
            result = await response.json()
            contacts = result.get("contacts", [])

            print("Sample Zoho Contact Structure:")
            print("=" * 80)
            for i, contact in enumerate(contacts[:3]):
                print(f"\nContact {i+1}:")
                print(json.dumps(contact, indent=2, ensure_ascii=False))
                print("-" * 80)

            # Check for owner_id specifically
            print("\nOwner ID Check:")
            for contact in contacts:
                print(f"  - {contact.get('contact_name')}: owner_id = {contact.get('owner_id', 'NOT PRESENT')}")


if __name__ == "__main__":
    asyncio.run(main())
