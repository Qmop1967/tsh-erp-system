#!/usr/bin/env python3
"""
Create symlinks for product images based on database
Maps {zoho_item_id}.jpg to actual downloaded files
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

UPLOADS_DIR = "/home/deploy/TSH_ERP_Ecosystem/uploads/products"
DB_URL = os.getenv("DATABASE_URL", "postgresql://tsh_admin:changeme@localhost:5432/tsh_erp")

print("=" * 60)
print("Creating Product Image Symlinks from Database")
print("=" * 60)
print()

engine = create_engine(DB_URL)

# Get all products with local image URLs
query = text("""
    SELECT zoho_item_id, image_url
    FROM products
    WHERE image_url IS NOT NULL 
    AND image_url != ''
    AND image_url LIKE '/uploads/products/%'
    AND zoho_item_id IS NOT NULL
""")

created = 0
skipped = 0
errors = 0

with engine.connect() as conn:
    result = conn.execute(query)
    products = list(result)
    
    print(f"Found {len(products)} products with local images")
    print()
    
    for row in products:
        zoho_item_id = row[0]
        image_url = row[1]
        
        # Extract filename from image_url
        # e.g., /uploads/products/AKS-YB-BL-3M_20251113_011506_665236.jpg
        filename = image_url.split('/')[-1]
        source_path = Path(UPLOADS_DIR) / filename
        
        # Create symlink with zoho_item_id
        # Extract extension from source
        ext = source_path.suffix or '.jpg'
        symlink_path = Path(UPLOADS_DIR) / f"{zoho_item_id}{ext}"
        
        try:
            # Check if source exists
            if not source_path.exists():
                errors += 1
                print(f"❌ Source not found: {filename}")
                continue
            
            # Skip if symlink already exists
            if symlink_path.exists():
                skipped += 1
                continue
            
            # Create symlink
            symlink_path.symlink_to(source_path.name)
            created += 1
            
            if created % 50 == 0:
                print(f"  Created {created} symlinks...")
                
        except Exception as e:
            errors += 1
            print(f"❌ Error creating symlink for {zoho_item_id}: {e}")

print()
print("=" * 60)
print(f"✅ Created: {created}")
print(f"⏭️  Skipped: {skipped} (already exist)")
print(f"❌ Errors: {errors}")
print("=" * 60)

