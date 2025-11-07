"""
Zoho Token Refresh Scheduler
Automatically refreshes Zoho OAuth tokens to keep them active
and prevents token expiration issues
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from .zoho_token_manager import get_token_manager

logger = logging.getLogger(__name__)


class ZohoTokenRefreshScheduler:
    """
    Scheduler to automatically refresh Zoho OAuth tokens

    Features:
    - Automatic token refresh every 50 minutes (tokens expire in 60 minutes)
    - Health check monitoring
    - Prevents token expiration
    - Logs all refresh activities
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.token_manager = get_token_manager()
        self.last_refresh_time: Optional[datetime] = None
        self.refresh_count = 0
        self.failure_count = 0

    async def refresh_token(self):
        """Refresh the Zoho OAuth access token"""
        try:
            logger.info("🔄 Starting scheduled token refresh...")

            # Get fresh access token (this will auto-refresh if needed)
            headers = await self.token_manager.get_auth_headers()

            if headers and 'Authorization' in headers:
                self.last_refresh_time = datetime.now()
                self.refresh_count += 1
                self.failure_count = 0

                logger.info(
                    f"✅ Token refresh successful! "
                    f"(Count: {self.refresh_count}, "
                    f"Time: {self.last_refresh_time.strftime('%Y-%m-%d %H:%M:%S')})"
                )
                return True
            else:
                raise Exception("Failed to get valid auth headers")

        except Exception as e:
            self.failure_count += 1
            logger.error(
                f"❌ Token refresh failed! "
                f"(Failure count: {self.failure_count}, Error: {str(e)})"
            )

            # Alert if consecutive failures
            if self.failure_count >= 3:
                logger.critical(
                    f"🚨 CRITICAL: {self.failure_count} consecutive token refresh failures! "
                    f"Manual intervention may be required."
                )

            return False

    async def health_check(self):
        """Perform health check on token status"""
        try:
            logger.info("🏥 Performing token health check...")

            # Check if token is still valid
            headers = await self.token_manager.get_auth_headers()

            if headers:
                time_since_refresh = (
                    datetime.now() - self.last_refresh_time
                    if self.last_refresh_time
                    else None
                )

                logger.info(
                    f"✅ Token health check passed. "
                    f"Last refresh: {time_since_refresh or 'Never'}"
                )
                return True
            else:
                logger.warning("⚠️ Token health check failed - token may be invalid")
                return False

        except Exception as e:
            logger.error(f"❌ Health check error: {str(e)}")
            return False

    def start(self):
        """Start the token refresh scheduler"""
        try:
            logger.info("🚀 Starting Zoho Token Refresh Scheduler...")

            # Schedule token refresh every 50 minutes
            # (Zoho access tokens expire in 60 minutes)
            self.scheduler.add_job(
                self.refresh_token,
                trigger=IntervalTrigger(minutes=50),
                id='zoho_token_refresh',
                name='Zoho Token Refresh',
                replace_existing=True,
                max_instances=1
            )

            # Schedule health check every 10 minutes
            self.scheduler.add_job(
                self.health_check,
                trigger=IntervalTrigger(minutes=10),
                id='zoho_token_health_check',
                name='Zoho Token Health Check',
                replace_existing=True,
                max_instances=1
            )

            self.scheduler.start()

            logger.info(
                "✅ Zoho Token Refresh Scheduler started successfully\n"
                "   - Token refresh: Every 50 minutes\n"
                "   - Health check: Every 10 minutes"
            )

        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {str(e)}")
            raise

    def stop(self):
        """Stop the token refresh scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=True)
                logger.info("🛑 Zoho Token Refresh Scheduler stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping scheduler: {str(e)}")

    def get_status(self) -> dict:
        """Get current scheduler status"""
        return {
            'running': self.scheduler.running if self.scheduler else False,
            'last_refresh_time': self.last_refresh_time.isoformat() if self.last_refresh_time else None,
            'refresh_count': self.refresh_count,
            'failure_count': self.failure_count,
            'next_refresh': self._get_next_run_time('zoho_token_refresh'),
            'next_health_check': self._get_next_run_time('zoho_token_health_check')
        }

    def _get_next_run_time(self, job_id: str) -> Optional[str]:
        """Get next run time for a scheduled job"""
        try:
            job = self.scheduler.get_job(job_id)
            if job and job.next_run_time:
                return job.next_run_time.isoformat()
        except Exception:
            pass
        return None


# Global scheduler instance
_scheduler_instance: Optional[ZohoTokenRefreshScheduler] = None


def get_scheduler() -> ZohoTokenRefreshScheduler:
    """Get or create the global scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = ZohoTokenRefreshScheduler()
    return _scheduler_instance


async def start_token_refresh_scheduler():
    """Start the token refresh scheduler (called on app startup)"""
    scheduler = get_scheduler()
    scheduler.start()

    # Perform immediate refresh on startup
    await scheduler.refresh_token()


def stop_token_refresh_scheduler():
    """Stop the token refresh scheduler (called on app shutdown)"""
    global _scheduler_instance
    if _scheduler_instance:
        _scheduler_instance.stop()
        _scheduler_instance = None
