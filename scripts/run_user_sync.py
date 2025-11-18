#!/usr/bin/env python3
"""
Standalone script to run Zoho user and customer sync operations.
This bypasses the need for a running FastAPI server.

Usage:
    python3 scripts/run_user_sync.py [--full-sync] [--resync-all]
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse, unquote
from dotenv import load_dotenv
from app.tds.integrations.zoho.client import UnifiedZohoClient
from app.tds.integrations.zoho.auth import ZohoAuthManager, ZohoCredentials
from app.tds.integrations.zoho.user_customer_sync import UserCustomerSyncService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get DATABASE_URL from .env
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tsh_app_user:changeme123@localhost:5432/tsh_erp_production")

# Replace Docker host with localhost for local development
DATABASE_URL = DATABASE_URL.replace('tsh_postgres', 'localhost')
logger.info(f"Using database: {DATABASE_URL.split('@')[1]}")  # Log host only for security

# Parse database URL to handle special characters in password
def parse_database_url(url: str) -> URL:
    """Parse DATABASE_URL and properly decode URL-encoded components."""
    parsed = urlparse(url)
    username = unquote(parsed.username) if parsed.username else None
    password = unquote(parsed.password) if parsed.password else None

    return URL.create(
        drivername=parsed.scheme,
        username=username,
        password=password,
        host=parsed.hostname,
        port=parsed.port,
        database=parsed.path.lstrip('/')
    )

# Create synchronous database engine
db_url = parse_database_url(DATABASE_URL)
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Get Zoho credentials from environment
ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
ZOHO_REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN")
ZOHO_ORGANIZATION_ID = os.getenv("ZOHO_ORGANIZATION_ID")


async def run_user_sync(full_sync: bool = False):
    """Run user sync from Zoho Books"""
    logger.info("=" * 80)
    logger.info(f"Starting User Sync (full_sync={full_sync})")
    logger.info("=" * 80)

    db = SessionLocal()
    try:
        # Create Zoho credentials
        credentials = ZohoCredentials(
            client_id=ZOHO_CLIENT_ID,
            client_secret=ZOHO_CLIENT_SECRET,
            refresh_token=ZOHO_REFRESH_TOKEN,
            organization_id=ZOHO_ORGANIZATION_ID
        )

        # Create Zoho auth manager
        auth_manager = ZohoAuthManager(credentials=credentials)

        # Create Zoho client
        zoho_client = UnifiedZohoClient(
            auth_manager=auth_manager,
            organization_id=ZOHO_ORGANIZATION_ID
        )

        # Create sync service
        sync_service = UserCustomerSyncService(db, zoho_client)

        # Run sync
        result = await sync_service.sync_users_from_zoho(full_sync=full_sync)

        logger.info("")
        logger.info("=" * 80)
        logger.info("USER SYNC RESULTS:")
        logger.info("=" * 80)
        logger.info(f"Total Fetched: {result.get('total_fetched', 0)}")
        logger.info(f"Created: {result.get('created', 0)}")
        logger.info(f"Updated: {result.get('updated', 0)}")
        logger.info(f"Skipped: {result.get('skipped', 0)}")
        logger.info(f"Errors: {len(result.get('errors', []))}")

        if result.get('errors'):
            logger.error("Errors encountered:")
            for error in result['errors']:
                logger.error(f"  - {error}")

        logger.info("=" * 80)
        return result

    except Exception as e:
        logger.error(f"User sync failed: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


async def run_customer_assignment(resync_all: bool = False):
    """Run customer-salesperson assignment"""
    logger.info("")
    logger.info("=" * 80)
    logger.info(f"Starting Customer Assignment Update (resync_all={resync_all})")
    logger.info("=" * 80)

    db = SessionLocal()
    try:
        # Create Zoho credentials
        credentials = ZohoCredentials(
            client_id=ZOHO_CLIENT_ID,
            client_secret=ZOHO_CLIENT_SECRET,
            refresh_token=ZOHO_REFRESH_TOKEN,
            organization_id=ZOHO_ORGANIZATION_ID
        )

        # Create Zoho auth manager
        auth_manager = ZohoAuthManager(credentials=credentials)

        # Create Zoho client
        zoho_client = UnifiedZohoClient(
            auth_manager=auth_manager,
            organization_id=ZOHO_ORGANIZATION_ID
        )

        # Create sync service
        sync_service = UserCustomerSyncService(db, zoho_client)

        # Run update
        result = await sync_service.update_customer_salesperson_assignments(resync_all=resync_all)

        logger.info("")
        logger.info("=" * 80)
        logger.info("CUSTOMER ASSIGNMENT RESULTS:")
        logger.info("=" * 80)
        logger.info(f"Total Checked: {result.get('total_checked', 0)}")
        logger.info(f"Updated: {result.get('updated', 0)}")
        logger.info(f"Skipped: {result.get('skipped', 0)}")
        logger.info(f"Errors: {len(result.get('errors', []))}")

        if result.get('errors'):
            logger.error("Errors encountered:")
            for error in result['errors']:
                logger.error(f"  - {error}")

        logger.info("=" * 80)
        return result

    except Exception as e:
        logger.error(f"Customer assignment failed: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


async def verify_data():
    """Verify data population in database"""
    logger.info("")
    logger.info("=" * 80)
    logger.info("Verifying Data Population")
    logger.info("=" * 80)

    db = SessionLocal()
    try:
        from app.models.user import User
        from app.models.customer import Customer

        # Check users with zoho_user_id
        users_with_zoho = db.query(User).filter(User.zoho_user_id.isnot(None)).count()
        total_users = db.query(User).count()

        # Check customers with salesperson_id
        customers_with_salesperson = db.query(Customer).filter(Customer.salesperson_id.isnot(None)).count()
        customers_with_zoho_owner = db.query(Customer).filter(Customer.zoho_owner_id.isnot(None)).count()
        total_customers = db.query(Customer).count()

        logger.info(f"Users with Zoho ID: {users_with_zoho}/{total_users}")
        logger.info(f"Customers with Salesperson: {customers_with_salesperson}/{total_customers}")
        logger.info(f"Customers with Zoho Owner ID: {customers_with_zoho_owner}/{total_customers}")

        # Sample data
        logger.info("")
        logger.info("Sample Users:")
        sample_users = db.query(User).filter(User.zoho_user_id.isnot(None)).limit(5).all()
        for user in sample_users:
            logger.info(f"  - {user.name} ({user.email}) -> Zoho ID: {user.zoho_user_id}")

        logger.info("")
        logger.info("Sample Customers:")
        sample_customers = db.query(Customer).filter(
            Customer.salesperson_id.isnot(None)
        ).limit(5).all()
        for customer in sample_customers:
            logger.info(f"  - {customer.name} -> Salesperson ID: {customer.salesperson_id}, Zoho Owner: {customer.zoho_owner_id}")

        logger.info("=" * 80)

        return {
            "users_with_zoho": users_with_zoho,
            "total_users": total_users,
            "customers_with_salesperson": customers_with_salesperson,
            "customers_with_zoho_owner": customers_with_zoho_owner,
            "total_customers": total_customers
        }

    finally:
        db.close()


async def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description='Run Zoho user and customer sync')
    parser.add_argument('--full-sync', action='store_true', help='Run full user sync')
    parser.add_argument('--resync-all', action='store_true', help='Resync all customer assignments')
    parser.add_argument('--skip-user-sync', action='store_true', help='Skip user sync')
    parser.add_argument('--skip-customer-assignment', action='store_true', help='Skip customer assignment')

    args = parser.parse_args()

    start_time = datetime.now()

    logger.info("")
    logger.info("#" * 80)
    logger.info("ZOHO USER AND CUSTOMER SYNC SCRIPT")
    logger.info(f"Started at: {start_time.isoformat()}")
    logger.info("#" * 80)

    try:
        # Step 1: User Sync
        if not args.skip_user_sync:
            user_result = await run_user_sync(full_sync=args.full_sync)
        else:
            logger.info("Skipping user sync")
            user_result = None

        # Step 2: Customer Assignment
        if not args.skip_customer_assignment:
            customer_result = await run_customer_assignment(resync_all=args.resync_all)
        else:
            logger.info("Skipping customer assignment")
            customer_result = None

        # Step 3: Verification
        verification = await verify_data()

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

        if user_result:
            logger.info("User Sync:")
            logger.info(f"  - Fetched: {user_result.get('total_fetched', 0)}")
            logger.info(f"  - Created: {user_result.get('created', 0)}")
            logger.info(f"  - Updated: {user_result.get('updated', 0)}")
            logger.info(f"  - Errors: {len(user_result.get('errors', []))}")

        if customer_result:
            logger.info("")
            logger.info("Customer Assignment:")
            logger.info(f"  - Checked: {customer_result.get('total_checked', 0)}")
            logger.info(f"  - Updated: {customer_result.get('updated', 0)}")
            logger.info(f"  - Errors: {len(customer_result.get('errors', []))}")

        logger.info("")
        logger.info("Database Verification:")
        logger.info(f"  - Users with Zoho ID: {verification['users_with_zoho']}/{verification['total_users']}")
        logger.info(f"  - Customers with Salesperson: {verification['customers_with_salesperson']}/{verification['total_customers']}")
        logger.info(f"  - Customers with Zoho Owner: {verification['customers_with_zoho_owner']}/{verification['total_customers']}")

        logger.info("#" * 80)
        logger.info("SUCCESS! Sync completed successfully.")
        logger.info("#" * 80)

    except Exception as e:
        logger.error(f"Sync failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
