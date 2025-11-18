#!/usr/bin/env python3
"""
Production-Compatible Zoho User Sync Script
============================================

This script is specifically designed to work with the ACTUAL production database schema.
It syncs users from Zoho Books and maps customer-salesperson relationships.

Usage:
    python3 scripts/run_user_sync_production.py [--full-sync]
"""

import sys
import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse, unquote
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
logger.info(f"Using database: {DATABASE_URL.split('@')[1]}")

# Get Zoho credentials from environment
ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
ZOHO_REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN")
ZOHO_ORGANIZATION_ID = os.getenv("ZOHO_ORGANIZATION_ID")

# Create database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def get_zoho_access_token() -> str:
    """Get a fresh access token from Zoho"""
    import aiohttp

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
                logger.info("Successfully obtained Zoho access token")
                return result["access_token"]
            else:
                raise Exception(f"Failed to get access token: {result}")


async def fetch_zoho_users(access_token: str) -> List[Dict]:
    """Fetch all users from Zoho Books"""
    import aiohttp

    url = f"https://www.zohoapis.com/books/v3/users"
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}"
    }
    params = {
        "organization_id": ZOHO_ORGANIZATION_ID
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            result = await response.json()
            if "users" in result:
                logger.info(f"Fetched {len(result['users'])} users from Zoho Books")
                return result["users"]
            else:
                logger.error(f"Failed to fetch users: {result}")
                return []


async def sync_users_to_database(zoho_users: List[Dict]) -> Dict[str, int]:
    """
    Sync Zoho users to the production database.

    Production schema for users table:
    - id: UUID (not integer)
    - email: text (required)
    - full_name: text (maps from Zoho 'name')
    - name: text (also stores name)
    - phone: text
    - zoho_user_id: varchar(100)
    - zoho_last_sync: timestamp
    - role_id: integer (FK to roles)
    - is_active: boolean
    """
    db = SessionLocal()
    result = {
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "errors": []
    }

    try:
        for zoho_user in zoho_users:
            try:
                zoho_user_id = str(zoho_user.get("user_id"))
                email = zoho_user.get("email", "").lower().strip()
                name = zoho_user.get("name", "")
                phone = zoho_user.get("phone") or zoho_user.get("mobile")
                is_active = zoho_user.get("status") == "active"

                if not email:
                    logger.warning(f"Skipping user without email: {zoho_user_id}")
                    result["skipped"] += 1
                    continue

                # Check if user exists (by zoho_user_id or email)
                check_query = text("""
                    SELECT id, email, zoho_user_id
                    FROM users
                    WHERE zoho_user_id = :zoho_id OR email = :email
                    LIMIT 1
                """)
                existing = db.execute(check_query, {
                    "zoho_id": zoho_user_id,
                    "email": email
                }).fetchone()

                if existing:
                    # Update existing user
                    update_query = text("""
                        UPDATE users
                        SET zoho_user_id = :zoho_id,
                            zoho_last_sync = :sync_time,
                            full_name = COALESCE(:name, full_name),
                            name = COALESCE(:name, name),
                            phone = COALESCE(:phone, phone),
                            is_active = :is_active
                        WHERE id = :user_id
                    """)
                    db.execute(update_query, {
                        "zoho_id": zoho_user_id,
                        "sync_time": datetime.utcnow(),
                        "name": name,
                        "phone": phone,
                        "is_active": is_active,
                        "user_id": existing[0]
                    })
                    db.commit()
                    result["updated"] += 1
                    logger.info(f"Updated user: {email} -> zoho_user_id: {zoho_user_id}")
                else:
                    # New user - skip creation (users are created through auth system)
                    logger.info(f"New Zoho user (not in TSH ERP): {email} - {zoho_user_id}")
                    result["skipped"] += 1

            except Exception as e:
                logger.error(f"Error processing user {zoho_user.get('user_id')}: {str(e)}")
                result["errors"].append({
                    "zoho_user_id": zoho_user.get("user_id"),
                    "error": str(e)
                })
                db.rollback()

    finally:
        db.close()

    return result


async def update_customer_salesperson_assignments() -> Dict[str, int]:
    """
    Update customer salesperson assignments based on zoho_owner_id.

    Production schema for customers table:
    - id: UUID
    - zoho_contact_id: text
    - zoho_owner_id: varchar(100)
    - salesperson_id: UUID (FK to users)
    - contact_name: text
    """
    db = SessionLocal()
    result = {
        "total_checked": 0,
        "updated": 0,
        "skipped": 0,
        "errors": []
    }

    try:
        # Get customers with zoho_owner_id but no salesperson_id
        customers_query = text("""
            SELECT c.id, c.contact_name, c.zoho_owner_id
            FROM customers c
            WHERE c.zoho_owner_id IS NOT NULL
        """)
        customers = db.execute(customers_query).fetchall()
        result["total_checked"] = len(customers)

        logger.info(f"Found {len(customers)} customers with Zoho owner_id")

        for customer in customers:
            try:
                customer_id = customer[0]
                contact_name = customer[1]
                zoho_owner_id = customer[2]

                # Find the TSH ERP user with this zoho_user_id
                user_query = text("""
                    SELECT id FROM users WHERE zoho_user_id = :zoho_id
                """)
                user = db.execute(user_query, {"zoho_id": zoho_owner_id}).fetchone()

                if user:
                    # Update customer's salesperson_id
                    update_query = text("""
                        UPDATE customers
                        SET salesperson_id = :user_id,
                            zoho_last_sync = :sync_time
                        WHERE id = :customer_id
                    """)
                    db.execute(update_query, {
                        "user_id": user[0],
                        "sync_time": datetime.utcnow(),
                        "customer_id": customer_id
                    })
                    db.commit()
                    result["updated"] += 1
                    logger.info(f"Assigned salesperson to customer: {contact_name}")
                else:
                    result["skipped"] += 1
                    logger.warning(f"No TSH user found for Zoho owner_id: {zoho_owner_id}")

            except Exception as e:
                logger.error(f"Error updating customer {customer_id}: {str(e)}")
                result["errors"].append({
                    "customer_id": str(customer_id),
                    "error": str(e)
                })
                db.rollback()

    finally:
        db.close()

    return result


async def verify_data() -> Dict[str, Any]:
    """Verify data population in database"""
    db = SessionLocal()
    try:
        # Check users with zoho_user_id
        users_query = text("""
            SELECT
                COUNT(*) FILTER (WHERE zoho_user_id IS NOT NULL) as users_with_zoho,
                COUNT(*) as total_users
            FROM users
        """)
        user_stats = db.execute(users_query).fetchone()

        # Check customers with salesperson_id
        customers_query = text("""
            SELECT
                COUNT(*) FILTER (WHERE salesperson_id IS NOT NULL) as customers_with_salesperson,
                COUNT(*) FILTER (WHERE zoho_owner_id IS NOT NULL) as customers_with_zoho_owner,
                COUNT(*) as total_customers
            FROM customers
        """)
        customer_stats = db.execute(customers_query).fetchone()

        # Sample data
        sample_users_query = text("""
            SELECT email, full_name, zoho_user_id
            FROM users
            WHERE zoho_user_id IS NOT NULL
            LIMIT 5
        """)
        sample_users = db.execute(sample_users_query).fetchall()

        sample_customers_query = text("""
            SELECT c.contact_name, c.salesperson_id, c.zoho_owner_id, u.email as salesperson_email
            FROM customers c
            LEFT JOIN users u ON c.salesperson_id = u.id
            WHERE c.salesperson_id IS NOT NULL
            LIMIT 5
        """)
        sample_customers = db.execute(sample_customers_query).fetchall()

        return {
            "users_with_zoho": user_stats[0],
            "total_users": user_stats[1],
            "customers_with_salesperson": customer_stats[0],
            "customers_with_zoho_owner": customer_stats[1],
            "total_customers": customer_stats[2],
            "sample_users": sample_users,
            "sample_customers": sample_customers
        }

    finally:
        db.close()


async def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description='Run Zoho user sync (production-compatible)')
    parser.add_argument('--full-sync', action='store_true', help='Run full user sync')
    args = parser.parse_args()

    start_time = datetime.now()

    logger.info("")
    logger.info("#" * 80)
    logger.info("ZOHO USER SYNC - PRODUCTION COMPATIBLE")
    logger.info(f"Started at: {start_time.isoformat()}")
    logger.info("#" * 80)

    try:
        # Step 1: Get Zoho access token
        logger.info("Step 1: Obtaining Zoho access token...")
        access_token = await get_zoho_access_token()

        # Step 2: Fetch users from Zoho
        logger.info("Step 2: Fetching users from Zoho Books...")
        zoho_users = await fetch_zoho_users(access_token)

        # Step 3: Sync users to database
        logger.info("Step 3: Syncing users to database...")
        user_result = await sync_users_to_database(zoho_users)

        logger.info("")
        logger.info("=" * 80)
        logger.info("USER SYNC RESULTS:")
        logger.info("=" * 80)
        logger.info(f"Total Fetched: {len(zoho_users)}")
        logger.info(f"Updated: {user_result['updated']}")
        logger.info(f"Skipped: {user_result['skipped']}")
        logger.info(f"Errors: {len(user_result['errors'])}")
        if user_result['errors']:
            for err in user_result['errors'][:5]:
                logger.error(f"  - {err}")
        logger.info("=" * 80)

        # Step 4: Update customer salesperson assignments
        logger.info("Step 4: Updating customer salesperson assignments...")
        customer_result = await update_customer_salesperson_assignments()

        logger.info("")
        logger.info("=" * 80)
        logger.info("CUSTOMER ASSIGNMENT RESULTS:")
        logger.info("=" * 80)
        logger.info(f"Total Checked: {customer_result['total_checked']}")
        logger.info(f"Updated: {customer_result['updated']}")
        logger.info(f"Skipped: {customer_result['skipped']}")
        logger.info(f"Errors: {len(customer_result['errors'])}")
        if customer_result['errors']:
            for err in customer_result['errors'][:5]:
                logger.error(f"  - {err}")
        logger.info("=" * 80)

        # Step 5: Verification
        logger.info("Step 5: Verifying data population...")
        verification = await verify_data()

        logger.info("")
        logger.info("=" * 80)
        logger.info("VERIFICATION RESULTS:")
        logger.info("=" * 80)
        logger.info(f"Users with Zoho ID: {verification['users_with_zoho']}/{verification['total_users']}")
        logger.info(f"Customers with Salesperson: {verification['customers_with_salesperson']}/{verification['total_customers']}")
        logger.info(f"Customers with Zoho Owner: {verification['customers_with_zoho_owner']}/{verification['total_customers']}")

        if verification['sample_users']:
            logger.info("")
            logger.info("Sample Users with Zoho ID:")
            for user in verification['sample_users']:
                logger.info(f"  - {user[1]} ({user[0]}) -> Zoho: {user[2]}")

        if verification['sample_customers']:
            logger.info("")
            logger.info("Sample Customers with Salesperson:")
            for customer in verification['sample_customers']:
                logger.info(f"  - {customer[0]} -> Salesperson: {customer[3] or 'N/A'}")

        logger.info("=" * 80)

        # Final Report
        end_time = datetime.now()
        duration = end_time - start_time

        logger.info("")
        logger.info("#" * 80)
        logger.info("FINAL REPORT")
        logger.info("#" * 80)
        logger.info(f"Started: {start_time.isoformat()}")
        logger.info(f"Completed: {end_time.isoformat()}")
        logger.info(f"Duration: {duration.total_seconds():.2f} seconds")
        logger.info("")
        logger.info(f"Users Synced: {user_result['updated']} updated, {user_result['skipped']} skipped")
        logger.info(f"Customers Assigned: {customer_result['updated']} updated")
        logger.info("#" * 80)
        logger.info("SUCCESS! Sync completed successfully.")
        logger.info("#" * 80)

    except Exception as e:
        logger.error(f"Sync failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
