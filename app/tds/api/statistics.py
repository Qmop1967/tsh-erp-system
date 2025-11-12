"""
TDS Statistics API Endpoints
=============================

RESTful API for TDS statistics and comparison operations.

نقاط نهاية واجهة برمجة التطبيقات لإحصائيات TDS

Author: TSH ERP Team
Date: January 7, 2025
Version: 4.0.0
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_db
from app.tds.statistics.engine import StatisticsEngine
from app.tds.statistics.models import EntityType, FullComparisonReport
from app.utils.permissions import simple_require_permission

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/tds/statistics",
    tags=["TDS Statistics"],
    responses={404: {"description": "Not found"}},
)


# ============================================================================
# Statistics & Comparison Endpoints
# ============================================================================

@router.get("/overview")
@simple_require_permission("tds.statistics.view")
async def get_statistics_overview(
    db: Session = Depends(get_db)
):
    """
    Get high-level statistics overview

    Returns summary of items, customers, vendors, stock, price lists, and images.

    **Permissions:** `tds.statistics.view`

    **Response:**
    ```json
    {
        "zoho": {
            "items": 1523,
            "customers": 287,
            "vendors": 45,
            "price_lists": 5,
            "stock_value": 125430.50
        },
        "local": {
            "items": 1498,
            "customers": 283,
            "vendors": 44,
            "price_lists": 5,
            "stock_value": 123210.30
        },
        "match_percentage": 97.8,
        "health_score": 95.2,
        "status": "excellent",
        "last_updated": "2025-01-07T15:30:45Z"
    }
    ```
    """
    try:
        logger.info("Getting statistics overview...")

        # Initialize engine
        engine = StatisticsEngine(db=db)

        # Run comparison
        report = await engine.collect_and_compare()

        # Build response
        response = {
            "zoho": {
                "items": report.zoho_statistics.items.total_count,
                "customers": report.zoho_statistics.customers.total_count,
                "vendors": report.zoho_statistics.vendors.total_count,
                "price_lists": report.zoho_statistics.price_lists.total_lists,
                "stock_value": report.zoho_statistics.stock.total_stock_value,
                "images_with_coverage": report.zoho_statistics.images.with_images,
            },
            "local": {
                "items": report.local_statistics.items.total_count,
                "customers": report.local_statistics.customers.total_count,
                "vendors": report.local_statistics.vendors.total_count,
                "price_lists": report.local_statistics.price_lists.total_lists,
                "stock_value": report.local_statistics.stock.total_stock_value,
                "images_with_coverage": report.local_statistics.images.with_images,
            },
            "match_percentage": report.overall_match_percentage,
            "health_score": report.health_score.overall_score,
            "status": report.health_score.status,
            "last_updated": report.timestamp.isoformat(),
            "execution_time_seconds": report.execution_time_seconds,
        }

        return response

    except Exception as e:
        logger.error(f"Error getting statistics overview: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare")
@simple_require_permission("tds.statistics.view")
async def compare_zoho_vs_local(
    entity_type: Optional[str] = Query(None, description="Entity type to compare (items, customers, vendors, price_lists, stock, images)"),
    db: Session = Depends(get_db)
):
    """
    Compare Zoho data with local data

    Performs comprehensive comparison and returns detailed results.

    **Permissions:** `tds.statistics.view`

    **Query Parameters:**
    - `entity_type` (optional): Filter by specific entity type

    **Response:**
    ```json
    {
        "report_id": "uuid",
        "timestamp": "2025-01-07T15:30:45Z",
        "overall_match_percentage": 97.8,
        "health_score": {
            "overall_score": 95.2,
            "status": "excellent",
            "items_score": 98.4,
            "customers_score": 98.6,
            "...": "..."
        },
        "comparisons": {
            "items": {
                "zoho_count": 1523,
                "local_count": 1498,
                "difference": 25,
                "match_percentage": 98.4,
                "requires_sync": true,
                "sync_recommendation": "incremental_sync"
            }
        },
        "alerts": [],
        "recommendations": []
    }
    ```
    """
    try:
        logger.info(f"Comparing Zoho vs Local (entity_type={entity_type})...")

        # Initialize engine
        engine = StatisticsEngine(db=db)

        # Parse entity filter
        entities = None
        if entity_type:
            try:
                entities = [EntityType(entity_type.upper())]
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid entity_type: {entity_type}. Valid values: items, customers, vendors, price_lists, stock, images"
                )

        # Run comparison
        report = await engine.collect_and_compare(entities=entities)

        # If specific entity requested, return only that comparison
        if entity_type and entity_type in report.comparisons:
            comparison = report.comparisons[entity_type]
            return {
                "entity_type": entity_type,
                "zoho_count": comparison.zoho_count,
                "local_count": comparison.local_count,
                "difference": comparison.difference,
                "match_percentage": comparison.match_percentage,
                "match_count": comparison.match_count,
                "requires_sync": comparison.requires_sync,
                "sync_recommendation": comparison.sync_recommendation.value,
                "sync_priority": comparison.sync_priority,
                "estimated_sync_duration_minutes": comparison.estimated_sync_duration_minutes,
                "missing_in_local_count": len(comparison.missing_in_local),
                "missing_in_zoho_count": len(comparison.missing_in_zoho),
                "mismatched_count": len(comparison.mismatched_entities),
            }

        # Return full report
        return {
            "report_id": report.report_id,
            "timestamp": report.timestamp.isoformat(),
            "overall_match_percentage": report.overall_match_percentage,
            "health_score": {
                "overall_score": report.health_score.overall_score,
                "status": report.health_score.status,
                "items_score": report.health_score.items_score,
                "customers_score": report.health_score.customers_score,
                "vendors_score": report.health_score.vendors_score,
                "price_lists_score": report.health_score.price_lists_score,
                "stock_score": report.health_score.stock_score,
                "images_score": report.health_score.images_score,
                "issues": report.health_score.issues,
                "recommendations": report.health_score.recommendations,
            },
            "comparisons": {
                entity_type: {
                    "zoho_count": comp.zoho_count,
                    "local_count": comp.local_count,
                    "difference": comp.difference,
                    "match_percentage": comp.match_percentage,
                    "requires_sync": comp.requires_sync,
                    "sync_recommendation": comp.sync_recommendation.value,
                    "sync_priority": comp.sync_priority,
                }
                for entity_type, comp in report.comparisons.items()
            },
            "alerts": report.alerts,
            "sync_recommendations": report.sync_recommendations,
            "execution_time_seconds": report.execution_time_seconds,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing Zoho vs Local: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-differences")
@simple_require_permission("tds.sync.execute")
async def sync_differences(
    entity_type: Optional[str] = Query(None, description="Entity type to sync"),
    dry_run: bool = Query(False, description="Dry run mode (don't actually sync)"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Sync differences found in comparison

    **Permissions:** `tds.sync.execute`

    **Query Parameters:**
    - `entity_type` (optional): Sync only specific entity type
    - `dry_run` (optional): If true, only simulate sync without making changes

    **Response:**
    ```json
    {
        "status": "syncing",
        "entity_type": "items",
        "dry_run": false,
        "items_to_sync": 25,
        "estimated_duration_minutes": 1,
        "job_id": "uuid"
    }
    ```
    """
    try:
        logger.info(f"Syncing differences (entity_type={entity_type}, dry_run={dry_run})...")

        # Initialize engine
        engine = StatisticsEngine(db=db)

        # Run comparison first to get differences
        entities = None
        if entity_type:
            try:
                entities = [EntityType(entity_type.upper())]
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid entity_type: {entity_type}"
                )

        report = await engine.collect_and_compare(entities=entities)

        # Check if sync is needed
        if not report.requires_immediate_attention and not any(
            comp.requires_sync for comp in report.comparisons.values()
        ):
            return {
                "status": "no_sync_needed",
                "message": "All systems are in sync. No action required.",
                "match_percentage": report.overall_match_percentage,
            }

        # Perform sync
        if dry_run:
            # Dry run - just return what would be synced
            items_to_sync = sum(
                abs(comp.difference)
                for comp in report.comparisons.values()
                if comp.requires_sync
            )

            return {
                "status": "dry_run",
                "entity_type": entity_type or "all",
                "items_to_sync": items_to_sync,
                "entities_to_sync": [
                    {
                        "entity_type": entity_type,
                        "difference": comp.difference,
                        "sync_recommendation": comp.sync_recommendation.value,
                    }
                    for entity_type, comp in report.comparisons.items()
                    if comp.requires_sync
                ],
                "message": "Dry run complete. No changes made.",
            }
        else:
            # Actual sync
            await engine.auto_sync_differences(report, dry_run=False)

            return {
                "status": "synced",
                "entity_type": entity_type or "all",
                "synced_entities": [
                    entity_type
                    for entity_type, comp in report.comparisons.items()
                    if comp.requires_sync
                ],
                "message": "Sync completed successfully",
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing differences: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Detailed Entity Statistics Endpoints
# ============================================================================

@router.get("/items")
@simple_require_permission("tds.statistics.view")
async def get_items_statistics(db: Session = Depends(get_db)):
    """
    Get detailed item/product statistics

    **Permissions:** `tds.statistics.view`
    """
    try:
        engine = StatisticsEngine(db=db)
        report = await engine.collect_and_compare(entities=[EntityType.ITEMS])

        zoho_stats = report.zoho_statistics.items
        local_stats = report.local_statistics.items
        comparison = report.comparisons.get("items")

        return {
            "zoho": {
                "total_count": zoho_stats.total_count,
                "active_count": zoho_stats.active_count,
                "inactive_count": zoho_stats.inactive_count,
                "with_images": zoho_stats.with_images_count,
                "without_images": zoho_stats.without_images_count,
                "image_coverage_percentage": zoho_stats.image_coverage_percentage,
                "by_category": zoho_stats.by_category,
                "by_brand": zoho_stats.by_brand,
                "average_price": zoho_stats.average_price,
                "total_stock_value": zoho_stats.total_stock_value,
            },
            "local": {
                "total_count": local_stats.total_count,
                "active_count": local_stats.active_count,
                "inactive_count": local_stats.inactive_count,
                "with_images": local_stats.with_images_count,
                "without_images": local_stats.without_images_count,
                "image_coverage_percentage": local_stats.image_coverage_percentage,
                "by_category": local_stats.by_category,
                "average_price": local_stats.average_price,
            },
            "comparison": {
                "difference": comparison.difference,
                "match_percentage": comparison.match_percentage,
                "requires_sync": comparison.requires_sync,
                "sync_recommendation": comparison.sync_recommendation.value,
            } if comparison else None,
        }

    except Exception as e:
        logger.error(f"Error getting items statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customers")
@simple_require_permission("tds.statistics.view")
async def get_customer_statistics(db: Session = Depends(get_db)):
    """
    Get detailed customer statistics

    **Permissions:** `tds.statistics.view`
    """
    try:
        engine = StatisticsEngine(db=db)
        report = await engine.collect_and_compare(entities=[EntityType.CUSTOMERS])

        zoho_stats = report.zoho_statistics.customers
        local_stats = report.local_statistics.customers
        comparison = report.comparisons.get("customers")

        return {
            "zoho": {
                "total_count": zoho_stats.total_count,
                "active_count": zoho_stats.active_count,
                "inactive_count": zoho_stats.inactive_count,
                "by_type": zoho_stats.by_type,
                "by_country": zoho_stats.by_country,
                "by_price_list": zoho_stats.by_price_list,
                "total_credit_limit": zoho_stats.total_credit_limit,
                "average_credit_limit": zoho_stats.average_credit_limit,
                "with_outstanding_balance": zoho_stats.with_outstanding_balance,
            },
            "local": {
                "total_count": local_stats.total_count,
                "active_count": local_stats.active_count,
                "inactive_count": local_stats.inactive_count,
                "by_type": local_stats.by_type,
                "by_country": local_stats.by_country,
                "total_credit_limit": local_stats.total_credit_limit,
            },
            "comparison": {
                "difference": comparison.difference,
                "match_percentage": comparison.match_percentage,
                "requires_sync": comparison.requires_sync,
            } if comparison else None,
        }

    except Exception as e:
        logger.error(f"Error getting customer statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
@simple_require_permission("tds.statistics.view")
async def get_system_health(db: Session = Depends(get_db)):
    """
    Get system health status

    Returns health score and status for quick health checks.

    **Permissions:** `tds.statistics.view`

    **Response:**
    ```json
    {
        "overall_score": 95.2,
        "status": "excellent",
        "is_healthy": true,
        "scores": {
            "items": 98.4,
            "customers": 98.6,
            "vendors": 97.8,
            "price_lists": 100.0,
            "stock": 98.5,
            "images": 97.3
        },
        "issues": [],
        "recommendations": []
    }
    ```
    """
    try:
        engine = StatisticsEngine(db=db)
        report = await engine.collect_and_compare()

        return {
            "overall_score": report.health_score.overall_score,
            "status": report.health_score.status,
            "is_healthy": report.health_score.is_healthy,
            "scores": {
                "items": report.health_score.items_score,
                "customers": report.health_score.customers_score,
                "vendors": report.health_score.vendors_score,
                "price_lists": report.health_score.price_lists_score,
                "stock": report.health_score.stock_score,
                "images": report.health_score.images_score,
            },
            "issues": report.health_score.issues,
            "recommendations": report.health_score.recommendations,
            "timestamp": report.timestamp.isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting system health: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ["router"]
