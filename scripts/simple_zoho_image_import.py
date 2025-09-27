"""
Simple Zoho Product Image Importer
مستورد بسيط لصور المنتجات من Zoho

A simplified synchronous version for importing product images from Zoho
"""

import os
import sys
import requests
import json
import logging
from pathlib import Path
from PIL import Image
import hashlib
from datetime import datetime
from urllib.parse import urlparse
import time

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.models.product import Product
from app.services.config_service import SecureConfigService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleImageImporter:
    """Simple synchronous image importer"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.config_service = SecureConfigService()
        
        # Get Zoho credentials
        try:
            self.credentials = self.config_service.get_zoho_credentials()
            logger.info("✅ Zoho credentials loaded")
        except Exception as e:
            logger.error(f"❌ Error loading Zoho credentials: {e}")
            raise
        
        # Create image directories
        self.base_image_dir = Path("app/static/images/products")
        self.base_image_dir.mkdir(parents=True, exist_ok=True)
        
        # Image settings
        self.max_size = (1024, 1024)
        self.thumb_size = (300, 300)
        
        # Zoho API settings
        self.base_url = "https://www.zohoapis.com/inventory/v1"
        self.headers = {
            "Authorization": f"Zoho-oauthtoken {self.credentials.access_token}",
            "Content-Type": "application/json"
        }
    
    def get_zoho_items(self):
        """Get all items from Zoho Inventory"""
        try:
            url = f"{self.base_url}/items"
            params = {
                "organization_id": self.credentials.organization_id,
                "per_page": 200
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('items', [])
            else:
                logger.error(f"Error getting Zoho items: {response.status_code}")
                logger.error(response.text)
                return []
                
        except Exception as e:
            logger.error(f"Exception getting Zoho items: {e}")
            return []
    
    def get_item_details(self, item_id):
        """Get detailed item information including images"""
        try:
            url = f"{self.base_url}/items/{item_id}"
            params = {"organization_id": self.credentials.organization_id}
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('item', {})
            else:
                logger.warning(f"Error getting item {item_id}: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Exception getting item {item_id}: {e}")
            return {}
    
    def download_image(self, image_url, filename, product_sku):
        """Download and process a single image"""
        try:
            # Create product directory
            product_dir = self.base_image_dir / product_sku
            product_dir.mkdir(exist_ok=True)
            
            # Download image
            headers = {
                "User-Agent": "TSH-ERP-System/1.0",
                "Authorization": f"Zoho-oauthtoken {self.credentials.access_token}"
            }
            
            response = requests.get(image_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # Save original
                original_path = product_dir / f"original_{filename}"
                with open(original_path, 'wb') as f:
                    f.write(response.content)
                
                # Process image
                processed_info = self.process_image(original_path, product_dir, filename)
                
                if processed_info:
                    return {
                        'original_url': image_url,
                        'original_path': str(original_path),
                        'processed_path': processed_info['main_path'],
                        'thumbnail_path': processed_info['thumbnail_path'],
                        'downloaded_at': datetime.now().isoformat()
                    }
            else:
                logger.warning(f"Failed to download {image_url}: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error downloading {image_url}: {e}")
            
        return None
    
    def process_image(self, original_path, product_dir, filename):
        """Process and resize image"""
        try:
            with Image.open(original_path) as img:
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Main image
                img_main = img.copy()
                img_main.thumbnail(self.max_size, Image.Resampling.LANCZOS)
                main_path = product_dir / f"main_{filename}"
                img_main.save(main_path, 'JPEG', quality=85, optimize=True)
                
                # Thumbnail
                img_thumb = img.copy()
                img_thumb.thumbnail(self.thumb_size, Image.Resampling.LANCZOS)
                thumb_path = product_dir / f"thumb_{filename}"
                img_thumb.save(thumb_path, 'JPEG', quality=80, optimize=True)
                
                return {
                    'main_path': str(main_path),
                    'thumbnail_path': str(thumb_path),
                    'size': img_main.size,
                    'format': 'JPEG'
                }
                
        except Exception as e:
            logger.error(f"Error processing image {original_path}: {e}")
            return None
    
    def import_images_for_product(self, product, zoho_items):
        """Import images for a specific product"""
        try:
            # Find matching Zoho item
            zoho_item = None
            
            for item in zoho_items:
                if (item.get('sku') == product.sku or 
                    item.get('name', '').lower() == product.name.lower()):
                    zoho_item = item
                    break
            
            if not zoho_item:
                logger.info(f"⚠️ No Zoho match for product: {product.sku}")
                return False
            
            # Get detailed item info
            item_details = self.get_item_details(zoho_item['item_id'])
            
            if not item_details:
                logger.warning(f"⚠️ No details for Zoho item: {zoho_item['item_id']}")
                return False
            
            # Look for images
            image_urls = []
            
            # Primary image
            if item_details.get('image_name'):
                # Zoho image URL format
                img_url = f"{self.base_url}/items/{zoho_item['item_id']}/image"
                image_urls.append(img_url)
            
            # Additional images from item details
            if 'images' in item_details:
                for img in item_details.get('images', []):
                    if isinstance(img, dict) and 'image_url' in img:
                        image_urls.append(img['image_url'])
            
            if not image_urls:
                logger.info(f"ℹ️ No images found for product: {product.sku}")
                return False
            
            logger.info(f"📷 Found {len(image_urls)} images for {product.sku}")
            
            # Download images
            downloaded_images = []
            for idx, image_url in enumerate(image_urls):
                filename = f"img_{idx+1}_{hashlib.md5(image_url.encode()).hexdigest()[:8]}.jpg"
                
                image_info = self.download_image(image_url, filename, product.sku)
                
                if image_info:
                    downloaded_images.append(image_info)
                    logger.info(f"  ✅ Downloaded image {idx+1}")
                else:
                    logger.warning(f"  ❌ Failed to download image {idx+1}")
                
                # Small delay
                time.sleep(0.5)
            
            if downloaded_images:
                # Update product
                primary_image = downloaded_images[0]
                
                # Set primary image URL
                product.image_url = f"/static/images/products/{product.sku}/main_{Path(primary_image['processed_path']).name}"
                
                # Set all images
                product.images = [
                    {
                        'url': f"/static/images/products/{product.sku}/main_{Path(img['processed_path']).name}",
                        'thumbnail': f"/static/images/products/{product.sku}/thumb_{Path(img['thumbnail_path']).name}",
                        'original_url': img['original_url'],
                        'downloaded_at': img['downloaded_at']
                    }
                    for img in downloaded_images
                ]
                
                # Add Zoho reference
                if not product.tags:
                    product.tags = []
                
                product.tags.append({
                    'zoho_item_id': zoho_item['item_id'],
                    'images_imported_at': datetime.now().isoformat()
                })
                
                # Save to database
                self.db.commit()
                
                logger.info(f"✅ Updated product {product.sku} with {len(downloaded_images)} images")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error importing images for {product.sku}: {e}")
            self.db.rollback()
            return False
    
    def run_import(self, limit=None):
        """Run the complete import process"""
        try:
            logger.info("🔄 Starting Zoho product image import...")
            
            # Get Zoho items
            logger.info("📦 Getting items from Zoho...")
            zoho_items = self.get_zoho_items()
            
            if not zoho_items:
                logger.error("❌ No items found in Zoho")
                return
            
            logger.info(f"📦 Found {len(zoho_items)} items in Zoho")
            
            # Get products from database
            query = self.db.query(Product)
            if limit:
                query = query.limit(limit)
            
            products = query.all()
            logger.info(f"📦 Found {len(products)} products in TSH ERP")
            
            # Process products
            results = {
                'total': len(products),
                'successful': 0,
                'failed': 0,
                'no_match': 0
            }
            
            for idx, product in enumerate(products, 1):
                logger.info(f"\n[{idx}/{len(products)}] Processing: {product.sku} - {product.name}")
                
                success = self.import_images_for_product(product, zoho_items)
                
                if success:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                
                # Progress update
                if idx % 10 == 0:
                    logger.info(f"📊 Progress: {idx}/{len(products)} - Success: {results['successful']}")
            
            # Final results
            logger.info("\n" + "="*60)
            logger.info("🎉 IMPORT COMPLETED!")
            logger.info("="*60)
            logger.info(f"📊 Total Products: {results['total']}")
            logger.info(f"✅ Successful: {results['successful']}")
            logger.info(f"❌ Failed: {results['failed']}")
            logger.info("="*60)
            
        except Exception as e:
            logger.error(f"Fatal error in import: {e}")
        finally:
            self.db.close()


def main():
    """Main function"""
    print("🚀 TSH ERP System - Zoho Image Importer")
    print("="*50)
    
    try:
        importer = SimpleImageImporter()
        
        # Ask for limit
        limit_input = input("Enter max products to process (or press Enter for all): ").strip()
        limit = int(limit_input) if limit_input else None
        
        # Run import
        importer.run_import(limit=limit)
        
    except KeyboardInterrupt:
        print("\n❌ Import cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
