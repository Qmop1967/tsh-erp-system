"""
Zoho Image Sync Service
========================

Downloads and stores product images from Zoho Books.

Author: TSH ERP Team
Date: November 9, 2025
"""

import logging
import asyncio
import aiohttp
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ZohoImageSyncService:
    """
    Service for syncing product images from Zoho Books

    Downloads images from Zoho and stores them locally with proper naming.
    """

    def __init__(self, auth_manager, base_image_path: str = "/root/TSH_ERP_Ecosystem/static/images/products"):
        """
        Initialize image sync service

        Args:
            auth_manager: ZohoAuthManager instance
            base_image_path: Base directory for storing images
        """
        self.auth_manager = auth_manager
        self.base_image_path = Path(base_image_path)
        self.base_image_path.mkdir(parents=True, exist_ok=True)

        self.organization_id = "748369814"
        self.base_url = "https://www.zohoapis.com/books/v3"

        # Statistics
        self.stats = {
            'total': 0,
            'downloaded': 0,
            'skipped': 0,
            'failed': 0,
            'errors': []
        }

    async def download_item_image(
        self,
        item_id: str,
        item_name: str,
        session: aiohttp.ClientSession
    ) -> Optional[str]:
        """
        Download image for a single item

        Args:
            item_id: Zoho item ID
            item_name: Item name for filename
            session: aiohttp session

        Returns:
            str: Local file path if successful, None otherwise
        """
        try:
            # Get fresh token
            token = await self.auth_manager.get_access_token()

            # Construct image URL
            url = f"{self.base_url}/items/{item_id}/image"
            params = {"organization_id": self.organization_id}
            headers = {"Authorization": f"Zoho-oauthtoken {token}"}

            # Download image
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    # Get content type to determine extension
                    content_type = response.headers.get('Content-Type', '')

                    # Determine file extension
                    if 'jpeg' in content_type or 'jpg' in content_type:
                        ext = 'jpg'
                    elif 'png' in content_type:
                        ext = 'png'
                    elif 'gif' in content_type:
                        ext = 'gif'
                    elif 'webp' in content_type:
                        ext = 'webp'
                    else:
                        ext = 'jpg'  # Default

                    # Create safe filename
                    safe_name = self._create_safe_filename(item_name)
                    filename = f"item_{item_id}_{safe_name}.{ext}"
                    filepath = self.base_image_path / filename

                    # Save image
                    content = await response.read()
                    with open(filepath, 'wb') as f:
                        f.write(content)

                    logger.debug(f"Downloaded image: {filename}")
                    self.stats['downloaded'] += 1

                    # Return relative path for database
                    return f"/static/images/products/{filename}"

                elif response.status == 404:
                    # No image for this item
                    logger.debug(f"No image found for item {item_id}")
                    self.stats['skipped'] += 1
                    return None

                else:
                    logger.warning(f"Failed to download image for {item_id}: HTTP {response.status}")
                    self.stats['failed'] += 1
                    self.stats['errors'].append({
                        'item_id': item_id,
                        'error': f"HTTP {response.status}",
                        'name': item_name
                    })
                    return None

        except Exception as e:
            logger.error(f"Error downloading image for {item_id}: {str(e)}")
            self.stats['failed'] += 1
            self.stats['errors'].append({
                'item_id': item_id,
                'error': str(e),
                'name': item_name
            })
            return None

    def _create_safe_filename(self, name: str, max_length: int = 50) -> str:
        """
        Create a safe filename from item name

        Args:
            name: Item name
            max_length: Maximum filename length

        Returns:
            str: Safe filename
        """
        import re

        # Remove special characters
        safe = re.sub(r'[^\w\s-]', '', name.lower())
        # Replace spaces with underscores
        safe = re.sub(r'[\s]+', '_', safe)
        # Truncate to max length
        safe = safe[:max_length]
        # Remove trailing underscores
        safe = safe.strip('_')

        return safe or 'unknown'

    async def sync_all_images(self, items: List[Dict[str, Any]], batch_size: int = 10) -> Dict[str, Any]:
        """
        Sync images for all items

        Args:
            items: List of item dictionaries with item_id and name
            batch_size: Number of concurrent downloads

        Returns:
            dict: Statistics about the sync
        """
        logger.info(f"Starting image sync for {len(items)} items...")

        self.stats['total'] = len(items)
        start_time = datetime.utcnow()

        # Filter items that have images
        items_with_images = [
            item for item in items
            if item.get('image_name') or item.get('image_document_id')
        ]

        logger.info(f"Found {len(items_with_images)} items with images in Zoho")

        # Create aiohttp session with timeout
        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector(limit=batch_size)

        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            # Process in batches
            for i in range(0, len(items_with_images), batch_size):
                batch = items_with_images[i:i + batch_size]

                # Download images concurrently
                tasks = [
                    self.download_item_image(
                        item.get('item_id'),
                        item.get('name', 'unknown'),
                        session
                    )
                    for item in batch
                ]

                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Update items with image paths
                for item, image_path in zip(batch, results):
                    if isinstance(image_path, str):
                        item['local_image_path'] = image_path

                # Progress logging
                processed = min(i + batch_size, len(items_with_images))
                logger.info(
                    f"Progress: {processed}/{len(items_with_images)} "
                    f"({processed/len(items_with_images)*100:.1f}%) - "
                    f"Downloaded: {self.stats['downloaded']}, "
                    f"Failed: {self.stats['failed']}"
                )

                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)

        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        self.stats['duration'] = duration
        self.stats['items_with_images'] = len(items_with_images)

        logger.info(
            f"✅ Image sync complete: {self.stats['downloaded']} downloaded, "
            f"{self.stats['failed']} failed, {self.stats['skipped']} skipped "
            f"in {duration:.1f}s"
        )

        return self.stats

    async def update_database_image_paths(self, items: List[Dict[str, Any]], db) -> int:
        """
        Update database with local image paths

        Args:
            items: List of items with local_image_path set
            db: Database session

        Returns:
            int: Number of records updated
        """
        from sqlalchemy import text

        updated = 0

        for item in items:
            if 'local_image_path' in item:
                try:
                    query = text("""
                        UPDATE products
                        SET image_url = :image_url, updated_at = NOW()
                        WHERE zoho_item_id = :zoho_item_id
                    """)

                    await db.execute(query, {
                        'image_url': item['local_image_path'],
                        'zoho_item_id': item['item_id']
                    })
                    updated += 1

                except Exception as e:
                    logger.error(f"Failed to update image path for {item.get('item_id')}: {str(e)}")

        await db.commit()

        logger.info(f"✅ Updated {updated} product records with image paths")

        return updated
