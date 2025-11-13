#!/usr/bin/env python3
"""
Download ALL Product Images from Zoho Books
===========================================

Uses Zoho Books API to download all product images and store them locally.
Updates TSH ERP database with local image paths.

Author: TSH ERP Team
Date: November 13, 2025
"""

import os
import sys
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse
import logging

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ZohoImageDownloader:
    """Downloads ALL product images from Zoho Books"""

    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.org_id = os.getenv("ZOHO_ORGANIZATION_ID", "748369814")
        self.zoho_token = os.getenv("ZOHO_ACCESS_TOKEN")
        self.uploads_dir = project_root / "uploads" / "products"
        
        # Statistics
        self.total_products = 0
        self.products_with_images = 0
        self.downloads_success = 0
        self.downloads_failed = 0
        self.downloads_skipped = 0
        self.db_updates = 0
        
        # Create uploads directory
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate environment
        if not self.db_url:
            raise ValueError("DATABASE_URL not found in environment")
        if not self.zoho_token:
            raise ValueError("ZOHO_ACCESS_TOKEN not found in environment")
        
        # Database engine
        self.engine = create_engine(self.db_url)
        
        logger.info(f"Initialized ZohoImageDownloader")
        logger.info(f"Organization ID: {self.org_id}")
        logger.info(f"Uploads directory: {self.uploads_dir}")

    async def fetch_zoho_products(self, page: int = 1, per_page: int = 200) -> List[Dict[str, Any]]:
        """Fetch products from Zoho Books API"""
        url = f"https://www.zohoapis.com/books/v3/items"
        
        params = {
            "organization_id": self.org_id,
            "page": page,
            "per_page": per_page
        }
        
        headers = {
            "Authorization": f"Zoho-oauthtoken {self.zoho_token}"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("items", [])
                    else:
                        logger.error(f"Failed to fetch products: HTTP {response.status}")
                        return []
            except Exception as e:
                logger.error(f"Error fetching products: {e}")
                return []

    async def download_zoho_image(self, session: aiohttp.ClientSession, item_id: str, document_id: str, image_name: str, sku: str) -> Optional[str]:
        """Download image from Zoho Books"""
        # Zoho Books image URL
        image_url = f"https://www.zohoapis.com/books/v3/items/{item_id}/image?organization_id={self.org_id}"
        
        headers = {
            "Authorization": f"Zoho-oauthtoken {self.zoho_token}"
        }
        
        try:
            # Generate filename
            ext = Path(image_name).suffix if image_name else '.jpg'
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            safe_sku = "".join(c for c in (sku or item_id) if c.isalnum() or c in ('-', '_'))[:50]
            filename = f"{safe_sku}_{timestamp}{ext}"
            filepath = self.uploads_dir / filename
            
            # Download image
            async with session.get(image_url, headers=headers, timeout=aiohttp.ClientTimeout(total=60)) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Verify it's an actual image (not error JSON)
                    if len(content) < 100 or content.startswith(b'{'):
                        logger.warning(f"  ⚠️  Invalid image data for {sku}")
                        self.downloads_skipped += 1
                        return None
                    
                    # Save to file
                    async with aiofiles.open(filepath, 'wb') as f:
                        await f.write(content)
                    
                    self.downloads_success += 1
                    logger.info(f"  ✅ Downloaded: {filename} ({len(content):,} bytes)")
                    
                    # Return relative path for database
                    return f"/uploads/products/{filename}"
                    
                elif response.status == 404:
                    logger.warning(f"  ⚠️  No image found for {sku}")
                    self.downloads_skipped += 1
                    return None
                else:
                    logger.error(f"  ❌ Failed to download {sku}: HTTP {response.status}")
                    self.downloads_failed += 1
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"  ❌ Timeout downloading image for {sku}")
            self.downloads_failed += 1
            return None
        except Exception as e:
            logger.error(f"  ❌ Error downloading image for {sku}: {e}")
            self.downloads_failed += 1
            return None

    def update_product_image_in_db(self, zoho_item_id: str, image_url: str) -> bool:
        """Update product image URL in database"""
        query = text("""
            UPDATE products
            SET image_url = :image_url,
                updated_at = NOW()
            WHERE zoho_item_id = :zoho_item_id
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"image_url": image_url, "zoho_item_id": zoho_item_id})
                conn.commit()
                
                if result.rowcount > 0:
                    self.db_updates += 1
                    return True
                else:
                    logger.warning(f"  ⚠️  Product not found in DB: {zoho_item_id}")
                    return False
        except Exception as e:
            logger.error(f"  ❌ Database update failed for {zoho_item_id}: {e}")
            return False

    async def download_all_images(self):
        """Main function to download ALL product images"""
        print("=" * 80)
        print("🖼️  TSH ERP - Complete Image Download from Zoho Books")
        print("=" * 80)
        print()
        
        logger.info("Starting image download process...")
        
        # Fetch all products from Zoho (with pagination)
        all_products = []
        page = 1
        has_more = True
        
        print("📦 Fetching all products from Zoho Books...")
        
        while has_more:
            products = await self.fetch_zoho_products(page=page, per_page=200)
            
            if products:
                all_products.extend(products)
                print(f"  📄 Fetched page {page}: {len(products)} products (Total: {len(all_products)})")
                page += 1
                
                # Check if there are more pages
                if len(products) < 200:
                    has_more = False
            else:
                has_more = False
        
        self.total_products = len(all_products)
        print(f"\n✅ Fetched {self.total_products} total products from Zoho")
        print()
        
        # Filter products with images
        products_with_images = [
            p for p in all_products
            if p.get('has_attachment') and p.get('image_document_id')
        ]
        
        self.products_with_images = len(products_with_images)
        
        print(f"🖼️  Found {self.products_with_images} products with images")
        print(f"📁 Download location: {self.uploads_dir}")
        print()
        
        if self.products_with_images == 0:
            print("⚠️  No products with images found!")
            return
        
        # Download images
        print("🚀 Starting image downloads...")
        print()
        
        async with aiohttp.ClientSession() as session:
            for index, product in enumerate(products_with_images, 1):
                item_id = product.get('item_id')
                sku = product.get('sku', item_id)
                name = product.get('name', 'Unknown')
                document_id = product.get('image_document_id')
                image_name = product.get('image_name', 'image.jpg')
                
                print(f"[{index}/{self.products_with_images}] {sku} - {name[:60]}")
                
                # Download image
                local_path = await self.download_zoho_image(
                    session, item_id, document_id, image_name, sku
                )
                
                if local_path:
                    # Update database
                    if self.update_product_image_in_db(item_id, local_path):
                        logger.info(f"  💾 Updated database")
                    else:
                        logger.warning(f"  ⚠️  Database update failed")
                
                print()
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.3)
        
        # Print summary
        print()
        print("=" * 80)
        print("📊 Image Download Summary")
        print("=" * 80)
        print(f"📦 Total products in Zoho:        {self.total_products:,}")
        print(f"🖼️  Products with images:          {self.products_with_images:,}")
        print(f"✅ Successfully downloaded:       {self.downloads_success:,}")
        print(f"❌ Failed downloads:              {self.downloads_failed:,}")
        print(f"⚠️  Skipped (no image/invalid):   {self.downloads_skipped:,}")
        print(f"💾 Database updates:              {self.db_updates:,}")
        print(f"📁 Images saved to:               {self.uploads_dir}")
        print("=" * 80)
        
        # Success rate
        if self.products_with_images > 0:
            success_rate = (self.downloads_success / self.products_with_images) * 100
            print(f"📈 Success rate: {success_rate:.1f}%")
            print("=" * 80)


async def main():
    """Main entry point"""
    try:
        downloader = ZohoImageDownloader()
        await downloader.download_all_images()
        
        print("\n✅ Image download complete!")
        
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        print("\nPlease ensure the following environment variables are set:")
        print("  - DATABASE_URL")
        print("  - ZOHO_ACCESS_TOKEN")
        print("  - ZOHO_ORGANIZATION_ID (optional, defaults to 748369814)")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        logger.exception("Fatal error occurred")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Download interrupted by user")
        print("You can run this script again to resume downloading remaining images.")
        sys.exit(0)

