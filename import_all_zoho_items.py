"""
Direct Zoho to TSH ERP Import Script
Imports ALL 2,221 items from Zoho Books with maximum tolerance for data quality issues
"""
import asyncio
import httpx
import asyncpg
import logging
from decimal import Decimal, InvalidOperation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
ZOHO_CLIENT_ID = "1000.SLY5X93N58VN46HXQIIZSOQKG8J3ZJ"
ZOHO_CLIENT_SECRET = "0581c245cd951e1453042ff2bcf223768e128fed9f"
ZOHO_REFRESH_TOKEN = "1000.456d43e0209a40ba2d580747be746a54.1aa75b48b965e8a8562dc89d2a15e517"
ZOHO_ORG_ID = "748369814"

DB_CONFIG = {
    'host': 'tsh_postgres',
    'port': 5432,
    'database': 'tsh_erp',
    'user': 'tsh_admin',
    'password': 'TSH@2025Secure!Production'
}


def safe_value(value, value_type='str', default=None):
    """Safely convert value to specified type"""
    try:
        if value is None or value == '' or str(value).strip() == '':
            return default

        if value_type == 'str':
            return str(value).strip()[:500]
        elif value_type == 'int':
            return int(float(str(value).replace(',', '')))
        elif value_type == 'float':
            return float(str(value).replace(',', ''))
        elif value_type == 'bool':
            if isinstance(value, bool):
                return value
            return str(value).lower() in ['true', '1', 'yes', 'active']
        return value
    except Exception as e:
        logger.warning(f"Conversion error for {value} to {value_type}: {e}")
        return default


