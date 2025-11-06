#!/usr/bin/env python3
"""
TDS Stock Sync Script
Syncs item stock from Zoho Books/Inventory to local database using pagination batch processing

Usage:
    python scripts/tds_sync_stock.py [options]

Options:
    --batch-size N          Number of items per Zoho API call (default: 200, max: 200)
    --db-batch-size N       Number of items per database batch (default: 100)
    --active-only           Only sync active items (default: True)
    --with-stock-only       Only sync items with stock > 0 (default: False)
    --dry-run               Show what would be synced without making changes
    --verbose               Enable verbose logging

Examples:
    # Full sync with default settings
    python scripts/tds_sync_stock.py

    # Sync only items with stock
    python scripts/tds_sync_stock.py --with-stock-only

    # Sync with custom batch sizes
    python scripts/tds_sync_stock.py --batch-size 100 --db-batch-size 50

    # Dry run to preview sync
    python scripts/tds_sync_stock.py --dry-run
"""
import asyncio
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.database import get_async_db
from app.services.zoho_stock_sync import ZohoStockSyncService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(project_root / 'logs' / f'tds_stock_sync_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger(__name__)


async def run_stock_sync(args):
    """
    Run stock sync with provided arguments

    Args:
        args: Parsed command line arguments
    """
    logger.info("=" * 80)
    logger.info("TDS STOCK SYNC - Pagination Batch Processing")
    logger.info("=" * 80)
    logger.info(f"Configuration:")
    logger.info(f"  Batch Size (Zoho API):  {args.batch_size}")
    logger.info(f"  DB Batch Size:          {args.db_batch_size}")
    logger.info(f"  Active Only:            {args.active_only}")
    logger.info(f"  With Stock Only:        {args.with_stock_only}")
    logger.info(f"  Dry Run:                {args.dry_run}")
    logger.info("=" * 80)

    if args.dry_run:
        logger.warning("DRY RUN MODE - No changes will be made to the database")
        logger.info("")

    # Get database session
    async for db in get_async_db():
        try:
            # Create sync service
            sync_service = ZohoStockSyncService(db)

            if args.dry_run:
                # In dry run, just get current stats
                logger.info("Fetching current database statistics...")
                stats = await sync_service.get_sync_statistics()

                logger.info("")
                logger.info("CURRENT DATABASE STATE:")
                logger.info(f"  Total Products:         {stats.get('total_products', 0)}")
                logger.info(f"  With Zoho ID:           {stats.get('with_zoho_id', 0)}")
                logger.info(f"  With Stock:             {stats.get('with_stock', 0)}")
                logger.info(f"  Total Stock Quantity:   {stats.get('total_stock_quantity', 0)}")
                logger.info(f"  Last Sync:              {stats.get('last_sync_time', 'Never')}")
                logger.info(f"  Stale Products:         {stats.get('stale_products', 0)}")
                logger.info("")
                logger.info("DRY RUN COMPLETE - Use without --dry-run to perform actual sync")

            else:
                # Run actual sync
                result = await sync_service.sync_all_stock(
                    batch_size=args.batch_size,
                    active_only=args.active_only,
                    with_stock_only=args.with_stock_only,
                    db_batch_size=args.db_batch_size
                )

                if result.get('success'):
                    logger.info("")
                    logger.info("=" * 80)
                    logger.info("SYNC COMPLETED SUCCESSFULLY")
                    logger.info("=" * 80)

                    stats = result.get('stats', {})
                    logger.info(f"Sync Run ID:            {result.get('sync_run_id')}")
                    logger.info(f"Duration:               {result.get('duration_seconds', 0):.2f}s")
                    logger.info(f"Items from Zoho:        {stats.get('total_items_from_zoho', 0)}")
                    logger.info(f"API Calls Made:         {stats.get('api_calls_made', 0)}")
                    logger.info(f"Products Updated:       {stats.get('products_updated', 0)}")
                    logger.info(f"Products Created:       {stats.get('products_created', 0)}")
                    logger.info(f"Products Skipped:       {stats.get('products_skipped', 0)}")
                    logger.info(f"Errors:                 {len(stats.get('errors', []))}")

                    if stats.get('errors'):
                        logger.warning("")
                        logger.warning("ERRORS ENCOUNTERED:")
                        for error in stats.get('errors', [])[:10]:  # Show first 10
                            logger.warning(f"  {error}")

                    logger.info("=" * 80)
                    return 0

                else:
                    logger.error("")
                    logger.error("=" * 80)
                    logger.error("SYNC FAILED")
                    logger.error("=" * 80)
                    logger.error(f"Error: {result.get('error')}")
                    logger.error("=" * 80)
                    return 1

        except Exception as e:
            logger.error(f"Unexpected error during sync: {e}", exc_info=True)
            return 1

        finally:
            await db.close()

    return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='TDS Stock Sync - Pagination Batch Processing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        default=200,
        help='Number of items per Zoho API call (max 200)'
    )

    parser.add_argument(
        '--db-batch-size',
        type=int,
        default=100,
        help='Number of items per database batch'
    )

    parser.add_argument(
        '--active-only',
        action='store_true',
        default=True,
        help='Only sync active items'
    )

    parser.add_argument(
        '--with-stock-only',
        action='store_true',
        default=False,
        help='Only sync items with stock > 0'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be synced without making changes'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Adjust logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate batch sizes
    if args.batch_size < 1 or args.batch_size > 200:
        logger.error("Batch size must be between 1 and 200")
        return 1

    if args.db_batch_size < 1:
        logger.error("DB batch size must be at least 1")
        return 1

    # Run sync
    try:
        exit_code = asyncio.run(run_stock_sync(args))
        sys.exit(exit_code)

    except KeyboardInterrupt:
        logger.warning("\nSync interrupted by user")
        sys.exit(130)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
