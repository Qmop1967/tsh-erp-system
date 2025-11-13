#!/bin/bash
# Automated Product Data Verification
# Verifies stock, prices, and images after sync

set -e

echo "=================================="
echo "Product Data Verification"
echo "=================================="
echo ""

# Check stock
echo "📦 Stock Verification:"
STOCK_COUNT=$(docker compose -f /home/deploy/TSH_ERP_Ecosystem/docker-compose.yml exec -T tsh_postgres psql -U tsh_admin -d tsh_erp -t -c \
  "SELECT COUNT(*) FROM products WHERE is_active = true AND actual_available_stock > 0;" 2>/dev/null | tr -d ' ')
echo "  Products with stock: $STOCK_COUNT"

NULL_STOCK=$(docker compose -f /home/deploy/TSH_ERP_Ecosystem/docker-compose.yml exec -T tsh_postgres psql -U tsh_admin -d tsh_erp -t -c \
  "SELECT COUNT(*) FROM products WHERE is_active = true AND actual_available_stock IS NULL;" 2>/dev/null | tr -d ' ')
if [ "$NULL_STOCK" -gt 0 ]; then
    echo "  ⚠️  Products with NULL stock: $NULL_STOCK"
else
    echo "  ✅ All products have stock data"
fi

# Check prices
echo ""
echo "💰 Price Verification:"
PRICE_COUNT=$(docker compose -f /home/deploy/TSH_ERP_Ecosystem/docker-compose.yml exec -T tsh_postgres psql -U tsh_admin -d tsh_erp -t -c \
  "SELECT COUNT(*) FROM product_prices pp JOIN pricing_lists pl ON pp.pricing_list_id = pl.id WHERE pl.code = 'consumer_iqd';" 2>/dev/null | tr -d ' ')
echo "  Consumer prices: $PRICE_COUNT"

if [ "$PRICE_COUNT" -eq 0 ]; then
    echo "  ❌ NO CONSUMER PRICES! Run: ./scripts/migrate_consumer_prices.sh"
else
    echo "  ✅ Consumer prices exist"
fi

# Check images
echo ""
echo "🖼️  Image Verification:"
IMAGE_COUNT=$(docker compose -f /home/deploy/TSH_ERP_Ecosystem/docker-compose.yml exec -T tsh_postgres psql -U tsh_admin -d tsh_erp -t -c \
  "SELECT COUNT(*) FROM products WHERE image_url LIKE '/uploads/%';" 2>/dev/null | tr -d ' ')
echo "  Products with local images: $IMAGE_COUNT"

SYMLINK_COUNT=$(ls -1 /home/deploy/TSH_ERP_Ecosystem/uploads/products/264661*.jpg 2>/dev/null | wc -l)
echo "  Image symlinks: $SYMLINK_COUNT"

FILE_COUNT=$(ls -1 /home/deploy/TSH_ERP_Ecosystem/uploads/products/*_2025*.jpg 2>/dev/null | wc -l)
echo "  Downloaded image files: $FILE_COUNT"

# Test API
echo ""
echo "🌐 API Verification:"
API_RESPONSE=$(curl -s "https://erp.tsh.sale/api/consumer/products?limit=1" 2>/dev/null)
if echo "$API_RESPONSE" | grep -q '"count"'; then
    API_COUNT=$(echo "$API_RESPONSE" | python3 -c "import json, sys; d=json.load(sys.stdin); print(d.get('count', 0))" 2>/dev/null || echo "0")
    echo "  ✅ Consumer API responding"
    echo "  Products available via API: $API_COUNT"
else
    echo "  ❌ Consumer API error"
fi

# Test critical products
echo ""
echo "🎯 Critical Products Test:"
for SKU in "tsh00059y" "AKS-YB-BL-3M" "tsh00057"; do
    PRODUCT_DATA=$(docker compose -f /home/deploy/TSH_ERP_Ecosystem/docker-compose.yml exec -T tsh_postgres psql -U tsh_admin -d tsh_erp -t -c \
      "SELECT zoho_item_id, actual_available_stock FROM products WHERE sku = '$SKU' AND is_active = true;" 2>/dev/null)
    
    if [ -n "$PRODUCT_DATA" ]; then
        ZOHO_ID=$(echo "$PRODUCT_DATA" | awk '{print $1}')
        STOCK=$(echo "$PRODUCT_DATA" | awk '{print $2}')
        echo "  $SKU: Stock=$STOCK, Image=$([ -f /home/deploy/TSH_ERP_Ecosystem/uploads/products/${ZOHO_ID}.jpg ] && echo '✅' || echo '❌')"
    else
        echo "  $SKU: ❌ Not found"
    fi
done

echo ""
echo "=================================="
echo "Verification Complete"
echo "=================================="

