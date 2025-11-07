"""
Image Download and CDN Upload Service
Handles downloading images from Zoho and uploading to CDN or local storage
"""
import os
import hashlib
import logging
from pathlib import Path
from typing import Optional, Tuple
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)


class ImageService:
    """
    Service for managing product images
    """

    # Local storage configuration
    LOCAL_STORAGE_PATH = os.getenv("IMAGE_STORAGE_PATH", "/var/www/html/images/products")
    PUBLIC_URL_BASE = os.getenv("IMAGE_PUBLIC_URL", "https://erp.tsh.sale/images/products")

    # CDN configuration (if using external CDN)
    USE_CDN = os.getenv("USE_CDN", "false").lower() == "true"
    CDN_ENDPOINT = os.getenv("CDN_ENDPOINT")
    CDN_API_KEY = os.getenv("CDN_API_KEY")

    @classmethod
    def _ensure_storage_directory(cls):
        """Ensure the local storage directory exists"""
        Path(cls.LOCAL_STORAGE_PATH).mkdir(parents=True, exist_ok=True)

    @classmethod
    def _generate_filename(cls, item_id: str, image_data: bytes) -> str:
        """
        Generate a unique filename for the image

        Args:
            item_id: Zoho item ID
            image_data: Image binary data

        Returns:
            Filename (e.g., "item_12345_abc123.jpg")
        """
        # Create hash of image data for uniqueness
        image_hash = hashlib.md5(image_data).hexdigest()[:8]

        # Detect file extension from image data
        extension = cls._detect_image_extension(image_data)

        return f"item_{item_id}_{image_hash}.{extension}"

    @classmethod
    def _detect_image_extension(cls, image_data: bytes) -> str:
        """
        Detect image file extension from binary data

        Args:
            image_data: Image binary data

        Returns:
            File extension (jpg, png, etc.)
        """
        # Check magic bytes
        if image_data.startswith(b'\xff\xd8\xff'):
            return "jpg"
        elif image_data.startswith(b'\x89PNG'):
            return "png"
        elif image_data.startswith(b'GIF'):
            return "gif"
        elif image_data.startswith(b'WEBP'):
            return "webp"
        else:
            # Default to jpg
            return "jpg"

    @classmethod
    async def download_and_store_image(
        cls,
        item_id: str,
        image_url: str,
        headers: Optional[dict] = None
    ) -> Optional[Tuple[str, str]]:
        """
        Download image from URL and store locally or on CDN

        Args:
            item_id: Zoho item ID
            image_url: URL to download image from
            headers: Optional HTTP headers for authenticated download

        Returns:
            Tuple of (local_path, public_url) or None if failed
        """
        try:
            # Download image
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(image_url, headers=headers or {})
                response.raise_for_status()

                image_data = response.content

            if not image_data:
                logger.warning(f"No image data downloaded for item {item_id}")
                return None

            logger.info(f"Downloaded image for item {item_id} ({len(image_data)} bytes)")

            # Store locally or on CDN
            if cls.USE_CDN and cls.CDN_ENDPOINT:
                return await cls._upload_to_cdn(item_id, image_data)
            else:
                return cls._store_locally(item_id, image_data)

        except Exception as e:
            logger.error(f"Failed to download/store image for item {item_id}: {e}")
            return None

    @classmethod
    def _store_locally(cls, item_id: str, image_data: bytes) -> Tuple[str, str]:
        """
        Store image in local filesystem

        Args:
            item_id: Zoho item ID
            image_data: Image binary data

        Returns:
            Tuple of (local_path, public_url)
        """
        cls._ensure_storage_directory()

        # Generate filename
        filename = cls._generate_filename(item_id, image_data)
        local_path = os.path.join(cls.LOCAL_STORAGE_PATH, filename)

        # Write file
        with open(local_path, 'wb') as f:
            f.write(image_data)

        logger.info(f"Stored image locally: {local_path}")

        # Generate public URL
        public_url = f"{cls.PUBLIC_URL_BASE}/{filename}"

        return local_path, public_url

    @classmethod
    async def _upload_to_cdn(cls, item_id: str, image_data: bytes) -> Optional[Tuple[str, str]]:
        """
        Upload image to CDN

        Args:
            item_id: Zoho item ID
            image_data: Image binary data

        Returns:
            Tuple of (cdn_path, public_url) or None if failed
        """
        if not cls.CDN_ENDPOINT or not cls.CDN_API_KEY:
            logger.warning("CDN configuration missing, falling back to local storage")
            return cls._store_locally(item_id, image_data)

        try:
            filename = cls._generate_filename(item_id, image_data)

            # Upload to CDN (implementation depends on CDN provider)
            # This is a generic example - adjust based on your CDN
            async with httpx.AsyncClient(timeout=60.0) as client:
                files = {'file': (filename, image_data)}
                headers = {'Authorization': f'Bearer {cls.CDN_API_KEY}'}

                response = await client.post(
                    f"{cls.CDN_ENDPOINT}/upload",
                    files=files,
                    headers=headers
                )

                response.raise_for_status()
                cdn_data = response.json()

                cdn_url = cdn_data.get('url')
                cdn_path = cdn_data.get('path')

                logger.info(f"Uploaded image to CDN: {cdn_url}")

                return cdn_path, cdn_url

        except Exception as e:
            logger.error(f"CDN upload failed for item {item_id}: {e}")
            # Fallback to local storage
            return cls._store_locally(item_id, image_data)

    @classmethod
    async def download_image_from_bytes(cls, item_id: str, image_data: bytes) -> Optional[Tuple[str, str]]:
        """
        Store image from binary data (already downloaded)

        Args:
            item_id: Zoho item ID
            image_data: Image binary data

        Returns:
            Tuple of (local_path, public_url) or None if failed
        """
        try:
            if cls.USE_CDN and cls.CDN_ENDPOINT:
                return await cls._upload_to_cdn(item_id, image_data)
            else:
                return cls._store_locally(item_id, image_data)
        except Exception as e:
            logger.error(f"Failed to store image for item {item_id}: {e}")
            return None

    @classmethod
    def delete_local_image(cls, filename: str) -> bool:
        """
        Delete an image from local storage

        Args:
            filename: Image filename to delete

        Returns:
            True if deleted successfully
        """
        try:
            file_path = os.path.join(cls.LOCAL_STORAGE_PATH, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted local image: {filename}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete image {filename}: {e}")
            return False

    @classmethod
    def get_image_public_url(cls, filename: str) -> str:
        """
        Get public URL for a stored image

        Args:
            filename: Image filename

        Returns:
            Public URL
        """
        return f"{cls.PUBLIC_URL_BASE}/{filename}"
