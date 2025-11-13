#!/usr/bin/env python3
"""
Download All Product Images from Zoho Using MCP
===============================================

Downloads product images from Zoho Books using MCP functions and stores them locally.
Updates database with local image paths.

Author: TSH ERP Team
Date: November 13, 2025
"""

import os
import sys
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from urllib.parse import urlparse

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ZohoImageDownloader:
    """Downloads product images from Zoho using MCP"""

    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.org_id = os.getenv("ZOHO_ORGANIZATION_ID", "748369814")
        self.uploads_dir = project_root / "uploads" / "products"
        self.downloads_count = 0
        self.errors_count = 0
        self.skipped_count = 0
        
        # Create uploads directory
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Database engine
        if not self.db_url:
            raise ValueError("DATABASE_URL not found in environment")
        
        self.engine = create_engine(self.db_url)

    async def download_image(self, session: aiohttp.ClientSession, image_url: str, product_sku: str) -> str:
        """Download a single image from URL"""
        try:
            # Get file extension from URL
            parsed_url = urlparse(image_url)
            ext = Path(parsed_url.path).suffix or '.jpg'
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_sku = "".join(c for c in product_sku if c.isalnum() or c in ('-', '_'))
            filename = f"{safe_sku}_{timestamp}{ext}"
            filepath = self.uploads_dir / filename
            
            # Download image
            async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Save to file
                    async with aiofiles.open(filepath, 'wb') as f:
                        await f.write(content)
                    
                    self.downloads_count += 1
                    print(f"  ✅ Downloaded: {filename} ({len(content)} bytes)")
                    
                    # Return relative path for database
                    return f"/uploads/products/{filename}"
                else:
                    print(f"  ❌ Failed to download: HTTP {response.status}")
                    self.errors_count += 1
                    return None
                    
        except Exception as e:
            print(f"  ❌ Error downloading image: {e}")
            self.errors_count += 1
            return None

    def get_products_needing_images(self) -> List[Dict[str, Any]]:
        """Get products from database that need images"""
        query = text("""
            SELECT id, sku, name, zoho_item_id, image_url
            FROM products
            WHERE status = 'active'
            AND (image_url IS NULL OR image_url = '' OR image_url NOT LIKE '/uploads/%')
            ORDER BY id
            LIMIT 100
        """)
        
        with self.engine.connect() as conn:
            result = conn.execute(query)
            return [dict(row._mapping) for row in result]

    def update_product_image_url(self, product_id: int, new_image_url: str):
        """Update product image URL in database"""
        query = text("""
            UPDATE products
            SET image_url = :image_url,
                updated_at = NOW()
            WHERE id = :product_id
        """)
        
        with self.engine.connect() as conn:
            conn.execute(query, {"image_url": new_image_url, "product_id": product_id})
            conn.commit()

    async def fetch_image_from_zoho(self, zoho_item_id: str) -> str:
        """Fetch product image URL from Zoho Books using MCP"""
        # Note: This would use MCP function mcp_ZohoMCP_ZohoBooks_get_item
        # For now, we'll construct the image URL based on Zoho's pattern
        # In production, you'd call the actual MCP function
        
        # Zoho Books image URL pattern
        return f"https://books.zoho.com/api/v3/items/{zoho_item_id}/image?organization_id={self.org_id}"

    async def download_all_images(self):
        """Main function to download all product images"""
        print("=" * 70)
        print("🖼️  TSH ERP - Product Image Downloader (via MCP)")
        print("=" * 70)
        print()
        
        # Get products needing images
        products = self.get_products_needing_images()
        total = len(products)
        
        if total == 0:
            print("✅ No products need image download. All products have local images!")
            return
        
        print(f"📦 Found {total} products needing images")
        print(f"📁 Download location: {self.uploads_dir}")
        print()
        
        # Create aiohttp session
        async with aiohttp.ClientSession() as session:
            for index, product in enumerate(products, 1):
                print(f"[{index}/{total}] Processing: {product['sku']} - {product['name'][:50]}")
                
                # Get image URL from Zoho
                if product.get('zoho_item_id'):
                    zoho_image_url = await self.fetch_image_from_zoho(product['zoho_item_id'])
                    
                    # Download image
                    local_path = await self.download_image(session, zoho_image_url, product['sku'])
                    
                    if local_path:
                        # Update database
                        self.update_product_image_url(product['id'], local_path)
                        print(f"  💾 Updated database with local path")
                    else:
                        print(f"  ⚠️  Skipping database update (download failed)")
                else:
                    print(f"  ⚠️  No Zoho item ID, skipping")
                    self.skipped_count += 1
                
                print()
                
                # Add small delay to avoid rate limiting
                await asyncio.sleep(0.5)
        
        # Summary
        print("=" * 70)
        print("📊 Download Summary")
        print("=" * 70)
        print(f"✅ Successfully downloaded: {self.downloads_count}")
        print(f"❌ Errors: {self.errors_count}")
        print(f"⚠️  Skipped: {self.skipped_count}")
        print(f"📁 Images saved to: {self.uploads_dir}")
        print("=" * 70)


async def main():
    """Main entry point"""
    downloader = ZohoImageDownloader()
    await downloader.download_all_images()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Download interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)

