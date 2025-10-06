"""
Product Image Assignment Script
Assigns available product images to products based on best match
"""
import os
from pathlib import Path
from app.db.database import SessionLocal
from app.models.product import Product

def get_available_images():
    """Get list of all available product images"""
    images_dir = Path("frontend/public/images/products")
    if not images_dir.exists():
        print(f"❌ Images directory not found: {images_dir}")
        return []

    images = []
    for img_file in images_dir.glob("*.jpg"):
        barcode = img_file.stem  # filename without extension
        images.append(barcode)

    return images

def assign_images_to_products():
    """Assign first available image as placeholder to all products"""
    db = SessionLocal()

    try:
        # Get available images
        available_images = get_available_images()
        if not available_images:
            print("❌ No images found")
            return

        print(f"✅ Found {len(available_images)} product images")

        # Use first image as default placeholder
        default_barcode = available_images[0]
        print(f"📷 Using default image: {default_barcode}.jpg")

        # Get all products without barcodes
        products = db.query(Product).filter(Product.barcode == None).all()
        print(f"📦 Found {len(products)} products without barcodes")

        if not products:
            print("✅ All products already have barcodes")
            return

        # Ask for confirmation
        response = input(f"\n⚠️ Assign placeholder barcode '{default_barcode}' to {len(products)} products? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Cancelled")
            return

        # Assign placeholder barcode to all products
        updated_count = 0
        for product in products:
            product.barcode = default_barcode
            updated_count += 1

        db.commit()
        print(f"\n✅ Updated {updated_count} products with placeholder barcode")
        print(f"🎯 All products will now show image: /public/images/products/{default_barcode}.jpg")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Product Image Assignment Script")
    print("=" * 60)
    assign_images_to_products()
    print("\n✅ Done! Restart backend to see changes.")
