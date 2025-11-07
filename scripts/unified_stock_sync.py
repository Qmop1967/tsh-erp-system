#!/usr/bin/env python3
"""
Unified Stock Sync CLI
======================

Single unified command-line interface for all stock sync operations.
Replaces: sync_zoho_stock.py, tds_sync_stock.py, sync_stock_from_zoho_inventory.py

استخدام CLI موحد لمزامنة المخزون

Usage:
    # Full sync
    python scripts/unified_stock_sync.py --mode full

    # Incremental sync
    python scripts/unified_stock_sync.py --mode incremental

    # Specific items
    python scripts/unified_stock_sync.py --items item_123,item_456

    # Low stock items
    python scripts/unified_stock_sync.py --low-stock --threshold 10

    # Specific warehouse
    python scripts/unified_stock_sync.py --warehouse warehouse_id

    # Show statistics
    python scripts/unified_stock_sync.py --stats

Author: TSH ERP Team
Date: November 6, 2025
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.tds.integrations.zoho import (
    UnifiedZohoClient,
    ZohoAuthManager,
    ZohoSyncOrchestrator,
    ZohoCredentials,
    SyncMode
)
from app.tds.integrations.zoho.stock_sync import (
    UnifiedStockSyncService,
    StockSyncConfig
)
from app.core.event_bus import EventBus


class Colors:
    """Terminal colors"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(message: str):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.END}\n")


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")


async def setup_services():
    """
    Setup and initialize all required services

    Returns:
        tuple: (zoho_client, orchestrator, stock_sync_service)
    """
    print_info("Initializing services...")

    # Load credentials from environment
    credentials = ZohoCredentials(
        client_id=os.getenv('ZOHO_CLIENT_ID'),
        client_secret=os.getenv('ZOHO_CLIENT_SECRET'),
        refresh_token=os.getenv('ZOHO_REFRESH_TOKEN'),
        organization_id=os.getenv('ZOHO_ORGANIZATION_ID')
    )

    # Validate credentials
    if not all([credentials.client_id, credentials.client_secret,
                credentials.refresh_token, credentials.organization_id]):
        print_error("Missing Zoho credentials in environment variables")
        print_info("Required: ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, ZOHO_REFRESH_TOKEN, ZOHO_ORGANIZATION_ID")
        sys.exit(1)

    # Create event bus
    event_bus = EventBus()

    # Create auth manager
    auth_manager = ZohoAuthManager(credentials, auto_refresh=True, event_bus=event_bus)
    await auth_manager.start()
    print_success("Authentication initialized")

    # Create Zoho client
    zoho_client = UnifiedZohoClient(
        auth_manager=auth_manager,
        organization_id=credentials.organization_id,
        rate_limit=100,
        event_bus=event_bus
    )
    await zoho_client.start_session()
    print_success("Zoho client connected")

    # Create sync orchestrator
    orchestrator = ZohoSyncOrchestrator(
        zoho_client=zoho_client,
        event_bus=event_bus
    )
    print_success("Sync orchestrator ready")

    # Create stock sync service
    stock_sync = UnifiedStockSyncService(
        zoho_client=zoho_client,
        sync_orchestrator=orchestrator,
        event_bus=event_bus
    )
    print_success("Stock sync service ready")

    return zoho_client, orchestrator, stock_sync


async def sync_full_stock(stock_sync: UnifiedStockSyncService, args):
    """Execute full stock sync"""
    print_header("Full Stock Sync")

    config = StockSyncConfig(
        batch_size=args.batch_size,
        active_only=args.active_only,
        with_stock_only=args.with_stock_only,
        sync_mode=SyncMode.FULL
    )

    result = await stock_sync.sync_all_stock(config)

    print_success(f"Sync completed successfully")
    print_stats(result, stock_sync)


async def sync_incremental_stock(stock_sync: UnifiedStockSyncService, args):
    """Execute incremental stock sync"""
    print_header("Incremental Stock Sync")

    config = StockSyncConfig(
        batch_size=args.batch_size,
        active_only=args.active_only,
        sync_mode=SyncMode.INCREMENTAL
    )

    result = await stock_sync.sync_all_stock(config)

    print_success(f"Incremental sync completed")
    print_stats(result, stock_sync)


async def sync_specific_items(stock_sync: UnifiedStockSyncService, args):
    """Sync specific items by ID"""
    print_header("Specific Items Sync")

    item_ids = args.items.split(',')
    print_info(f"Syncing {len(item_ids)} items: {', '.join(item_ids)}")

    config = StockSyncConfig(batch_size=args.batch_size)

    result = await stock_sync.sync_specific_items(item_ids, config)

    print_success(f"Specific items sync completed")
    print_stats(result, stock_sync)


