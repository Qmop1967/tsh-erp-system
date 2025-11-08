#!/usr/bin/env python3
"""
TDS Statistics & Comparison Runner
===================================

Run comprehensive statistics collection and comparison between Zoho and TSH ERP.

Usage:
    python run_tds_statistics.py
    python run_tds_statistics.py --entities items customers
    python run_tds_statistics.py --auto-sync
    python run_tds_statistics.py --dry-run

أداة تشغيل إحصائيات ومقارنة TDS
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.tds.statistics.engine import StatisticsEngine
from app.tds.statistics.models import EntityType


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="TDS Statistics & Comparison System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full comparison
  python run_tds_statistics.py

  # Compare specific entities only
  python run_tds_statistics.py --entities items customers

  # Auto-sync differences
  python run_tds_statistics.py --auto-sync

  # Dry run (show what would be synced)
  python run_tds_statistics.py --auto-sync --dry-run

  # Save report to file
  python run_tds_statistics.py --output report.json
        """
    )

    parser.add_argument(
        '--entities',
        nargs='+',
        choices=['items', 'customers', 'vendors', 'price_lists', 'stock', 'images'],
        help='Specific entities to compare (default: all)'
    )

    parser.add_argument(
        '--auto-sync',
        action='store_true',
        help='Automatically sync differences found'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode (show what would be synced without syncing)'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Save report to JSON file'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Quiet mode (less output)'
    )

    return parser.parse_args()


async def main():
    """Main execution function"""

    # Parse arguments
    args = parse_args()

    # Create database session
    db = SessionLocal()

    try:
        # Print header (unless quiet)
        if not args.quiet:
            print("\n" + "="*80)
            print("🚀 TDS Statistics & Comparison System")
            print("="*80 + "\n")

        # Initialize statistics engine
        if not args.quiet:
            print("📊 Initializing TDS Statistics Engine...")

        engine = StatisticsEngine(db=db)

        # Parse entities if specified
        entities = None
        if args.entities:
            entities = [EntityType(e.upper()) for e in args.entities]
            if not args.quiet:
                print(f"   Comparing entities: {', '.join(args.entities)}")

        # Run comparison
        if not args.quiet:
            print("\n📈 Starting statistics collection and comparison...")
            print("   (This may take 20-30 seconds...)\n")

        report = await engine.collect_and_compare(entities=entities)

        # Save report if requested
        if args.output:
            import json
            from dataclasses import asdict

            output_file = args.output
            with open(output_file, 'w') as f:
                # Convert report to dict (simplified)
                report_data = {
                    'report_id': report.report_id,
                    'timestamp': report.timestamp.isoformat(),
                    'overall_match_percentage': report.overall_match_percentage,
                    'health_score': report.health_score.overall_score,
                    'status': report.health_score.status,
                    'execution_time_seconds': report.execution_time_seconds,
                    'comparisons': {
                        entity_type: {
                            'zoho_count': comp.zoho_count,
                            'local_count': comp.local_count,
                            'difference': comp.difference,
                            'match_percentage': comp.match_percentage,
                            'requires_sync': comp.requires_sync,
                        }
                        for entity_type, comp in report.comparisons.items()
                    },
                    'alerts': report.alerts,
                    'recommendations': report.sync_recommendations,
                }
                json.dump(report_data, f, indent=2)

            print(f"\n💾 Report saved to: {output_file}")

        # Auto-sync if requested
        if args.auto_sync:
            print("\n" + "="*80)
            print("🔄 AUTO-SYNC MODE")
            print("="*80 + "\n")

            if args.dry_run:
                print("🔍 DRY RUN - No actual changes will be made\n")

            if report.requires_immediate_attention:
                print("⚠️  Critical issues detected. Starting auto-sync...\n")
                await engine.auto_sync_differences(report, dry_run=args.dry_run)
            else:
                print("✅ No sync required. All systems healthy!\n")

        # Final summary
        if not args.quiet:
            print("\n" + "="*80)
            print("✅ TDS Statistics Complete!")
            print("="*80)
            print(f"\n📊 Overall Match: {report.overall_match_percentage:.1f}%")
            print(f"🏥 Health Score: {report.health_score.overall_score:.1f}/100 ({report.health_score.status.upper()})")

            if report.requires_immediate_attention:
                print("\n⚠️  ATTENTION REQUIRED:")
                for issue in report.critical_issues:
                    print(f"   - {issue}")

                if not args.auto_sync:
                    print("\n💡 TIP: Run with --auto-sync to automatically sync differences")

            print("\n" + "="*80 + "\n")

        # Return exit code based on health
        if report.health_score.overall_score < 80:
            return 1  # Critical issues
        elif report.health_score.overall_score < 90:
            return 2  # Warning
        else:
            return 0  # Healthy

    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        return 130

    except Exception as e:
        print(f"\n\n❌ Error: {e}", file=sys.stderr)
        if not args.quiet:
            import traceback
            traceback.print_exc()
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    # Run async main
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
