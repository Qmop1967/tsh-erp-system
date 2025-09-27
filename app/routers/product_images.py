"""
Product Image Management Router
موجه إدارة صور المنتجات

FastAPI router for managing product images including upload, download, and Zoho import
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from pathlib import Path
import asyncio
import json
from datetime import datetime

from app.db.database import get_db
from app.models.product import Product
from app.schemas.product import ProductResponse
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/products", tags=["Product Images"])

# Image directory configuration
STATIC_DIR = Path("app/static")
IMAGES_DIR = STATIC_DIR / "images" / "products"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Allowed image types
ALLOWED_IMAGE_TYPES = {
    "image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"
}

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB


@router.get("/{product_id}/images")
async def get_product_images(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get all images for a product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "product_id": product_id,
        "product_sku": product.sku,
        "primary_image": product.image_url,
        "images": product.images or [],
        "total_images": len(product.images) if product.images else 0
    }


@router.post("/{product_id}/images/upload")
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    is_primary: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload an image for a product"""
    
    # Validate product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    # Validate file size
    if file.size and file.size > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Max size: {MAX_IMAGE_SIZE//1024//1024}MB"
        )
    
    try:
        # Create product directory
        product_dir = IMAGES_DIR / product.sku
        product_dir.mkdir(exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(file.filename).suffix.lower()
        filename = f"{timestamp}_{file.filename}"
        file_path = product_dir / filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Generate web URL
        web_url = f"/static/images/products/{product.sku}/{filename}"
        
        # Update product images
        if not product.images:
            product.images = []
        
        # Add new image info
        image_info = {
            "url": web_url,
            "filename": filename,
            "original_name": file.filename,
            "content_type": file.content_type,
            "size": file.size,
            "uploaded_at": datetime.now().isoformat(),
            "uploaded_by": current_user.username
        }
        
        product.images.append(image_info)
        
        # Set as primary image if requested or if it's the first image
        if is_primary or not product.image_url:
            product.image_url = web_url
        
        db.commit()
        
        return {
            "message": "Image uploaded successfully",
            "image_info": image_info,
            "is_primary": is_primary or not product.image_url
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")


@router.delete("/{product_id}/images/{image_index}")
async def delete_product_image(
    product_id: int,
    image_index: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a specific image from a product"""
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if not product.images or image_index >= len(product.images):
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        # Get image info
        image_info = product.images[image_index]
        
        # Delete file from filesystem
        if image_info.get('filename'):
            file_path = IMAGES_DIR / product.sku / image_info['filename']
            if file_path.exists():
                file_path.unlink()
        
        # Remove from images list
        del product.images[image_index]
        
        # If this was the primary image, set a new primary
        if product.image_url == image_info.get('url'):
            product.image_url = product.images[0]['url'] if product.images else None
        
        db.commit()
        
        return {"message": "Image deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting image: {str(e)}")


@router.put("/{product_id}/images/{image_index}/set-primary")
async def set_primary_image(
    product_id: int,
    image_index: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Set a specific image as the primary image"""
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if not product.images or image_index >= len(product.images):
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Set new primary image
    product.image_url = product.images[image_index]['url']
    db.commit()
    
    return {
        "message": "Primary image updated successfully",
        "new_primary_url": product.image_url
    }


@router.post("/{product_id}/images/import-from-zoho")
async def import_images_from_zoho(
    product_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Import images for a specific product from Zoho"""
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Add background task to import images
    background_tasks.add_task(
        import_single_product_images_background,
        product_id,
        current_user.id
    )
    
    return {
        "message": "Image import started",
        "product_id": product_id,
        "product_sku": product.sku,
        "status": "processing"
    }


@router.post("/images/import-all-from-zoho")
async def import_all_images_from_zoho(
    background_tasks: BackgroundTasks,
    limit: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """Import images for all products from Zoho (background task)"""
    
    # Add background task
    background_tasks.add_task(
        import_all_product_images_background,
        limit,
        current_user.id
    )
    
    return {
        "message": "Bulk image import started",
        "limit": limit,
        "status": "processing",
        "note": "This may take several minutes. Check logs for progress."
    }


@router.get("/images/import-status")
async def get_import_status():
    """Get the status of image import operations"""
    
    # Check for status files
    status_files = list(Path(".").glob("zoho_image_import_results_*.json"))
    
    if not status_files:
        return {"status": "no_imports_found"}
    
    # Get latest status file
    latest_file = max(status_files, key=os.path.getctime)
    
    try:
        with open(latest_file, 'r') as f:
            results = json.load(f)
        
        return {
            "status": "completed",
            "results": results,
            "results_file": str(latest_file),
            "last_updated": datetime.fromtimestamp(os.path.getctime(latest_file)).isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


# Background task functions
async def import_single_product_images_background(product_id: int, user_id: int):
    """Background task to import images for a single product"""
    try:
        from scripts.simple_zoho_image_import import SimpleImageImporter
        
        importer = SimpleImageImporter()
        
        # Get the specific product
        product = importer.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return
        
        # Get Zoho items
        zoho_items = importer.get_zoho_items()
        
        # Import images for this product
        success = importer.import_images_for_product(product, zoho_items)
        
        # Log result
        status = "successful" if success else "failed"
        print(f"Image import for product {product.sku}: {status}")
        
    except Exception as e:
        print(f"Error in background image import: {e}")


async def import_all_product_images_background(limit: Optional[int], user_id: int):
    """Background task to import images for all products"""
    try:
        from scripts.simple_zoho_image_import import SimpleImageImporter
        
        importer = SimpleImageImporter()
        importer.run_import(limit=limit)
        
    except Exception as e:
        print(f"Error in background bulk import: {e}")


# Static file serving
@router.get("/images/{product_sku}/{filename}")
async def serve_product_image(product_sku: str, filename: str):
    """Serve product image files"""
    file_path = IMAGES_DIR / product_sku / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(
        file_path,
        media_type="image/jpeg",
        headers={"Cache-Control": "public, max-age=3600"}
    )
