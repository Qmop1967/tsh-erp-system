#!/usr/bin/env python3
"""
TDS Auto-Sync Scheduler
========================

Automatically runs TDS comparison and sync every 6 hours to ensure
Zoho and TSH ERP data stays synchronized.

Features:
- Runs comparison every 6 hours
- Auto-syncs differences when found
- Logs all operations
- Sends alerts on critical issues
- Can run as background daemon

Usage:
    # Run in foreground
    python tds_auto_sync_scheduler.py

    # Run as daemon (background)
    python tds_auto_sync_scheduler.py --daemon

    # Run once and exit (for cron)
    python tds_auto_sync_scheduler.py --once

    # Dry run mode (test without syncing)
    python tds_auto_sync_scheduler.py --dry-run

جدولة المزامنة التلقائية TDS
"""

import asyncio
import argparse
import sys
import os
import logging
import signal
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.tds.statistics.engine import StatisticsEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/tds_auto_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TDSAutoSyncScheduler:
    """
    TDS Auto-Sync Scheduler

    Runs comparison and auto-sync operations on a schedule
    """

    def __init__(self, interval_hours: int = 6, dry_run: bool = False):
        """
        Initialize scheduler

        Args:
            interval_hours: How often to run (default: 6 hours)
            dry_run: If True, simulate sync without making changes
        """
        self.interval_hours = interval_hours
        self.dry_run = dry_run
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        self.run_count = 0

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"\n⚠️  Received signal {signum}. Shutting down gracefully...")
        self.stop()
        sys.exit(0)

    async def run_comparison_and_sync(self):
        """
        Run comparison and auto-sync

        This is the main job that runs on schedule
        """
        self.run_count += 1

        logger.info("\n" + "="*80)
        logger.info(f"🚀 TDS AUTO-SYNC RUN #{self.run_count}")
        logger.info(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"🔄 Mode: {'DRY RUN' if self.dry_run else 'LIVE SYNC'}")
        logger.info("="*80 + "\n")

        db = SessionLocal()

        try:
            # Initialize statistics engine
            logger.info("📊 Initializing TDS Statistics Engine...")
            engine = StatisticsEngine(db=db)

            # Run comparison
            logger.info("📈 Running comparison (this may take 20-30 seconds)...\n")
            report = await engine.collect_and_compare()

            # Check if sync is needed
            if report.requires_immediate_attention:
                logger.info(f"\n⚠️  Issues detected! Health score: {report.health_score.overall_score:.1f}/100")
                logger.info(f"   Overall match: {report.overall_match_percentage:.1f}%")
                logger.info("\n🔄 Starting auto-sync...")

                # Run auto-sync
                sync_results = await engine.auto_sync_differences(
                    report,
                    dry_run=self.dry_run
                )

                # Log results
                success_count = sum(1 for r in sync_results.values() if r.get('success', False))
                total_count = len(sync_results)

                logger.info(f"\n✅ Auto-sync completed: {success_count}/{total_count} entities synced successfully")

                # Send alert if there were failures
                if success_count < total_count:
                    self._send_alert(
                        "TDS Auto-Sync Partial Failure",
                        f"Only {success_count}/{total_count} entities synced successfully. Check logs for details."
                    )
            else:
                logger.info(f"\n✅ All systems healthy!")
                logger.info(f"   Health score: {report.health_score.overall_score:.1f}/100")
                logger.info(f"   Overall match: {report.overall_match_percentage:.1f}%")
                logger.info(f"   No sync required.")

            # Save report summary
            self._save_run_summary(report, sync_results if report.requires_immediate_attention else None)

        except Exception as e:
            logger.error(f"\n❌ TDS auto-sync failed: {e}", exc_info=True)
            self._send_alert(
                "TDS Auto-Sync Failed",
                f"Error during auto-sync: {str(e)}"
            )

        finally:
            db.close()
            logger.info("\n" + "="*80)
            logger.info(f"✅ TDS AUTO-SYNC RUN #{self.run_count} COMPLETE")
            logger.info(f"⏭️  Next run in {self.interval_hours} hours")
            logger.info("="*80 + "\n")

    def _save_run_summary(self, report, sync_results: Optional[dict] = None):
        """Save run summary to file for monitoring"""
        try:
            summary_file = Path('logs/tds_auto_sync_summary.txt')
            summary_file.parent.mkdir(parents=True, exist_ok=True)

            with open(summary_file, 'a') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"Run #{self.run_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*80}\n")
                f.write(f"Health Score: {report.health_score.overall_score:.1f}/100 ({report.health_score.status})\n")
                f.write(f"Overall Match: {report.overall_match_percentage:.1f}%\n")
                f.write(f"Execution Time: {report.execution_time_seconds}s\n")

                if report.requires_immediate_attention:
                    f.write(f"\n⚠️  Issues Found:\n")
                    for issue in report.health_score.issues:
                        f.write(f"  - {issue}\n")

                    if sync_results:
                        f.write(f"\n🔄 Sync Results:\n")
                        for entity, result in sync_results.items():
                            if result.get('success'):
                                f.write(f"  ✅ {entity}: {result['synced_count']} synced\n")
                            else:
                                f.write(f"  ❌ {entity}: {result.get('error', 'Unknown error')}\n")
                else:
                    f.write(f"\n✅ All systems healthy - no sync needed\n")

                f.write(f"\n")

        except Exception as e:
            logger.error(f"Failed to save run summary: {e}")

    def _send_alert(self, subject: str, message: str):
        """
        Send alert notification

        TODO: Implement actual alert sending (email, Slack, etc.)
        """
        logger.warning(f"\n📧 ALERT: {subject}")
        logger.warning(f"   {message}\n")

        # TODO: Implement actual alert mechanism
        # - Send email
        # - Send Slack notification
        # - Create database alert record
        # - Send WhatsApp message

    def start(self):
        """Start the scheduler"""
        logger.info("\n" + "="*80)
        logger.info("🚀 TDS AUTO-SYNC SCHEDULER STARTING")
        logger.info("="*80)
        logger.info(f"   Interval: Every {self.interval_hours} hours")
        logger.info(f"   Mode: {'DRY RUN' if self.dry_run else 'LIVE SYNC'}")
        logger.info(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80 + "\n")

        # Add job to scheduler
        self.scheduler.add_job(
            self.run_comparison_and_sync,
            trigger=IntervalTrigger(hours=self.interval_hours),
            id='tds_auto_sync',
            name='TDS Auto-Sync Job',
            replace_existing=True,
            max_instances=1  # Prevent overlapping runs
        )

        # Run immediately on start
        logger.info("▶️  Running initial comparison and sync now...\n")
        self.scheduler.add_job(
            self.run_comparison_and_sync,
            id='initial_run',
            replace_existing=True
        )

        # Start scheduler
        self.scheduler.start()
        self.is_running = True

        logger.info("✅ Scheduler started successfully")
        logger.info(f"   Next scheduled run: {self.interval_hours} hours from now")
        logger.info("   Press Ctrl+C to stop\n")

    def stop(self):
        """Stop the scheduler"""
        if self.is_running:
            logger.info("\n⏹️  Stopping scheduler...")
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("✅ Scheduler stopped")

    async def run_once(self):
        """Run once and exit (for cron jobs)"""
        logger.info("▶️  Running in ONCE mode (will exit after completion)")
        await self.run_comparison_and_sync()


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="TDS Auto-Sync Scheduler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run scheduler (every 6 hours)
  python tds_auto_sync_scheduler.py

  # Run with custom interval
  python tds_auto_sync_scheduler.py --interval 12

  # Dry run mode (test without syncing)
  python tds_auto_sync_scheduler.py --dry-run

  # Run once and exit (for cron)
  python tds_auto_sync_scheduler.py --once

  # Run as daemon
  python tds_auto_sync_scheduler.py --daemon
        """
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=6,
        help='Run interval in hours (default: 6)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode (test without making changes)'
    )

    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (for cron jobs)'
    )

    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run as background daemon'
    )

    return parser.parse_args()


async def main():
    """Main execution function"""
    args = parse_args()

    # Create scheduler
    scheduler = TDSAutoSyncScheduler(
        interval_hours=args.interval,
        dry_run=args.dry_run
    )

    if args.once:
        # Run once and exit
        await scheduler.run_once()
        return 0

    # Start scheduler
    scheduler.start()

    # Keep running
    try:
        # Run forever
        while scheduler.is_running:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("\n⚠️  Received keyboard interrupt")

    finally:
        scheduler.stop()

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
