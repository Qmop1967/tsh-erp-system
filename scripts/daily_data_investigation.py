#!/usr/bin/env python3
"""
Daily Data Investigation Script
================================

Compares data counts between Zoho and TSH ERP database.
التحقيق اليومي للبيانات - مقارنة بين Zoho وقاعدة البيانات

Author: TSH ERP Team
Date: November 7, 2025
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple
import logging

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import text
from app.db.database import SessionLocal
from app.tds.integrations.zoho import UnifiedZohoClient, ZohoAuthManager, ZohoCredentials, ZohoAPI
from app.models.data_investigation import DataInvestigationReport

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/tsh_erp/data_investigation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
MISMATCH_THRESHOLD = 5  # Alert if difference is more than 5%


class DataInvestigator:
    """
    Daily data investigation coordinator
    منسق التحقيق اليومي للبيانات
    """

    def __init__(self):
        """Initialize data investigator"""
        self.db = SessionLocal()
        self.zoho_client = None
        self.results: List[Dict] = []

    async def initialize_zoho(self):
        """Initialize Zoho client"""
        logger.info("Initializing Zoho client...")

        credentials = ZohoCredentials(
            client_id=os.getenv('ZOHO_CLIENT_ID'),
            client_secret=os.getenv('ZOHO_CLIENT_SECRET'),
            refresh_token=os.getenv('ZOHO_REFRESH_TOKEN'),
            organization_id=os.getenv('ZOHO_ORGANIZATION_ID')
        )

        auth_manager = ZohoAuthManager(credentials, auto_refresh=True)
        await auth_manager.start()

        self.zoho_client = UnifiedZohoClient(
            auth_manager=auth_manager,
            organization_id=credentials.organization_id,
            rate_limit=100
        )

        await self.zoho_client.__aenter__()
        logger.info("✅ Zoho client initialized")

    async def get_zoho_count(self, entity_type: str) -> Tuple[int, str]:
        """
        Get count from Zoho for specific entity type

        Args:
            entity_type: products, customers, invoices, etc.

        Returns:
            Tuple of (count, error_message)
        """
        try:
            endpoint_map = {
                'products': 'items',
                'customers': 'contacts',
                'invoices': 'invoices',
                'sales_orders': 'salesorders',
                'purchase_orders': 'purchaseorders',
                'bills': 'bills',
                'vendors': 'contacts',
            }

            endpoint = endpoint_map.get(entity_type)
            if not endpoint:
                return 0, f"Unknown entity type: {entity_type}"

            # Add filters for specific entity types
            params = {"per_page": 1, "page": 1}
            if entity_type == 'vendors':
                params['contact_type'] = 'vendor'
            elif entity_type == 'customers':
                params['contact_type'] = 'customer'

            response = await self.zoho_client.get(
                api_type=ZohoAPI.INVENTORY,
                endpoint=endpoint,
                params=params
            )

            # Extract total count from page_context
            page_context = response.get('page_context', {})
            total = page_context.get('total', 0)

            logger.info(f"Zoho {entity_type}: {total}")
            return total, None

        except Exception as e:
            error_msg = f"Error fetching Zoho {entity_type}: {str(e)}"
            logger.error(error_msg)
            return 0, error_msg

    def get_tsh_erp_count(self, entity_type: str) -> Tuple[int, str]:
        """
        Get count from TSH ERP database for specific entity type

        Args:
            entity_type: products, customers, invoices, etc.

        Returns:
            Tuple of (count, error_message)
        """
        try:
            table_map = {
                'products': 'products',
                'customers': 'customers',
                'invoices': 'invoices',
                'sales_orders': 'sales_orders',
                'purchase_orders': 'purchase_orders',
                'bills': 'purchase_invoices',
                'vendors': 'suppliers',
            }

            table = table_map.get(entity_type)
            if not table:
                return 0, f"Unknown entity type: {entity_type}"

            # Build query with appropriate filters
            query = f"SELECT COUNT(*) as count FROM {table}"

            # Add is_active filter if table has it
            if entity_type in ['products', 'customers']:
                query += " WHERE is_active = true"

            result = self.db.execute(text(query))
            count = result.scalar()

            logger.info(f"TSH ERP {entity_type}: {count}")
            return count, None

        except Exception as e:
            error_msg = f"Error fetching TSH ERP {entity_type}: {str(e)}"
            logger.error(error_msg)
            return 0, error_msg

    async def investigate_entity(self, entity_type: str):
        """
        Investigate single entity type

        Args:
            entity_type: products, customers, etc.
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Investigating {entity_type}...")
        logger.info(f"{'='*60}")

        # Get counts from both systems
        zoho_count, zoho_error = await self.get_zoho_count(entity_type)
        tsh_erp_count, tsh_erp_error = self.get_tsh_erp_count(entity_type)

        # Calculate difference
        difference = abs(zoho_count - tsh_erp_count)
        difference_pct = (difference / zoho_count * 100) if zoho_count > 0 else 0

        # Determine status
        if zoho_error or tsh_erp_error:
            status = "error"
        elif difference == 0:
            status = "matched"
        else:
            status = "mismatch"

        is_critical = difference_pct > MISMATCH_THRESHOLD

        # Prepare result
        result = {
            'entity_type': entity_type,
            'zoho_count': zoho_count,
            'tsh_erp_count': tsh_erp_count,
            'difference': difference,
            'difference_percentage': f"{difference_pct:.2f}%",
            'status': status,
            'is_critical': is_critical,
            'error_message': zoho_error or tsh_erp_error,
            'details': {
                'investigation_time': datetime.utcnow().isoformat(),
                'threshold_used': MISMATCH_THRESHOLD
            }
        }

        self.results.append(result)

        # Log result
        if status == "matched":
            logger.info(f"✅ {entity_type}: MATCHED ({zoho_count})")
        elif status == "mismatch":
            emoji = "🚨" if is_critical else "⚠️"
            logger.warning(
                f"{emoji} {entity_type}: MISMATCH - "
                f"Zoho: {zoho_count}, TSH ERP: {tsh_erp_count}, "
                f"Difference: {difference} ({difference_pct:.2f}%)"
            )
        else:
            logger.error(f"❌ {entity_type}: ERROR - {zoho_error or tsh_erp_error}")

    def save_results(self):
        """Save investigation results to database"""
        logger.info("\n" + "="*60)
        logger.info("Saving investigation results...")
        logger.info("="*60)

        try:
            for result in self.results:
                report = DataInvestigationReport(
                    entity_type=result['entity_type'],
                    zoho_count=result['zoho_count'],
                    tsh_erp_count=result['tsh_erp_count'],
                    difference=result['difference'],
                    difference_percentage=result['difference_percentage'],
                    status=result['status'],
                    is_critical=result['is_critical'],
                    error_message=result['error_message'],
                    details=result['details']
                )
                self.db.add(report)

            self.db.commit()
            logger.info("✅ Results saved to database")

        except Exception as e:
            logger.error(f"❌ Error saving results: {str(e)}")
            self.db.rollback()

    def print_summary(self):
        """Print investigation summary"""
        logger.info("\n" + "="*60)
        logger.info("📊 DAILY DATA INVESTIGATION SUMMARY")
        logger.info("="*60)
        logger.info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Total entities investigated: {len(self.results)}")

        matched = sum(1 for r in self.results if r['status'] == 'matched')
        mismatched = sum(1 for r in self.results if r['status'] == 'mismatch')
        critical = sum(1 for r in self.results if r['is_critical'])
        errors = sum(1 for r in self.results if r['status'] == 'error')

        logger.info(f"\n✅ Matched: {matched}")
        logger.info(f"⚠️  Mismatched: {mismatched}")
        logger.info(f"🚨 Critical: {critical}")
        logger.info(f"❌ Errors: {errors}")

        if critical > 0:
            logger.warning("\n🚨 CRITICAL MISMATCHES DETECTED:")
            for result in self.results:
                if result['is_critical']:
                    logger.warning(
                        f"  - {result['entity_type']}: "
                        f"Zoho={result['zoho_count']}, "
                        f"TSH ERP={result['tsh_erp_count']}, "
                        f"Diff={result['difference_percentage']}"
                    )

        logger.info("="*60)

    async def run(self):
        """Run daily data investigation"""
        try:
            logger.info("\n" + "="*60)
            logger.info("🔍 STARTING DAILY DATA INVESTIGATION")
            logger.info("="*60)

            # Initialize Zoho client
            await self.initialize_zoho()

            # Investigate each entity type
            entity_types = [
                'products',
                'customers',
                'vendors',
                'invoices',
                'sales_orders',
                'purchase_orders',
                'bills'
            ]

            for entity_type in entity_types:
                await self.investigate_entity(entity_type)

            # Save results
            self.save_results()

            # Print summary
            self.print_summary()

            logger.info("\n✅ Daily data investigation completed successfully!")

        except Exception as e:
            logger.error(f"\n❌ Investigation failed: {str(e)}")
            import traceback
            traceback.print_exc()

        finally:
            # Cleanup
            if self.zoho_client:
                await self.zoho_client.__aexit__(None, None, None)
            self.db.close()


async def main():
    """Main entry point"""
    investigator = DataInvestigator()
    await investigator.run()


if __name__ == "__main__":
    asyncio.run(main())
