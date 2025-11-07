#!/usr/bin/env python3
"""
Zoho Stock Sync Script
Syncs item stock quantities from Zoho Inventory using optimized pagination

Usage:
    python3 scripts/sync_zoho_stock.py                    # Sync all items
    python3 scripts/sync_zoho_stock.py --active-only      # Only active items
    python3 scripts/sync_zoho_stock.py --with-stock-only  # Only items with stock
    python3 scripts/sync_zoho_stock.py --stats            # Show current stats
"""
import asyncio
import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.database import AsyncSessionLocal
from app.services.zoho_stock_sync import ZohoStockSyncService


async def sync_stock(
    active_only: bool = True,
    with_stock_only: bool = False,
    batch_size: int = 200,
    db_batch_size: int = 100
):
    """
    Run stock sync from Zoho

    Args:
        active_only: Only sync active items
        with_stock_only: Only sync items with stock > 0
        batch_size: Items per Zoho API call (max 200)
        db_batch_size: Items per database batch
    """
    print("\n" + "=" * 70)
    print("  ZOHO STOCK SYNC - OPTIMIZED BATCH MODE")
    print("=" * 70)
    print(f"  Active Only:     {active_only}")
    print(f"  With Stock Only: {with_stock_only}")
    print(f"  Batch Size:      {batch_size} items/API call")
    print(f"  DB Batch Size:   {db_batch_size} items/batch")
    print("=" * 70)
    print()

    async with AsyncSessionLocal() as db:
        service = ZohoStockSyncService(db)

        try:
            # Run sync
            result = await service.sync_all_stock(
                batch_size=batch_size,
                active_only=active_only,
                with_stock_only=with_stock_only,
                db_batch_size=db_batch_size
            )

            if result["success"]:
                print("\n✅ SUCCESS!")
                print_sync_results(result)
            else:
                print(f"\n❌ FAILED: {result.get('error')}")
                if result.get("stats"):
                    print_sync_results(result)
                return 1

        except KeyboardInterrupt:
            print("\n\n⚠️  Sync interrupted by user")
            return 1
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return 1

    return 0


async def show_stats():
    """Show current sync statistics"""
    print("\n" + "=" * 70)
    print("  ZOHO STOCK SYNC - CURRENT STATISTICS")
    print("=" * 70)

    async with AsyncSessionLocal() as db:
        service = ZohoStockSyncService(db)

        try:
            stats = await service.get_sync_statistics()

            if "error" in stats:
                print(f"\n❌ Error getting stats: {stats['error']}")
                return 1

            print()
            print(f"  Total Products:        {stats['total_products']:,}")
            print(f"  With Zoho ID:          {stats['with_zoho_id']:,}")
            print(f"  With Stock:            {stats['with_stock']:,}")
            print(f"  Total Stock Quantity:  {stats['total_stock_quantity']:,}")
            print(f"  Last Sync:             {stats['last_sync_time'] or 'Never'}")
            print(f"  Stale Products:        {stats['stale_products']:,} (>24h old)")
            print()

            if stats['with_zoho_id'] > 0:
                coverage = (stats['with_stock'] / stats['with_zoho_id']) * 100
                print(f"  Stock Coverage:        {coverage:.1f}%")
                print()

            print("=" * 70)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return 1

    return 0


def print_sync_results(result: dict):
    """Pretty print sync results"""
    stats = result.get("stats", {})
    duration = result.get("duration_seconds", 0)

    print()
    print("  📊 SYNC RESULTS")
    print("  " + "-" * 66)
    print(f"  Total Items from Zoho: {stats.get('total_items_from_zoho', 0):,}")
    print(f"  API Calls Made:        {stats.get('api_calls_made', 0):,}")
    print()
    print(f"  Products Updated:      {stats.get('products_updated', 0):,}")
    print(f"  Products Created:      {stats.get('products_created', 0):,}")
    print(f"  Products Skipped:      {stats.get('products_skipped', 0):,}")
    print()
    print(f"  Errors:                {len(stats.get('errors', []))}")
    print(f"  Duration:              {duration:.2f} seconds")

    if stats.get('api_calls_made', 0) > 0:
        avg_items = stats.get('total_items_from_zoho', 0) / stats['api_calls_made']
        print(f"  Avg Items/API Call:    {avg_items:.1f}")

    if duration > 0:
        rate = stats.get('total_items_from_zoho', 0) / duration
        print(f"  Sync Rate:             {rate:.1f} items/second")

    print()

    # Show errors if any
    errors = stats.get('errors', [])
    if errors:
        print("  ⚠️  ERRORS:")
        for i, error in enumerate(errors[:5], 1):  # Show first 5 errors
            print(f"     {i}. {error.get('item_id', 'Unknown')}: {error.get('error', 'Unknown error')}")
        if len(errors) > 5:
            print(f"     ... and {len(errors) - 5} more errors")
        print()

    print("=" * 70)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Sync item stock from Zoho Inventory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sync all active items
  python3 scripts/sync_zoho_stock.py

  # Sync only items with stock
  python3 scripts/sync_zoho_stock.py --with-stock-only

  # Show current statistics
  python3 scripts/sync_zoho_stock.py --stats

  # Custom batch size (for testing)
  python3 scripts/sync_zoho_stock.py --batch-size 50
        """
    )

    parser.add_argument(
        "--active-only",
        action="store_true",
        default=True,
        help="Only sync active items (default: True)"
    )

    parser.add_argument(
        "--all-items",
        action="store_true",
        help="Sync all items including inactive (overrides --active-only)"
    )

    parser.add_argument(
        "--with-stock-only",
        action="store_true",
        help="Only sync items with stock > 0"
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=200,
        help="Items per Zoho API call (default: 200, max: 200)"
    )

    parser.add_argument(
        "--db-batch-size",
        type=int,
        default=100,
        help="Items per database batch (default: 100)"
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show current sync statistics and exit"
    )

    args = parser.parse_args()

    # Validate batch size
    if args.batch_size > 200:
        print("⚠️  Warning: Zoho API max is 200 items per call. Using 200.")
        args.batch_size = 200

    # Show stats mode
    if args.stats:
        return asyncio.run(show_stats())

    # Run sync
    active_only = not args.all_items
    return asyncio.run(sync_stock(
        active_only=active_only,
        with_stock_only=args.with_stock_only,
        batch_size=args.batch_size,
        db_batch_size=args.db_batch_size
    ))


if __name__ == "__main__":
    sys.exit(main())
