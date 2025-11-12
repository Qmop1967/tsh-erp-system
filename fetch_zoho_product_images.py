"""
Fetch Product Images from Zoho Books
Updates TSH ERP database with product image URLs from Zoho
"""
import asyncio
import httpx
import asyncpg
import logging

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


async def fetch_all_zoho_items_with_images(access_token):
    """Fetch ALL items from Zoho Books with their images"""
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

            # Extract only items with images
            items_with_images = [
                item for item in items
                if item.get('image_url') or item.get('image_name')
            ]

            all_items.extend(items_with_images)
            logger.info(f"Page {page}: {len(items_with_images)} items with images (Total: {len(all_items)})")

            if not data.get('page_context', {}).get('has_more_page'):
                break

            page += 1
            await asyncio.sleep(0.5)  # Rate limiting

    logger.info(f"✅ Fetched {len(all_items)} items with images from Zoho")
    return all_items


async def update_product_images(items_with_images):
    """Update database with product images"""
    conn = await asyncpg.connect(**DB_CONFIG)

    success_count = 0
    failure_count = 0
    not_found_count = 0

    try:
        for idx, item in enumerate(items_with_images, 1):
            try:
                zoho_item_id = item.get('item_id')
                image_url = item.get('image_url')
                image_name = item.get('image_name')
                image_type = item.get('image_type')

                if not zoho_item_id:
                    failure_count += 1
                    continue

                # Check if product exists
                existing = await conn.fetchval(
                    "SELECT id FROM products WHERE zoho_item_id = $1",
                    zoho_item_id
                )

                if existing:
                    # Update image
                    await conn.execute("""
                        UPDATE products SET
                            image_url = $1,
                            image_name = $2,
                            image_type = $3,
                            updated_at = NOW()
                        WHERE zoho_item_id = $4
                    """, image_url, image_name, image_type, zoho_item_id)
                    success_count += 1

                    if idx % 50 == 0:
                        logger.info(f"Progress: {idx}/{len(items_with_images)} - Updated: {success_count}")
                else:
                    not_found_count += 1

            except Exception as e:
                logger.error(f"Failed to update image for {item.get('item_id')}: {e}")
                failure_count += 1

    finally:
        await conn.close()

    logger.info(f"""
    ==========================================
    IMAGE UPDATE COMPLETE!
    ==========================================
    Total Items:        {len(items_with_images)}
    Updated:            {success_count}
    Not Found in DB:    {not_found_count}
    Failed:             {failure_count}
    ==========================================
    """)

    return success_count, failure_count


async def main():
    """Main function"""
    logger.info("🚀 Starting Zoho product images fetch...")

    # Get access token
    logger.info("🔑 Getting Zoho access token...")
    access_token = await get_access_token()

    # Fetch items with images
    logger.info("📸 Fetching items with images from Zoho Books...")
    items_with_images = await fetch_all_zoho_items_with_images(access_token)

    # Update database
    logger.info("💾 Updating database with product images...")
    await update_product_images(items_with_images)

    logger.info("✅ Image update complete!")


if __name__ == "__main__":
    asyncio.run(main())