async def get_access_token():
    """Get fresh Zoho access token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://accounts.zoho.com/oauth/v2/token',
            data={
                'refresh_token': ZOHO_REFRESH_TOKEN,
                'client_id': ZOHO_CLIENT_ID,
                'client_secret': ZOHO_CLIENT_SECRET,
                'grant_type': 'refresh_token'
            }
        )
        if response.status_code == 200:
            return response.json()['access_token']
        raise Exception(f"Failed to get access token: {response.text}")


async def fetch_all_zoho_items(access_token):
    """Fetch ALL items from Zoho Books"""
    all_items = []
    page = 1
    headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}

    async with httpx.AsyncClient(timeout=60.0) as client:
        while True:
            logger.info(f"Fetching page {page}...")
            response = await client.get(
                f'https://www.zohoapis.com/books/v3/items',
                params={
                    'organization_id': ZOHO_ORG_ID,
                    'page': page,
                    'per_page': 200
                },
                headers=headers
            )

            if response.status_code != 200:
                logger.error(f"Failed to fetch page {page}: {response.text}")
                break

            data = response.json()
            items = data.get('items', [])
            all_items.extend(items)

            logger.info(f"Page {page}: {len(items)} items (Total: {len(all_items)})")

            if not data.get('page_context', {}).get('has_more_page'):
                break

            page += 1
            await asyncio.sleep(0.5)  # Rate limiting

    logger.info(f"✅ Fetched {len(all_items)} items from Zoho")
    return all_items


async def import_items_to_db(items):
    """Import all items to TSH ERP database"""
    # Connect to database
    conn = await asyncpg.connect(**DB_CONFIG)

    success_count = 0
    failure_count = 0
    update_count = 0
    insert_count = 0

    try:
        for idx, item in enumerate(items, 1):
            try:
                # Extract data with maximum tolerance
                zoho_item_id = safe_value(item.get('item_id'), 'str')
                if not zoho_item_id:
                    logger.warning(f"Skipping item without ID: {item}")
                    failure_count += 1
                    continue

                # Generate fallbacks for required fields
                sku = safe_value(item.get('sku'), 'str') or f"ZOHO-{zoho_item_id}"
                name = safe_value(item.get('name'), 'str') or f"Product {zoho_item_id}"

                # Prepare product data
                product_data = {
                    'zoho_item_id': zoho_item_id,
                    'sku': sku[:100],
                    'name': name[:255],
                    'description': safe_value(item.get('description'), 'str', '')[:1000],
                    'category': safe_value(item.get('category_name'), 'str', 'Uncategorized')[:100],
                    'price': safe_value(item.get('rate'), 'float', 0.0),
                    'cost_price': safe_value(item.get('purchase_rate'), 'float', 0.0),
                    'unit_price': safe_value(item.get('rate'), 'float', 0.0),
                    'actual_available_stock': safe_value(item.get('actual_available_stock'), 'int', 0),
                    'image_url': safe_value(item.get('image_url'), 'str'),
                    'is_active': item.get('status') == 'active',
                    'unit_of_measure': safe_value(item.get('unit'), 'str', 'piece')[:50],
                    'brand': safe_value(item.get('brand'), 'str'),
                    'is_trackable': safe_value(item.get('is_combo_product'), 'bool', False) == False,
                }

                # Check if product exists
                existing = await conn.fetchval(
                    "SELECT id FROM products WHERE zoho_item_id = $1",
                    zoho_item_id
                )

                if existing:
                    # Update existing
                    await conn.execute("""
                        UPDATE products SET
                            sku = $1, name = $2, description = $3, category = $4,
                            price = $5, cost_price = $6, unit_price = $7,
                            actual_available_stock = $8, image_url = $9,
                            is_active = $10, unit_of_measure = $11,
                            brand = $12, is_trackable = $13, updated_at = NOW()
                        WHERE zoho_item_id = $14
                    """,
                        product_data['sku'], product_data['name'],
                        product_data['description'], product_data['category'],
                        product_data['price'], product_data['cost_price'],
                        product_data['unit_price'], product_data['actual_available_stock'],
                        product_data['image_url'], product_data['is_active'],
                        product_data['unit_of_measure'], product_data['brand'],
                        product_data['is_trackable'], zoho_item_id
                    )
                    update_count += 1
                else:
                    # Get/create default category
                    category_id = await conn.fetchval(
                        "SELECT id FROM categories WHERE name = 'General' LIMIT 1"
                    )
                    if not category_id:
                        category_id = await conn.fetchval(
                            "INSERT INTO categories (name, is_active, created_at) VALUES ('General', true, NOW()) RETURNING id"
                        )

                    # Insert new product
                    await conn.execute("""
                        INSERT INTO products (
                            zoho_item_id, sku, name, description, category, category_id,
                            price, cost_price, unit_price, actual_available_stock,
                            image_url, is_active, unit_of_measure, brand, is_trackable,
                            created_at, updated_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, NOW(), NOW())
                    """,
                        product_data['zoho_item_id'], product_data['sku'],
                        product_data['name'], product_data['description'],
                        product_data['category'], category_id,
                        product_data['price'], product_data['cost_price'],
                        product_data['unit_price'], product_data['actual_available_stock'],
                        product_data['image_url'], product_data['is_active'],
                        product_data['unit_of_measure'], product_data['brand'],
                        product_data['is_trackable']
                    )
                    insert_count += 1

                success_count += 1

                if idx % 100 == 0:
                    logger.info(f"Progress: {idx}/{len(items)} - Success: {success_count}, Failed: {failure_count}")

            except Exception as e:
                logger.error(f"Failed to import item {item.get('item_id')}: {e}")
                failure_count += 1
                continue

    finally:
        await conn.close()

    logger.info(f"""
    ==========================================
    IMPORT COMPLETE!
    ==========================================
    Total Items:    {len(items)}
    Successful:     {success_count}
    Failed:         {failure_count}
    New Inserts:    {insert_count}
    Updates:        {update_count}
    ==========================================
    """)

    return success_count, failure_count


async def main():
    """Main import function"""
    logger.info("🚀 Starting direct Zoho to TSH ERP import...")

    # Get access token
    logger.info("🔑 Getting Zoho access token...")
    access_token = await get_access_token()

    # Fetch all items
    logger.info("📦 Fetching all items from Zoho Books...")
    items = await fetch_all_zoho_items(access_token)

    # Import to database
    logger.info("💾 Importing to TSH ERP database...")
    await import_items_to_db(items)

    logger.info("✅ Import complete!")


if __name__ == "__main__":
    asyncio.run(main())
