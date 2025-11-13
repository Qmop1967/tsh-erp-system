#!/bin/bash
# Create symlinks for product images
# Maps {zoho_item_id}.jpg to actual files {zoho_item_id}_{timestamp}.jpg

set -e

UPLOADS_DIR="/home/deploy/TSH_ERP_Ecosystem/uploads/products"

echo "=================================="
echo "Creating Image Symlinks"
echo "=================================="
echo ""

cd "$UPLOADS_DIR"

# Count existing files
TOTAL_FILES=$(ls -1 | wc -l)
echo "📁 Found $TOTAL_FILES image files"

# Create symlinks for each unique zoho_item_id
CREATED=0
SKIPPED=0

for file in *.jpg *.jpeg *.png *.webp; do
    if [ -f "$file" ]; then
        # Extract zoho_item_id (everything before the first underscore with timestamp)
        ITEM_ID=$(echo "$file" | sed 's/_[0-9]\{8\}_.*$//')
        
        # If we extracted a valid item_id (not the same as filename)
        if [ "$ITEM_ID" != "$file" ] && [ -n "$ITEM_ID" ]; then
            SYMLINK_NAME="${ITEM_ID}.jpg"
            
            # Only create if symlink doesn't exist
            if [ ! -e "$SYMLINK_NAME" ]; then
                ln -s "$file" "$SYMLINK_NAME"
                ((CREATED++))
                
                if [ $((CREATED % 100)) -eq 0 ]; then
                    echo "  Created $CREATED symlinks..."
                fi
            else
                ((SKIPPED++))
            fi
        fi
    fi
done

echo ""
echo "✅ Created $CREATED new symlinks"
echo "⏭️  Skipped $SKIPPED (already exist)"
echo ""
echo "Total files in directory: $(ls -1 | wc -l)"
echo ""

