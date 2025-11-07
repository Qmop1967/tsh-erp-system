"""
TDS Core - Prometheus Metrics Endpoint
Exports TDS Core metrics for Prometheus scraping
"""
from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db
from models.tds_models import TDSSyncQueue

router = APIRouter()


@router.get("/metrics", response_class=PlainTextResponse)
async def metrics(db: AsyncSession = Depends(get_db)):
    """
    Prometheus metrics endpoint

    Exports TDS Core queue metrics in Prometheus format
    """
    # Get queue statistics
    queue_stats = await db.execute(
        select(
            TDSSyncQueue.status,
            func.count(TDSSyncQueue.id).label('count')
        ).group_by(TDSSyncQueue.status)
    )

    # Build metrics output
    metrics_output = []

    # Add help and type info
    metrics_output.append('# HELP tds_queue_total Total number of items in TDS sync queue by status')
    metrics_output.append('# TYPE tds_queue_total gauge')

    # Add queue counts by status
    for row in queue_stats:
        status = str(row.status).lower() if hasattr(row.status, 'value') else str(row.status).lower()
        # Extract just the enum value name (e.g., "completed" from "EventStatus.COMPLETED")
        if '.' in status:
            status = status.split('.')[-1]
        count = row.count
        metrics_output.append(f'tds_queue_total{{status="{status}"}} {count}')

    # Get entity type distribution
    entity_stats = await db.execute(
        select(
            TDSSyncQueue.entity_type,
            func.count(TDSSyncQueue.id).label('count')
        ).group_by(TDSSyncQueue.entity_type)
    )

    metrics_output.append('')
    metrics_output.append('# HELP tds_queue_by_entity Total number of items by entity type')
    metrics_output.append('# TYPE tds_queue_by_entity gauge')

    for row in entity_stats:
        entity_type = str(row.entity_type).lower() if hasattr(row.entity_type, 'value') else str(row.entity_type).lower()
        # Extract just the enum value name (e.g., "product" from "EntityType.PRODUCT")
        if '.' in entity_type:
            entity_type = entity_type.split('.')[-1]
        count = row.count
        metrics_output.append(f'tds_queue_by_entity{{entity_type="{entity_type}"}} {count}')

    return '\n'.join(metrics_output) + '\n'
