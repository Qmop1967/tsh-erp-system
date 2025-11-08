from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime

from app.db.database import get_db

router = APIRouter()

@router.get("/price-lists")
async def get_price_lists(
    db: Session = Depends(get_db)
):
    """
    💰 Multi-Price System - 5 Tier Pricing for TSH ERP
    Critical for 500 wholesale clients and partner network
    """
    
    try:
        # Mock price lists for the 5-tier pricing system
        price_lists = [
            {
                "id": 1,
                "name": "wholesale_a",
                "price_list_type": "wholesale_a",
                "description": "Wholesale A - High Volume Clients (>$10K/month)",
                "minimum_order_value": 1000.0,
                "discount_percentage": 15.0,
                "is_active": True,
                "valid_from": "2025-01-01T00:00:00",
                "valid_to": None,
                "product_count": 2847,
                "customer_categories": ["wholesale_a"],
                "created_at": "2025-01-01T00:00:00",
                "customers_count": 125,
                "monthly_volume": "$2.5M USD"
            },
            {
                "id": 2,
                "name": "wholesale_b",
                "price_list_type": "wholesale_b", 
                "description": "Wholesale B - Medium Volume Clients ($5K-$10K/month)",
                "minimum_order_value": 500.0,
                "discount_percentage": 12.0,
                "is_active": True,
                "valid_from": "2025-01-01T00:00:00",
                "valid_to": None,
                "product_count": 2847,
                "customer_categories": ["wholesale_b"],
                "created_at": "2025-01-01T00:00:00",
                "customers_count": 185,
                "monthly_volume": "$1.4M USD"
            },
            {
                "id": 3,
                "name": "retailer",
                "price_list_type": "retailer",
                "description": "Retailer Shop - Small Retail Businesses",
                "minimum_order_value": 200.0,
                "discount_percentage": 8.0,
                "is_active": True,
                "valid_from": "2025-01-01T00:00:00",
                "valid_to": None,
                "product_count": 2847,
                "customer_categories": ["retailer"],
                "created_at": "2025-01-01T00:00:00",
                "customers_count": 145,
                "monthly_volume": "$650K USD"
            },
            {
                "id": 4,
                "name": "technical",
                "price_list_type": "technical",
                "description": "Technical - Specialized Technical Products",
                "minimum_order_value": 100.0,
                "discount_percentage": 18.0,
                "is_active": True,
                "valid_from": "2025-01-01T00:00:00",
                "valid_to": None,
                "product_count": 856,
                "customer_categories": ["technical"],
                "created_at": "2025-01-01T00:00:00",
                "customers_count": 35,
                "monthly_volume": "$280K USD"
            },
            {
                "id": 5,
                "name": "consumer",
                "price_list_type": "consumer",
                "description": "Consumer - End User Retail Pricing",
                "minimum_order_value": 50.0,
                "discount_percentage": 3.0,
                "is_active": True,
                "valid_from": "2025-01-01T00:00:00",
                "valid_to": None,
                "product_count": 1845,
                "customer_categories": ["consumer"],
                "created_at": "2025-01-01T00:00:00",
                "customers_count": 10,
                "monthly_volume": "$45K USD"
            }
        ]
        
        return {
            "price_lists": price_lists,
            "total": len(price_lists),
            "status": "operational",
            "system_info": {
                "total_customers": 500,
                "total_products": 2847,
                "monthly_revenue": "$4.875M USD",
                "price_tiers": 5,
                "last_updated": datetime.now().isoformat()
            },
            "business_impact": {
                "wholesale_clients": 310,
                "retail_customers": 190,
                "average_order_wholesale": "$3,250 USD",
                "average_order_retail": "$185 USD",
                "conversion_rate": "94.2%"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get price lists: {str(e)}")

@router.get("/dashboard")
async def get_pricing_dashboard(
    db: Session = Depends(get_db)
):
    """
    📊 Multi-Price System Dashboard
    """
    
    try:
        return {
            "status": "operational",
            "pricing_tiers": {
                "wholesale_a": {"customers": 125, "avg_discount": "15%", "volume": "$2.5M"},
                "wholesale_b": {"customers": 185, "avg_discount": "12%", "volume": "$1.4M"},
                "retailer": {"customers": 145, "avg_discount": "8%", "volume": "$650K"},
                "technical": {"customers": 35, "avg_discount": "18%", "volume": "$280K"},
                "consumer": {"customers": 10, "avg_discount": "3%", "volume": "$45K"}
            },
            "recent_updates": {
                "price_changes_today": 24,
                "new_negotiations": 8,
                "pending_approvals": 3
            },
            "performance_metrics": {
                "profit_margin": "22.5%",
                "pricing_accuracy": "98.7%",
                "customer_satisfaction": "94.2%",
                "negotiation_success_rate": "87.3%"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pricing dashboard: {str(e)}") 