"""
Zoho Product Image Import Service
خدمة استيراد صور المنتجات من Zoho

This service downloads product images from Zoho and imports them into TSH ERP System
"""

import asyncio
import aiohttp
import aiofiles
import os
import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import mimetypes
from PIL import Image
import hashlib
import json
from datetime import datetime

from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.product import Product
from app.services.zoho_service import ZohoService
from app.services.config_service import SecureConfigService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductImageImportService:
    """Service to import product images from Zoho to TSH ERP System"""
    
    def __init__(self, db: Session):
        self.db = db
        self.zoho_service = ZohoService()
        self.config_service = SecureConfigService()
        
        # Create directories for storing images
        self.base_image_dir = Path("app/static/images/products")
        self.base_image_dir.mkdir(parents=True, exist_ok=True)
        
        # Image settings
        self.max_image_size = (1024, 1024)  # Max dimensions
        self.thumbnail_size = (300, 300)    # Thumbnail dimensions
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        
    async def download_image(self, session: aiohttp.ClientSession, image_url: str, 
                           filename: str, product_sku: str) -> Optional[Dict]:
        """Download a single image from URL"""
        try:
            headers = {
                'User-Agent': 'TSH-ERP-System/1.0',
                'Accept': 'image/*'
            }
            
            async with session.get(image_url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    
                    # Validate content type
                    if not content_type.startswith('image/'):
                        logger.warning(f"Invalid content type for {image_url}: {content_type}")
                        return None
                    
                    # Create product-specific directory
                    product_dir = self.base_image_dir / product_sku
                    product_dir.mkdir(exist_ok=True)
                    
                    # Save original image
                    original_path = product_dir / f"original_{filename}"
                    
                    content = await response.read()
                    async with aiofiles.open(original_path, 'wb') as f:
                        await f.write(content)
                    
                    # Process and resize image
                    processed_info = await self.process_image(original_path, product_dir, filename)
                    
                    if processed_info:
                        logger.info(f"✅ Downloaded and processed image for {product_sku}: {filename}")
                        return {
                            'original_url': image_url,
                            'original_path': str(original_path),
                            'processed_path': processed_info['main_path'],
                            'thumbnail_path': processed_info['thumbnail_path'],
                            'size': processed_info['size'],
                            'format': processed_info['format'],
                            'file_size': os.path.getsize(original_path),
                            'downloaded_at': datetime.now().isoformat()
                        }
                else:
                    logger.warning(f"Failed to download {image_url}: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error downloading image {image_url}: {str(e)}")
            return None
    
    async def process_image(self, original_path: Path, product_dir: Path, 
                          filename: str) -> Optional[Dict]:
        """Process and resize image"""
        try:
            with Image.open(original_path) as img:
                # Convert RGBA to RGB if necessary
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                
                # Create main resized image
                img_resized = img.copy()
                img_resized.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)
                
                main_path = product_dir / f"main_{filename}"
                img_resized.save(main_path, 'JPEG', quality=85, optimize=True)
                
                # Create thumbnail
                img_thumb = img.copy()
                img_thumb.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                
                thumb_path = product_dir / f"thumb_{filename}"
                img_thumb.save(thumb_path, 'JPEG', quality=80, optimize=True)
                
                return {
                    'main_path': str(main_path),
                    'thumbnail_path': str(thumb_path),
                    'size': img_resized.size,
                    'format': img_resized.format or 'JPEG'
                }
                
        except Exception as e:
            logger.error(f"Error processing image {original_path}: {str(e)}")
            return None
    
    async def get_product_images_from_zoho(self, item_id: str) -> List[str]:
        """Get product images from Zoho Inventory"""
        try:
            # Get item details with images
            item_details = await self.zoho_service.get_item_details(item_id)
            
            image_urls = []
            
            # Check for primary image
            if item_details.get('image_name'):
                # Construct image URL (Zoho format)
                image_url = f"https://inventory.zoho.com/api/v1/items/{item_id}/image"
                image_urls.append(image_url)
            
            # Check for additional images in item details
            if 'images' in item_details:
                for img in item_details['images']:
                    if isinstance(img, dict) and 'image_url' in img:
                        image_urls.append(img['image_url'])
                    elif isinstance(img, str):
                        image_urls.append(img)
            
            # Also check documents for images
            if 'documents' in item_details:
                for doc in item_details['documents']:
                    if doc.get('file_name', '').lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        image_urls.append(doc.get('download_url', ''))
            
            return [url for url in image_urls if url]  # Filter out empty URLs
            
        except Exception as e:
            logger.error(f"Error getting images for item {item_id}: {str(e)}")
            return []
    
    async def import_product_images(self, batch_size: int = 10) -> Dict[str, Any]:
        """Import all product images from Zoho"""
        try:
            logger.info("🔄 Starting product image import from Zoho...")
            
            # Get all products from TSH ERP that might have Zoho references
            products = self.db.query(Product).all()
            
            results = {
                'total_products': len(products),
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'images_downloaded': 0,
                'errors': [],
                'product_results': []
            }
            
            # Create aiohttp session
            connector = aiohttp.TCPConnector(limit=20, limit_per_host=5)
            timeout = aiohttp.ClientTimeout(total=300)
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                
                # Process products in batches
                for i in range(0, len(products), batch_size):
                    batch = products[i:i + batch_size]
                    
                    logger.info(f"📦 Processing batch {i//batch_size + 1}/{(len(products)-1)//batch_size + 1} ({len(batch)} products)")
                    
                    # Process batch
                    batch_tasks = [
                        self.process_single_product(session, product) 
                        for product in batch
                    ]
                    
                    batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                    
                    # Process results
                    for product, result in zip(batch, batch_results):
                        results['processed'] += 1
                        
                        if isinstance(result, Exception):
                            results['failed'] += 1
                            results['errors'].append({
                                'product_sku': product.sku,
                                'error': str(result)
                            })
                        elif result and result['success']:
                            results['successful'] += 1
                            results['images_downloaded'] += result['images_count']
                            results['product_results'].append(result)
                        else:
                            results['failed'] += 1
                            if result:
                                results['errors'].append({
                                    'product_sku': product.sku,
                                    'error': result.get('error', 'Unknown error')
                                })
                    
                    # Small delay between batches
                    await asyncio.sleep(1)
            
            # Save results to file
            results_file = Path(f"zoho_image_import_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"📊 Import completed!")
            logger.info(f"✅ Successful: {results['successful']}/{results['total_products']}")
            logger.info(f"📸 Total images downloaded: {results['images_downloaded']}")
            logger.info(f"❌ Failed: {results['failed']}")
            logger.info(f"📁 Results saved to: {results_file}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in image import: {str(e)}")
            raise
    
    async def process_single_product(self, session: aiohttp.ClientSession, 
                                   product: Product) -> Dict[str, Any]:
        """Process images for a single product"""
        try:
            result = {
                'product_id': product.id,
                'product_sku': product.sku,
                'product_name': product.name,
                'success': False,
                'images_count': 0,
                'images': [],
                'error': None
            }
            
            # Try to find Zoho item ID (this might be in product.tags or other fields)
            zoho_item_id = None
            
            # Check if we have Zoho ID in tags
            if product.tags:
                for tag in product.tags:
                    if isinstance(tag, dict) and 'zoho_item_id' in tag:
                        zoho_item_id = tag['zoho_item_id']
                        break
                    elif isinstance(tag, str) and tag.startswith('zoho_'):
                        zoho_item_id = tag.replace('zoho_', '')
            
            # If no Zoho ID found, try to match by SKU or name
            if not zoho_item_id:
                # Get all Zoho items and try to match
                zoho_items = await self.zoho_service.get_all_items()
                for item in zoho_items:
                    if (item.get('sku') == product.sku or 
                        item.get('name') == product.name):
                        zoho_item_id = item.get('item_id')
                        break
            
            if not zoho_item_id:
                result['error'] = 'No matching Zoho item found'
                return result
            
            # Get images from Zoho
            image_urls = await self.get_product_images_from_zoho(zoho_item_id)
            
            if not image_urls:
                result['error'] = 'No images found in Zoho'
                return result
            
            # Download images
            downloaded_images = []
            for idx, image_url in enumerate(image_urls):
                filename = f"img_{idx+1}_{hashlib.md5(image_url.encode()).hexdigest()[:8]}.jpg"
                
                image_info = await self.download_image(
                    session, image_url, filename, product.sku
                )
                
                if image_info:
                    downloaded_images.append(image_info)
            
            if downloaded_images:
                # Update product in database
                primary_image = downloaded_images[0]
                
                # Update main image URL (relative path for web serving)
                product.image_url = f"/static/images/products/{product.sku}/main_{Path(primary_image['processed_path']).name}"
                
                # Update images JSON with all images
                product.images = [
                    {
                        'url': f"/static/images/products/{product.sku}/main_{Path(img['processed_path']).name}",
                        'thumbnail': f"/static/images/products/{product.sku}/thumb_{Path(img['thumbnail_path']).name}",
                        'original_url': img['original_url'],
                        'size': img['size'],
                        'downloaded_at': img['downloaded_at']
                    }
                    for img in downloaded_images
                ]
                
                # Add Zoho reference to tags if not already present
                if not product.tags:
                    product.tags = []
                
                # Add or update Zoho tag
                zoho_tag_exists = False
                for i, tag in enumerate(product.tags):
                    if isinstance(tag, dict) and 'zoho_item_id' in tag:
                        product.tags[i]['zoho_item_id'] = zoho_item_id
                        zoho_tag_exists = True
                        break
                
                if not zoho_tag_exists:
                    product.tags.append({
                        'zoho_item_id': zoho_item_id,
                        'images_imported_at': datetime.now().isoformat()
                    })
                
                # Commit changes
                self.db.commit()
                
                result['success'] = True
                result['images_count'] = len(downloaded_images)
                result['images'] = downloaded_images
                
                logger.info(f"✅ Updated product {product.sku} with {len(downloaded_images)} images")
            
            else:
                result['error'] = 'Failed to download any images'
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing product {product.sku}: {str(e)}")
            return {
                'product_id': product.id,
                'product_sku': product.sku,
                'success': False,
                'error': str(e)
            }


async def main():
    """Main function to run the image import"""
    try:
        # Get database session
        db = next(get_db())
        
        # Create import service
        import_service = ProductImageImportService(db)
        
        # Run import
        results = await import_service.import_product_images(batch_size=5)
        
        print("\n" + "="*60)
        print("🎉 ZOHO PRODUCT IMAGE IMPORT COMPLETED!")
        print("="*60)
        print(f"📊 Total Products: {results['total_products']}")
        print(f"✅ Successful: {results['successful']}")
        print(f"❌ Failed: {results['failed']}")
        print(f"📸 Images Downloaded: {results['images_downloaded']}")
        print("="*60)
        
        if results['errors']:
            print("\n❌ Errors encountered:")
            for error in results['errors'][:10]:  # Show first 10 errors
                print(f"  • {error['product_sku']}: {error['error']}")
        
        db.close()
        
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