async def sync_low_stock(stock_sync: UnifiedStockSyncService, args):
    """Sync low stock items"""
    print_header(f"Low Stock Sync (threshold: {args.threshold})")

    config = StockSyncConfig(batch_size=args.batch_size)

    result = await stock_sync.sync_low_stock_items(
        threshold=args.threshold,
        config=config
    )

    print_success(f"Low stock sync completed")
    print_stats(result, stock_sync)


async def sync_warehouse(stock_sync: UnifiedStockSyncService, args):
    """Sync specific warehouse stock"""
    print_header(f"Warehouse Stock Sync: {args.warehouse}")

    config = StockSyncConfig(batch_size=args.batch_size)

    result = await stock_sync.sync_warehouse_stock(args.warehouse, config)

    print_success(f"Warehouse sync completed")
    print(f"\n  Warehouse ID: {result['warehouse_id']}")
    print(f"  Total Items: {result['total_items']}")
    print(f"  Updated: {Colors.GREEN}{result['updated']}{Colors.END}")
    print(f"  Failed: {Colors.RED}{result['failed']}{Colors.END}")


async def show_summary(stock_sync: UnifiedStockSyncService):
    """Show stock summary"""
    print_header("Stock Summary")

    summary = await stock_sync.get_stock_summary()

    if 'error' in summary:
        print_error(f"Failed to get summary: {summary['error']}")
    else:
        print(f"\n  Total Items: {Colors.BOLD}{summary['total_items']}{Colors.END}")
        print(f"  Has More Pages: {summary['has_more_pages']}")
        print(f"  Fetched At: {summary['fetched_at']}")


def print_stats(result, stock_sync: UnifiedStockSyncService):
    """Print sync statistics"""
    print(f"\n{Colors.BOLD}Sync Results:{Colors.END}")
    print(f"  Total Processed: {result.total_processed}")
    print(f"  Successful: {Colors.GREEN}{result.total_success}{Colors.END}")
    print(f"  Failed: {Colors.RED}{result.total_failed}{Colors.END}")
    print(f"  Skipped: {result.total_skipped}")

    if result.duration:
        print(f"  Duration: {result.duration}")

    print(f"  Success Rate: {Colors.GREEN}{result.success_rate:.2f}%{Colors.END}")

    # Additional stats from service
    stats = stock_sync.get_statistics()
    if 'items_per_second' in stats:
        print(f"  Speed: {stats['items_per_second']:.2f} items/sec")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Unified Stock Sync CLI - TSH ERP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Full sync:            python scripts/unified_stock_sync.py --mode full
  Incremental sync:     python scripts/unified_stock_sync.py --mode incremental
  Specific items:       python scripts/unified_stock_sync.py --items item_123,item_456
  Low stock:            python scripts/unified_stock_sync.py --low-stock --threshold 10
  Warehouse:            python scripts/unified_stock_sync.py --warehouse wh_123
  Summary:              python scripts/unified_stock_sync.py --summary
        """
    )

    # Sync mode
    parser.add_argument(
        '--mode',
        choices=['full', 'incremental'],
        help='Sync mode (full or incremental)'
    )

    # Specific items
    parser.add_argument(
        '--items',
        help='Comma-separated list of item IDs to sync'
    )

    # Low stock
    parser.add_argument(
        '--low-stock',
        action='store_true',
        help='Sync only low stock items'
    )

    parser.add_argument(
        '--threshold',
        type=int,
        default=10,
        help='Stock threshold for low stock sync (default: 10)'
    )

    # Warehouse
    parser.add_argument(
        '--warehouse',
        help='Sync specific warehouse by ID'
    )

    # Summary
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show stock summary'
    )

    # Options
    parser.add_argument(
        '--batch-size',
        type=int,
        default=200,
        help='Batch size for API calls (default: 200)'
    )

    parser.add_argument(
        '--active-only',
        action='store_true',
        default=True,
        help='Sync only active items (default: True)'
    )

    parser.add_argument(
        '--with-stock-only',
        action='store_true',
        help='Sync only items with stock > 0'
    )

    args = parser.parse_args()

    # Validate arguments
    if not any([args.mode, args.items, args.low_stock, args.warehouse, args.summary]):
        parser.print_help()
        sys.exit(1)

    try:
        # Setup services
        zoho_client, orchestrator, stock_sync = await setup_services()

        # Execute requested operation
        if args.summary:
            await show_summary(stock_sync)

        elif args.mode == 'full':
            await sync_full_stock(stock_sync, args)

        elif args.mode == 'incremental':
            await sync_incremental_stock(stock_sync, args)

        elif args.items:
            await sync_specific_items(stock_sync, args)

        elif args.low_stock:
            await sync_low_stock(stock_sync, args)

        elif args.warehouse:
            await sync_warehouse(stock_sync, args)

        # Cleanup
        await zoho_client.close_session()
        print_success("\nAll operations completed successfully")

    except KeyboardInterrupt:
        print_warning("\n\nOperation cancelled by user")
        sys.exit(1)

    except Exception as e:
        print_error(f"\n\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
