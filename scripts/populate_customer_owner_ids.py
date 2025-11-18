#!/usr/bin/env python3
"""
Populate Customer Owner IDs from Zoho Books Contacts
=====================================================

This script fetches contacts from Zoho Books and updates the customers table
with the zoho_owner_id field.

Usage:
    python3 scripts/populate_customer_owner_ids.py
"""

import sys
import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://khaleel:Zcbbm.97531tsh@localhost:5432/tsh_erp")
DATABASE_URL = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')

# Get Zoho credentials
ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
ZOHO_REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN")
ZOHO_ORGANIZATION_ID = os.getenv("ZOHO_ORGANIZATION_ID")

# Create database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def get_zoho_access_token() -> str:
    """Get a fresh access token from Zoho"""
    url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "refresh_token": ZOHO_REFRESH_TOKEN
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            result = await response.json()
            if "access_token" in result:
                return result["access_token"]
            else:
                raise Exception(f"Failed to get access token: {result}")


async def fetch_all_contacts(access_token: str) -> List[Dict]:
    """Fetch all contacts from Zoho Books with pagination"""
    all_contacts = []
    page = 1
    per_page = 200

    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}"
    }

    async with aiohttp.ClientSession() as session:
        while True:
            url = f"https://www.zohoapis.com/books/v3/contacts"
            params = {
                "organization_id": ZOHO_ORGANIZATION_ID,
                "page": page,
                "per_page": per_page
            }

            async with session.get(url, headers=headers, params=params) as response:
                result = await response.json()

                if "contacts" not in result:
                    logger.error(f"Failed to fetch contacts: {result}")
                    break

                contacts = result["contacts"]
                if not contacts:
                    break

                all_contacts.extend(contacts)
                logger.info(f"Fetched page {page}: {len(contacts)} contacts (total: {len(all_contacts)})")

                # Check if there are more pages
                if len(contacts) < per_page:
                    break

                page += 1

                # Rate limiting
                await asyncio.sleep(0.5)

    logger.info(f"Total contacts fetched from Zoho: {len(all_contacts)}")
    return all_contacts


async def update_customer_owner_ids(contacts: List[Dict]) -> Dict[str, int]:
    """Update customers with owner_id from Zoho contacts"""
    db = SessionLocal()
    result = {
        "updated": 0,
        "not_found": 0,
        "no_owner": 0,
        "errors": []
    }

    try:
        for contact in contacts:
            try:
                contact_id = str(contact.get("contact_id"))
                owner_id = contact.get("owner_id")
                contact_name = contact.get("contact_name", "Unknown")

                if not owner_id:
                    result["no_owner"] += 1
                    continue

                # Update customer with owner_id
                update_query = text("""
                    UPDATE customers
                    SET zoho_owner_id = :owner_id,
                        zoho_last_sync = :sync_time
                    WHERE zoho_contact_id = :contact_id
                """)
                update_result = db.execute(update_query, {
                    "owner_id": str(owner_id),
                    "contact_id": contact_id,
                    "sync_time": datetime.utcnow()
                })

                if update_result.rowcount > 0:
                    result["updated"] += 1
                    if result["updated"] % 100 == 0:
                        logger.info(f"Updated {result['updated']} customers...")
                else:
                    result["not_found"] += 1

            except Exception as e:
                logger.error(f"Error updating customer {contact_id}: {str(e)}")
                result["errors"].append({
                    "contact_id": contact_id,
                    "error": str(e)
                })
                db.rollback()

        db.commit()

    finally:
        db.close()

    return result


async def main():
    start_time = datetime.now()

    logger.info("")
    logger.info("#" * 80)
    logger.info("POPULATE CUSTOMER OWNER IDs FROM ZOHO CONTACTS")
    logger.info(f"Started at: {start_time.isoformat()}")
    logger.info("#" * 80)

    try:
        # Step 1: Get access token
        logger.info("Step 1: Obtaining Zoho access token...")
        access_token = await get_zoho_access_token()
        logger.info("Access token obtained successfully")

        # Step 2: Fetch all contacts
        logger.info("Step 2: Fetching all contacts from Zoho Books...")
        contacts = await fetch_all_contacts(access_token)

        # Step 3: Update customers with owner_ids
        logger.info("Step 3: Updating customer owner_ids...")
        result = await update_customer_owner_ids(contacts)

        # Report
        logger.info("")
        logger.info("=" * 80)
        logger.info("RESULTS:")
        logger.info("=" * 80)
        logger.info(f"Total Contacts Fetched: {len(contacts)}")
        logger.info(f"Customers Updated: {result['updated']}")
        logger.info(f"Contacts Without Owner: {result['no_owner']}")
        logger.info(f"Contacts Not Found in DB: {result['not_found']}")
        logger.info(f"Errors: {len(result['errors'])}")

        # Verify
        db = SessionLocal()
        verify_query = text("""
            SELECT
                COUNT(*) FILTER (WHERE zoho_owner_id IS NOT NULL) as with_owner,
                COUNT(*) as total
            FROM customers
        """)
        verify_result = db.execute(verify_query).fetchone()
        db.close()

        logger.info("")
        logger.info(f"Customers with Owner ID: {verify_result[0]}/{verify_result[1]}")
        logger.info("=" * 80)

        end_time = datetime.now()
        logger.info(f"Duration: {(end_time - start_time).total_seconds():.2f} seconds")
        logger.info("#" * 80)
        logger.info("SUCCESS!")
        logger.info("#" * 80)

    except Exception as e:
        logger.error(f"Failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
