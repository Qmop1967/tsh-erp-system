"""
Image Helper Utility for TSH ERP System
Provides unified image URL generation for products across all platforms
"""
import os
from typing import Optional
from pathlib import Path

# Static base URL for product images
STATIC_BASE_URL = "/public/images/products"

# Default placeholder image (first available image in directory)
DEFAULT_PLACEHOLDER = "6923172538284"  # Use any existing image as placeholder


def get_product_image_url(barcode: Optional[str] = None, sku: Optional[str] = None, base_url: str = "", use_placeholder: bool = False) -> Optional[str]:
    """
    Generate product image URL from barcode or SKU, with optional placeholder fallback

    Args:
        barcode: Product barcode (preferred)
        sku: Product SKU (fallback if barcode is None)
        base_url: API base URL (e.g., "http://192.168.68.66:8000")
        use_placeholder: If True, return placeholder image when file doesn't exist (default: False)

    Returns:
        Full image URL if image exists, or None if not found

    Example:
        >>> get_product_image_url(barcode="6923172538284", base_url="http://192.168.68.66:8000")
        'http://192.168.68.66:8000/public/images/products/6923172538284.jpg'
        >>> get_product_image_url(sku="LAP-001", base_url="http://192.168.68.66:8000")
        None  # No placeholder by default
    """
    # Try barcode first, then SKU as fallback
    identifier = barcode or sku

    # Check if image file exists for the identifier
    if identifier and check_image_exists(identifier):
        # Image exists - use it
        image_path = f"{STATIC_BASE_URL}/{identifier}.jpg"
        # Return full URL
        if base_url:
            return f"{base_url}{image_path}"
        return image_path

    # No image found - return None instead of placeholder
    return None


def check_image_exists(barcode: str) -> bool:
    """
    Check if product image file exists on filesystem

    Args:
        barcode: Product barcode

    Returns:
        True if image file exists, False otherwise
    """
    if not barcode:
        return False

    # Path to image file
    file_path = Path("frontend/public/images/products") / f"{barcode}.jpg"
    return file_path.exists()


def get_image_file_size(barcode: str) -> Optional[int]:
    """
    Get the file size of a product image

    Args:
        barcode: Product barcode

    Returns:
        File size in bytes, or None if file doesn't exist
    """
    if not barcode:
        return None

    file_path = Path("frontend/public/images/products") / f"{barcode}.jpg"
    if file_path.exists():
        return file_path.stat().st_size
    return None


def list_available_product_images() -> list[str]:
    """
    List all available product image barcodes

    Returns:
        List of barcodes that have images
    """
    images_dir = Path("frontend/public/images/products")
    if not images_dir.exists():
        return []

    barcodes = []
    for image_file in images_dir.glob("*.jpg"):
        # Extract barcode from filename (remove .jpg extension)
        barcode = image_file.stem
        barcodes.append(barcode)

    return barcodes
