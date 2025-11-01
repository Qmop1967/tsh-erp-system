"""
Zoho API Proxy Router
Provides endpoints for proxying requests to Zoho APIs, including image fetching
"""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
import httpx
import logging
import os
from typing import Optional

from app.services.zoho_token_manager import get_token_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/zoho", tags=["Zoho Proxy"])


@router.get("/image/{item_id}")
async def get_item_image(item_id: str):
    """
    Fetch and serve product image from Zoho Inventory
    Acts as a proxy to avoid CORS issues and provide caching
    Uses automatic token refresh to ensure images are always accessible
    """
    try:
        # Directly reload token from .env file for maximum freshness
        from dotenv import load_dotenv
        load_dotenv(override=True)
        token = os.getenv("ZOHO_ACCESS_TOKEN")

        if not token:
            raise HTTPException(status_code=500, detail="Unable to obtain valid Zoho token")

        # Get organization ID from environment
        organization_id = os.getenv("ZOHO_ORGANIZATION_ID", "748369814")
        inventory_api_base = "https://www.zohoapis.com/inventory/v1"

        # Construct Zoho API URL for image
        image_url = f"{inventory_api_base}/items/{item_id}/image"

        params = {
            "organization_id": organization_id
        }

        headers = {
            "Authorization": f"Zoho-oauthtoken {token}"
        }

        # Fetch image from Zoho
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(image_url, params=params, headers=headers)

            # Check if request was successful
            if response.status_code == 200:
                # Return image with appropriate content type
                content_type = response.headers.get("content-type", "image/jpeg")

                return Response(
                    content=response.content,
                    media_type=content_type,
                    headers={
                        "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                        "Access-Control-Allow-Origin": "*",  # Allow CORS
                    }
                )
            elif response.status_code == 404:
                # Image not found in Zoho - return placeholder
                raise HTTPException(status_code=404, detail="Image not found in Zoho")
            elif response.status_code == 401:
                # Unauthorized - token might be expired
                logger.error(f"Zoho API unauthorized - token might be expired")
                raise HTTPException(status_code=500, detail="Zoho API authentication failed")
            else:
                logger.error(f"Zoho API returned status {response.status_code}: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to fetch image from Zoho: {response.status_code}"
                )

    except httpx.TimeoutException:
        logger.error(f"Timeout fetching image for item {item_id}")
        raise HTTPException(status_code=504, detail="Timeout fetching image from Zoho")
    except httpx.RequestError as e:
        logger.error(f"Request error fetching image for item {item_id}: {str(e)}")
        raise HTTPException(status_code=502, detail=f"Error connecting to Zoho API: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching image for item {item_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for Zoho proxy"""
    try:
        token_manager = get_token_manager()
        organization_id = os.getenv("ZOHO_ORGANIZATION_ID", "748369814")

        # Test if token is valid
        is_valid = await token_manager.test_token()

        return {
            "status": "ok" if is_valid else "token_invalid",
            "zoho_configured": True,
            "organization_id": organization_id,
            "token_valid": is_valid
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
