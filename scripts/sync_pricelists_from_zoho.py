#!/usr/bin/env python3
"""
Sync Price Lists from Zoho Books
=================================

Fetches all price lists from Zoho Books API and syncs them to TSH ERP database.

This script follows TDS architecture principles:
- Uses UnifiedZohoClient for API calls
- Uses PriceListProcessor for data transformation
- Implements proper error handling and logging
- Follows Books API priority (Books first, Inventory fallback)

TSH Multi-Price System (6 Price Lists):
- Wholesale A (USD)
- Wholesale B (USD)
- Retailer (USD)
- Technical IQD (IQD)
- Technical USD (USD)
- Consumer IQD (IQD)

Usage:
    python scripts/sync_pricelists_from_zoho.py

Author: Claude Code (Senior Software Engineer AI)
Date: November 7, 2025
Version: 1.0.0
"""

import asyncio
import sys
import os
import logging
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

# TDS Components
from app.tds.integrations.zoho.client import UnifiedZohoClient, ZohoAPI
from app.tds.integrations.zoho.auth import ZohoAuthManager, ZohoCredentials
from app.tds.integrations.zoho.processors.pricelists import PriceListProcessor, batch_transform_pricelists

# Database
from app.db.database import get_async_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/pricelist_sync.log')
    ]
)
logger = logging.getLogger(__name__)


