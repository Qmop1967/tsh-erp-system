"""
TDS Core - Simple Sync Worker (Non-ORM version)
Uses raw SQL to bypass SQLAlchemy ORM async issues
"""
import asyncio
import logging
import time
from uuid import uuid4
import asyncpg
import json

from core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleWorker:
    """Simple worker using raw asyncpg instead of SQLAlchemy ORM"""
    
    def __init__(self):
        self.worker_id = f"simple-worker-{uuid4().hex[:8]}"
        self.running = False
        self.pool = None
        self.stats = {
            "processed": 0,
            "succeeded": 0,
            "failed": 0
        }
        
    async def start(self):
        """Start the worker"""
        self.running = True
        
        # Create database connection pool
        logger.info(f"Creating database connection pool...")
        self.pool = await asyncpg.create_pool(
            host=settings.database_host,
            port=settings.database_port,
            database=settings.database_name,
            user=settings.database_user,
            password=settings.database_password,
            min_size=2,
            max_size=10
        )
        logger.info(f"✅ Database pool created")
        
        logger.info(f"🚀 Simple worker {self.worker_id} started")
        
        try:
            while self.running:
                try:
                    processed = await self._process_batch()
                    
                    if processed == 0:
                        await asyncio.sleep(1)
                    else:
                        logger.info(f"📊 Stats: processed={self.stats['processed']}, succeeded={self.stats['succeeded']}, failed={self.stats['failed']}")
                        
                except Exception as e:
                    logger.error(f"Error in worker loop: {e}", exc_info=True)
                    await asyncio.sleep(5)
                    
        finally:
            if self.pool:
                await self.pool.close()
            logger.info(f"🛑 Simple worker {self.worker_id} stopped")
            logger.info(f"📊 Final stats: {self.stats}")
            
    async def _process_batch(self) -> int:
        """Process a batch of pending events"""
        try:
            async with self.pool.acquire() as conn:
                # Get pending events using raw SQL
                rows = await conn.fetch("""
                    SELECT id, entity_type, source_entity_id, operation_type, 
                           validated_payload, attempt_count
                    FROM tds_sync_queue
                    WHERE status = 'pending'
                      AND locked_by IS NULL
                      AND priority >= 1
                    ORDER BY priority ASC, created_at ASC
                    LIMIT 10
                """)
                
                if not rows:
                    return 0
                    
                logger.info(f"Processing batch of {len(rows)} events...")
                    
                for row in rows:
                    await self._process_event(row, conn)
                    
                return len(rows)
                
        except Exception as e:
            logger.error(f"Error in _process_batch: {e}", exc_info=True)
            return 0
            
    async def _process_event(self, row, conn):
        """Process a single event"""
        try:
            # Mark as processing
            await conn.execute("""
                UPDATE tds_sync_queue
                SET status = 'processing',
                    locked_by = $1
                WHERE id = $2
            """, self.worker_id, row['id'])

            logger.info(f"Processing {row['entity_type']}:{row['source_entity_id']}")

            # Process based on entity type
            entity_type = str(row['entity_type']).lower()
            payload = row['validated_payload']

            # Handle both string and dict types (asyncpg may return JSONB as string)
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON payload: {e}")
                    raise ValueError(f"Invalid JSON in validated_payload: {e}")

            if 'product' in entity_type:
                await self._sync_product(payload, conn)
            else:
                logger.warning(f"No handler for entity type: {entity_type}")

            # Mark as completed
            await conn.execute("""
                UPDATE tds_sync_queue
                SET status = 'completed',
                    completed_at = NOW(),
                    locked_by = NULL
                WHERE id = $1
            """, row['id'])

            self.stats['processed'] += 1
            self.stats['succeeded'] += 1
            logger.info(f"✅ Completed: {row['source_entity_id']}")

        except Exception as e:
            self.stats['processed'] += 1
            self.stats['failed'] += 1
            logger.error(f"❌ Error processing event {row['id']}: {e}")
            # Mark as failed
            await conn.execute("""
                UPDATE tds_sync_queue
                SET status = 'failed',
                    attempt_count = attempt_count + 1,
                    last_error = $1,
                    locked_by = NULL
                WHERE id = $2
            """, str(e), row['id'])

    async def _sync_product(self, payload: dict, conn):
        """Sync product to local database"""
        try:
            # Extract fields from payload
            zoho_item_id = payload.get("item_id") or payload.get("id")
            if not zoho_item_id:
                raise ValueError("Missing item_id in payload")

            name = payload.get("name", "")
            sku = payload.get("sku", "") or payload.get("item_code", "")
            description = payload.get("description", "")
            price = float(payload.get("rate", 0) or payload.get("price", 0))
            stock_quantity = int(payload.get("stock_on_hand", 0) or payload.get("stock", 0))

            # Extract actual_available_stock from locations array
            actual_available_stock = 0
            locations = payload.get("locations", [])
            if locations and isinstance(locations, list):
                for location in locations:
                    if isinstance(location, dict):
                        loc_stock = location.get("location_actual_available_stock", 0)
                        actual_available_stock += int(loc_stock) if loc_stock else 0
                logger.info(f"Calculated actual_available_stock from {len(locations)} locations: {actual_available_stock}")
            else:
                # Fallback to stock_quantity if no locations data
                actual_available_stock = stock_quantity

            # Respect Zoho product status
            zoho_status = payload.get("status", "active").lower()
            is_active = zoho_status == "active"

            # Set image_url to use local ERP API endpoint
            image_url = f"/api/zoho/image/{zoho_item_id}"
            cdn_image_url = None  # Not using CDN anymore

            logger.info(f"Syncing product: {name} (SKU: {sku}, Zoho ID: {zoho_item_id}, Stock: {stock_quantity}, Available: {actual_available_stock}, Status: {zoho_status})")

            # Upsert product using raw SQL
            await conn.execute("""
                INSERT INTO products (
                    zoho_item_id, name, sku, description, price,
                    stock_quantity, actual_available_stock, is_active,
                    image_url, cdn_image_url, created_at, updated_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW(), NOW())
                ON CONFLICT (zoho_item_id)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    sku = EXCLUDED.sku,
                    description = EXCLUDED.description,
                    price = EXCLUDED.price,
                    stock_quantity = EXCLUDED.stock_quantity,
                    actual_available_stock = EXCLUDED.actual_available_stock,
                    is_active = EXCLUDED.is_active,
                    image_url = EXCLUDED.image_url,
                    cdn_image_url = EXCLUDED.cdn_image_url,
                    updated_at = NOW()
            """, zoho_item_id, name, sku, description, price, stock_quantity, actual_available_stock, is_active, image_url, cdn_image_url)

            logger.info(f"✅ Product synced: {name}")

        except Exception as e:
            logger.error(f"Error syncing product: {e}", exc_info=True)
            raise


async def run_simple_worker():
    """Run the simple worker"""
    worker = SimpleWorker()
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        worker.running = False


if __name__ == "__main__":
    asyncio.run(run_simple_worker())
