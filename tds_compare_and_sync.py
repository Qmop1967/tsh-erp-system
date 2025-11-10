#!/usr/bin/env python3
"""
TDS Quick Compare & Sync
=========================

Simple command to compare Zoho vs TSH ERP and optionally sync differences.

Usage:
    # Just compare (no sync)
    python tds_compare_and_sync.py

    # Compare and auto-sync differences
    python tds_compare_and_sync.py --sync

    # Compare specific entities only
    python tds_compare_and_sync.py --entities items stock images price_lists

    # Dry run (see what would be synced)
    python tds_compare_and_sync.py --sync --dry-run

مقارنة ومزامنة سريعة TDS
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.db.database import SessionLocal
from app.tds.statistics.engine import StatisticsEngine
from app.tds.statistics.models import EntityType


async def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="TDS Quick Compare & Sync")
    parser.add_argument('--sync', action='store_true', help='Auto-sync differences')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no actual sync)')
    parser.add_argument(
        '--entities',
        nargs='+',
        choices=['items', 'customers', 'vendors', 'price_lists', 'stock', 'images'],
        help='Specific entities to compare'
    )
    args = parser.parse_args()

    db = SessionLocal()

    try:
        print("\n" + "="*80)
        print("🚀 TDS QUICK COMPARE & SYNC")
        print("="*80 + "\n")

        # Initialize engine
        print("📊 Initializing TDS Statistics Engine...")
        engine = StatisticsEngine(db=db)

        # Parse entities
        entities = None
        if args.entities:
            entities = [EntityType(e.upper()) for e in args.entities]
            print(f"   Comparing: {', '.join(args.entities)}\n")

        # Run comparison
        print("📈 Running comparison...\n")
        report = await engine.collect_and_compare(entities=entities)

        # Print quick summary
        print("\n" + "-"*80)
        print("📊 QUICK SUMMARY")
        print("-"*80)
        print(f"Health Score: {report.health_score.overall_score:.1f}/100 ({report.health_score.status.upper()})")
        print(f"Overall Match: {report.overall_match_percentage:.1f}%")
        print(f"\nComparisons:")

        for entity_type, comparison in report.comparisons.items():
            icon = "✅" if comparison.is_healthy else "⚠️"
            print(f"  {icon} {entity_type:15s} Zoho: {comparison.zoho_count:6,} | Local: {comparison.local_count:6,} | Diff: {comparison.difference:+6,} | Match: {comparison.match_percentage:5.1f}%")

        # Auto-sync if requested
        if args.sync:
            print("\n" + "-"*80)
            if args.dry_run:
                print("🔍 DRY RUN MODE - Showing what would be synced")
            else:
                print("🔄 AUTO-SYNC MODE - Syncing differences")
            print("-"*80 + "\n")

            if report.requires_immediate_attention:
                sync_results = await engine.auto_sync_differences(report, dry_run=args.dry_run)

                # Print sync summary
                print("\n" + "-"*80)
                print("🔄 SYNC RESULTS")
                print("-"*80)

                for entity, result in sync_results.items():
                    if result.get('dry_run'):
                        print(f"  🔍 {entity:15s} Would sync")
                    elif result.get('success'):
                        print(f"  ✅ {entity:15s} Synced: {result['synced_count']} | Failed: {result['failed_count']}")
                    else:
                        print(f"  ❌ {entity:15s} Error: {result.get('error', 'Unknown')}")
            else:
                print("✅ All systems healthy - no sync needed!")

        elif report.requires_immediate_attention:
            print("\n💡 TIP: Run with --sync to automatically fix differences")

        print("\n" + "="*80)
        print("✅ COMPLETE")
        print("="*80 + "\n")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