class PriceListSyncService:
    """
    Price List Sync Service
    خدمة مزامنة قوائم الأسعار

    Handles syncing price lists from Zoho Books to TSH ERP.
    """

    def __init__(self, zoho_client: UnifiedZohoClient, db: AsyncSession):
        """
        Initialize sync service.

        Args:
            zoho_client: Zoho API client
            db: Database session
        """
        self.zoho_client = zoho_client
        self.db = db
        self.processor = PriceListProcessor()
        self.stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }

    async def fetch_pricelists_from_zoho(self) -> List[Dict[str, Any]]:
        """
        Fetch all price lists from Zoho Books API.

        Returns:
            list: List of price list data from Zoho

        Raises:
            ZohoAPIError: If API call fails
        """
        logger.info("📘 Fetching price lists from Zoho Books...")

        try:
            # Zoho Books API endpoint for price books (price lists)
            response = await self.zoho_client.get(
                api_type=ZohoAPI.BOOKS,
                endpoint="pricebooks",
                params={
                    "per_page": 200,  # Max allowed
                    "page": 1
                }
            )

            pricelists = response.get('pricebooks', [])
            logger.info(f"✅ Found {len(pricelists)} price lists in Zoho Books")

            return pricelists

        except Exception as e:
            logger.error(f"❌ Failed to fetch price lists from Zoho: {e}", exc_info=True)
            raise

    async def save_pricelist(self, pricelist_data: Dict[str, Any]) -> bool:
        """
        Save or update a single price list in database.

        Args:
            pricelist_data: Transformed price list data

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            zoho_id = pricelist_data['zoho_price_list_id']
            code = pricelist_data['code']

            # Check if price list exists
            check_query = text("""
                SELECT id FROM price_lists
                WHERE zoho_price_list_id = :zoho_id
            """)

            result = await self.db.execute(check_query, {"zoho_id": zoho_id})
            existing = result.fetchone()

            if existing:
                # Update existing
                update_query = text("""
                    UPDATE price_lists
                    SET
                        code = :code,
                        name_en = :name_en,
                        name_ar = :name_ar,
                        description_en = :description_en,
                        description_ar = :description_ar,
                        currency = :currency,
                        is_default = :is_default,
                        is_active = :is_active,
                        zoho_last_sync = :zoho_last_sync,
                        updated_at = :updated_at
                    WHERE zoho_price_list_id = :zoho_id
                """)

                await self.db.execute(update_query, {
                    "code": code,
                    "name_en": pricelist_data['name_en'],
                    "name_ar": pricelist_data['name_ar'],
                    "description_en": pricelist_data['description_en'],
                    "description_ar": pricelist_data['description_ar'],
                    "currency": pricelist_data['currency'],
                    "is_default": pricelist_data['is_default'],
                    "is_active": pricelist_data['is_active'],
                    "zoho_last_sync": pricelist_data['zoho_last_sync'],
                    "updated_at": pricelist_data['updated_at'],
                    "zoho_id": zoho_id
                })

                logger.info(f"✅ Updated price list: {pricelist_data['name_en']} ({code})")

            else:
                # Insert new
                insert_query = text("""
                    INSERT INTO price_lists (
                        code, name_en, name_ar, description_en, description_ar,
                        currency, is_default, is_active, zoho_price_list_id,
                        zoho_last_sync, created_at, updated_at
                    ) VALUES (
                        :code, :name_en, :name_ar, :description_en, :description_ar,
                        :currency, :is_default, :is_active, :zoho_id,
                        :zoho_last_sync, :created_at, :updated_at
                    )
                """)

                await self.db.execute(insert_query, {
                    "code": code,
                    "name_en": pricelist_data['name_en'],
                    "name_ar": pricelist_data['name_ar'],
                    "description_en": pricelist_data['description_en'],
                    "description_ar": pricelist_data['description_ar'],
                    "currency": pricelist_data['currency'],
                    "is_default": pricelist_data['is_default'],
                    "is_active": pricelist_data['is_active'],
                    "zoho_id": zoho_id,
                    "zoho_last_sync": datetime.utcnow(),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })

                logger.info(f"✅ Created new price list: {pricelist_data['name_en']} ({code})")

            await self.db.commit()
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save price list {pricelist_data.get('name_en', 'Unknown')}: {e}", exc_info=True)
            await self.db.rollback()
            return False

    async def sync_all_pricelists(self) -> Dict[str, Any]:
        """
        Sync all price lists from Zoho Books to database.

        Returns:
            dict: Sync statistics
        """
        start_time = datetime.utcnow()
        logger.info("=" * 70)
        logger.info("🚀 Starting Price List Sync from Zoho Books")
        logger.info("=" * 70)

        try:
            # Step 1: Fetch from Zoho
            zoho_pricelists = await self.fetch_pricelists_from_zoho()
            self.stats['total'] = len(zoho_pricelists)

            if not zoho_pricelists:
                logger.warning("⚠️ No price lists found in Zoho Books")
                return self.stats

            # Step 2: Transform data
            logger.info("🔄 Transforming price list data...")
            transformed_pricelists = batch_transform_pricelists(zoho_pricelists)

            # Step 3: Save to database
            logger.info("💾 Saving price lists to database...")
            for pricelist in transformed_pricelists:
                success = await self.save_pricelist(pricelist)
                if success:
                    self.stats['successful'] += 1
                else:
                    self.stats['failed'] += 1

            # Calculate duration
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.stats['duration_seconds'] = duration

            # Log summary
            logger.info("=" * 70)
            logger.info("✅ Price List Sync Complete")
            logger.info(f"   Total: {self.stats['total']}")
            logger.info(f"   Successful: {self.stats['successful']}")
            logger.info(f"   Failed: {self.stats['failed']}")
            logger.info(f"   Duration: {duration:.2f} seconds")
            logger.info("=" * 70)

            return self.stats

        except Exception as e:
            logger.error(f"❌ Price list sync failed: {e}", exc_info=True)
            self.stats['errors'].append(str(e))
            raise


async def main():
    """
    Main entry point for price list sync script.
    """
    logger.info("📋 TSH ERP - Price List Sync from Zoho Books")
    logger.info(f"   Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize Zoho client
    zoho_client = None
    db_session = None

    try:
        # Get credentials from environment
        credentials = ZohoCredentials(
            client_id=os.getenv('ZOHO_CLIENT_ID'),
            client_secret=os.getenv('ZOHO_CLIENT_SECRET'),
            refresh_token=os.getenv('ZOHO_REFRESH_TOKEN'),
            organization_id=os.getenv('ZOHO_ORGANIZATION_ID')
        )

        # Initialize auth manager
        auth_manager = ZohoAuthManager(credentials)
        await auth_manager.start()

        # Initialize Zoho client
        zoho_client = UnifiedZohoClient(
            auth_manager=auth_manager,
            organization_id=credentials.organization_id,
            rate_limit=100  # Books API: 100 req/min
        )

        # Get database session
        async for db in get_async_db():
            db_session = db

            # Create sync service
            sync_service = PriceListSyncService(zoho_client, db_session)

            # Execute sync
            stats = await sync_service.sync_all_pricelists()

            # Print final stats
            print("\n" + "=" * 70)
            print("📊 SYNC STATISTICS")
            print("=" * 70)
            print(f"Total Price Lists: {stats['total']}")
            print(f"Successfully Synced: {stats['successful']}")
            print(f"Failed: {stats['failed']}")
            print(f"Duration: {stats.get('duration_seconds', 0):.2f} seconds")
            print("=" * 70)

            break  # Exit after first iteration

    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)

    finally:
        # Cleanup
        if zoho_client:
            await zoho_client.close_session()
        if db_session:
            await db_session.close()


if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

    # Run the sync
    asyncio.run(main())
