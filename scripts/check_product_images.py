#!/usr/bin/env python3
"""
Check Product Images Status
Query database to see which products have images and which don't
"""
import sys
sys.path.insert(0, '/Users/khaleelal-mulla/TSH_ERP_Ecosystem')

from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# URL encode the password to handle special characters
password = quote_plus('TSH@2025Secure!Production')
db_url = f'postgresql://tsh_app_user:{password}@localhost:5432/tsh_erp_production'

def check_product_images():
    """Check product image status in database"""
    engine = create_engine(db_url)

    with engine.connect() as conn:
        # Count products with/without images
        result = conn.execute(text("""
            SELECT
                COUNT(*) as total_products,
                COUNT(image_url) as with_images,
                COUNT(*) - COUNT(image_url) as without_images,
                COUNT(CASE WHEN image_url IS NOT NULL AND image_url != '' THEN 1 END) as with_valid_images
            FROM products
            WHERE is_active = true
        """))
        row = result.fetchone()

        print("=" * 60)
        print("PRODUCT IMAGE STATUS")
        print("=" * 60)
        print(f"Total Active Products:     {row[0]}")
        print(f"With Images (not null):    {row[1]}")
        print(f"With Valid Images:         {row[3]}")
        print(f"Without Images:            {row[2]}")
        print("=" * 60)

        # Sample products with Zoho IDs
        print("\nSample Products with Zoho IDs:")
        print("-" * 60)
        result = conn.execute(text("""
            SELECT id, sku, name,
                   CASE WHEN image_url IS NOT NULL AND image_url != '' THEN 'YES' ELSE 'NO' END as has_image,
                   zoho_item_id
            FROM products
            WHERE is_active = true AND zoho_item_id IS NOT NULL
            LIMIT 10
        """))

        for row in result:
            print(f"ID: {row[0]}, SKU: {row[1]}, Name: {row[2][:30]}, Has Image: {row[3]}, Zoho ID: {row[4]}")

        print("-" * 60)

        # Products without images but with Zoho IDs
        result = conn.execute(text("""
            SELECT COUNT(*)
            FROM products
            WHERE is_active = true
              AND zoho_item_id IS NOT NULL
              AND (image_url IS NULL OR image_url = '')
        """))
        count = result.fetchone()[0]
        print(f"\nProducts needing image download: {count}")
        print("=" * 60)

if __name__ == "__main__":
    check_product_images()
