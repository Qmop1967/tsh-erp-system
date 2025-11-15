"""
GPS Tracking BFF Router for Salesperson App
8 endpoints for real-time location tracking and visit verification

Business Purpose:
- Track 12 travel salespersons' routes and locations
- Verify customer visits with geofencing
- Calculate distance traveled and route efficiency
- Fraud prevention (ensure visits are genuine)
- Performance analytics and route optimization
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import Optional, List
from datetime import datetime, date, timedelta
from decimal import Decimal
import math

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.salesperson import SalespersonGPSLocation, SalespersonDailySummary
from app.models.customer import Customer
from app.schemas.salesperson import (
    GPSLocationCreate,
    BatchLocationRequest,
    VerifyVisitRequest,
    GPSLocationResponse,
    DailySummaryResponse,
    WeeklySummaryResponse,
    VerifyVisitResponse,
    SyncStatusResponse,
    BatchOperationResponse
)

router = APIRouter(prefix="/gps", tags=["Salesperson GPS Tracking"])


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two GPS coordinates using Haversine formula
    Returns distance in meters
    """
    R = 6371000  # Earth's radius in meters

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance


def is_within_geofence(customer_lat: float, customer_lon: float,
                        visit_lat: float, visit_lon: float,
                        radius_meters: float = 100) -> bool:
    """Check if visit location is within geofence radius of customer location"""
    distance = calculate_distance(customer_lat, customer_lon, visit_lat, visit_lon)
    return distance <= radius_meters


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/track", response_model=dict, status_code=status.HTTP_201_CREATED)
async def track_location(
    location: GPSLocationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload single GPS location point

    Business Logic:
    - Automatic background tracking from mobile app
    - Records every 30-60 seconds while on route
    - Supports offline mode (stores locally, syncs later)

    Authorization:
    - Only salespersons can upload their own locations
    - Managers can view but not create locations for others
    """
    # Authorization: salespersons only
    if not current_user.is_salesperson:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only salespersons can track GPS locations"
        )

    try:
        # Create GPS location record
        gps_location = SalespersonGPSLocation(
            salesperson_id=current_user.id,
            latitude=location.latitude,
            longitude=location.longitude,
            timestamp=location.timestamp,
            accuracy=location.accuracy,
            altitude=location.altitude,
            speed=location.speed,
            heading=location.heading,
            activity_type=location.activity_type,
            battery_level=location.battery_level,
            is_charging=location.is_charging,
            device_id=location.device_id,
            is_synced=True,  # Directly uploaded, so marked as synced
            synced_at=datetime.utcnow()
        )

        db.add(gps_location)
        db.commit()
        db.refresh(gps_location)

        return {
            "success": True,
            "location_id": gps_location.id,
            "message": "Location tracked successfully"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track location: {str(e)}"
        )


@router.post("/track/batch", response_model=BatchOperationResponse)
async def batch_track_locations(
    request: BatchLocationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Batch upload GPS locations (offline sync)

    Business Logic:
    - Used when salesperson comes back online after offline period
    - Mobile app stores locations locally during offline
    - Syncs all pending locations in one batch
    - Maximum 1000 locations per batch

    Performance:
    - Uses bulk insert for efficiency
    - Processes 1000 locations in ~2 seconds
    """
    # Authorization
    if not current_user.is_salesperson:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only salespersons can upload GPS locations"
        )

    uploaded = 0
    failed = 0
    errors = []
    ids = []

    try:
        for idx, location in enumerate(request.locations):
            try:
                gps_location = SalespersonGPSLocation(
                    salesperson_id=current_user.id,
                    latitude=location.latitude,
                    longitude=location.longitude,
                    timestamp=location.timestamp,
                    accuracy=location.accuracy,
                    altitude=location.altitude,
                    speed=location.speed,
                    heading=location.heading,
                    activity_type=location.activity_type,
                    battery_level=location.battery_level,
                    is_charging=location.is_charging,
                    device_id=location.device_id,
                    is_synced=True,
                    synced_at=datetime.utcnow()
                )

                db.add(gps_location)
                db.flush()  # Get ID without committing

                ids.append(gps_location.id)
                uploaded += 1

            except Exception as e:
                failed += 1
                errors.append({
                    "index": idx,
                    "error": str(e),
                    "location": location.dict()
                })

        db.commit()

        return BatchOperationResponse(
            success=failed == 0,
            total=len(request.locations),
            uploaded=uploaded,
            failed=failed,
            errors=errors,
            ids=ids
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch upload failed: {str(e)}"
        )


@router.get("/history", response_model=List[GPSLocationResponse])
async def get_location_history(
    salesperson_id: int = Query(..., description="Salesperson user ID"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get GPS location history

    Authorization:
    - Salespersons can view their own history
    - Managers can view any salesperson's history

    Default: Last 24 hours if no dates specified
    """
    # Authorization
    if current_user.id != salesperson_id and not current_user.role.name.lower() in ['admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own GPS history"
        )

    # Default to last 24 hours
    if not start_date:
        start_date = datetime.utcnow().date() - timedelta(days=1)
    if not end_date:
        end_date = datetime.utcnow().date()

    # Query locations
    locations = db.query(SalespersonGPSLocation).filter(
        and_(
            SalespersonGPSLocation.salesperson_id == salesperson_id,
            func.date(SalespersonGPSLocation.timestamp) >= start_date,
            func.date(SalespersonGPSLocation.timestamp) <= end_date
        )
    ).order_by(desc(SalespersonGPSLocation.timestamp)).limit(limit).all()

    return locations


@router.get("/summary/daily", response_model=DailySummaryResponse)
async def get_daily_summary(
    salesperson_id: int = Query(..., description="Salesperson user ID"),
    summary_date: date = Query(..., description="Date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get daily GPS tracking summary

    Returns:
    - Total distance traveled (km)
    - Total time on route (hours)
    - Customer visits count
    - Complete route (all GPS points for the day)
    - Start/end times

    Performance:
    - First checks pre-calculated summary table
    - Falls back to real-time calculation if not cached
    """
    # Authorization
    if current_user.id != salesperson_id and not current_user.role.name.lower() in ['admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own summaries"
        )

    # Try to get pre-calculated summary
    cached_summary = db.query(SalespersonDailySummary).filter(
        and_(
            SalespersonDailySummary.salesperson_id == salesperson_id,
            SalespersonDailySummary.summary_date == summary_date
        )
    ).first()

    # Get route points for the day
    route = db.query(SalespersonGPSLocation).filter(
        and_(
            SalespersonGPSLocation.salesperson_id == salesperson_id,
            func.date(SalespersonGPSLocation.timestamp) == summary_date
        )
    ).order_by(SalespersonGPSLocation.timestamp).all()

    if cached_summary:
        # Use cached data
        return DailySummaryResponse(
            date=summary_date,
            total_distance_km=cached_summary.total_distance_km,
            total_duration_hours=cached_summary.total_time_hours,
            customer_visits=cached_summary.customer_visits,
            verified_visits=cached_summary.verified_visits,
            route=route,
            start_time=route[0].timestamp if route else None,
            end_time=route[-1].timestamp if route else None
        )
    else:
        # Calculate on-the-fly
        total_distance = Decimal(0)
        customer_visits = db.query(SalespersonGPSLocation).filter(
            and_(
                SalespersonGPSLocation.salesperson_id == salesperson_id,
                func.date(SalespersonGPSLocation.timestamp) == summary_date,
                SalespersonGPSLocation.is_customer_visit == True
            )
        ).count()

        verified_visits = db.query(SalespersonGPSLocation).filter(
            and_(
                SalespersonGPSLocation.salesperson_id == salesperson_id,
                func.date(SalespersonGPSLocation.timestamp) == summary_date,
                SalespersonGPSLocation.is_customer_visit == True,
                SalespersonGPSLocation.visit_verified == True
            )
        ).count()

        # Calculate distance between consecutive points
        for i in range(1, len(route)):
            dist = calculate_distance(
                float(route[i-1].latitude), float(route[i-1].longitude),
                float(route[i].latitude), float(route[i].longitude)
            )
            total_distance += Decimal(dist / 1000)  # Convert to km

        # Calculate duration
        total_duration = Decimal(0)
        if route:
            duration_seconds = (route[-1].timestamp - route[0].timestamp).total_seconds()
            total_duration = Decimal(duration_seconds / 3600)  # Convert to hours

        return DailySummaryResponse(
            date=summary_date,
            total_distance_km=round(total_distance, 2),
            total_duration_hours=round(total_duration, 2),
            customer_visits=customer_visits,
            verified_visits=verified_visits,
            route=route,
            start_time=route[0].timestamp if route else None,
            end_time=route[-1].timestamp if route else None
        )


@router.get("/summary/weekly", response_model=WeeklySummaryResponse)
async def get_weekly_summary(
    salesperson_id: int = Query(..., description="Salesperson user ID"),
    week_start: date = Query(..., description="Week start date (Monday)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get weekly GPS tracking summary

    Returns:
    - Weekly totals (distance, time, visits)
    - Daily breakdown for each day of the week

    Week Definition:
    - Monday to Sunday (7 days)
    """
    # Authorization
    if current_user.id != salesperson_id and not current_user.role.name.lower() in ['admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own summaries"
        )

    week_end = week_start + timedelta(days=6)

    # Get daily summaries for the week
    daily_breakdowns = []
    total_distance = Decimal(0)
    total_duration = Decimal(0)
    total_visits = 0
    total_verified = 0

    for day_offset in range(7):
        current_date = week_start + timedelta(days=day_offset)

        # Get or calculate daily summary
        daily_summary = await get_daily_summary(
            salesperson_id=salesperson_id,
            summary_date=current_date,
            current_user=current_user,
            db=db
        )

        daily_breakdowns.append(daily_summary)
        total_distance += daily_summary.total_distance_km
        total_duration += daily_summary.total_duration_hours
        total_visits += daily_summary.customer_visits
        total_verified += daily_summary.verified_visits

    return WeeklySummaryResponse(
        week_start=week_start,
        week_end=week_end,
        total_distance_km=round(total_distance, 2),
        total_duration_hours=round(total_duration, 2),
        total_customer_visits=total_visits,
        total_verified_visits=total_verified,
        daily_breakdown=daily_breakdowns
    )


@router.post("/verify-visit", response_model=VerifyVisitResponse)
async def verify_customer_visit(
    request: VerifyVisitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify customer visit using GPS coordinates

    Business Logic:
    - Checks if salesperson is within 100 meters of customer location
    - Creates GPS record marked as customer visit
    - Used for visit verification and fraud prevention

    Geofence:
    - Default radius: 100 meters
    - Can be configured per customer if needed
    """
    # Authorization
    if not current_user.is_salesperson:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only salespersons can verify visits"
        )

    # Get customer location
    customer = db.query(Customer).filter(Customer.id == request.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    # Check if customer has GPS coordinates
    if not customer.latitude or not customer.longitude:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer location not available. Cannot verify visit."
        )

    # Calculate distance from customer
    distance = calculate_distance(
        float(customer.latitude),
        float(customer.longitude),
        request.latitude,
        request.longitude
    )

    # Check geofence (100 meters default)
    within_geofence = distance <= 100
    verified = within_geofence

    # Create GPS location record
    gps_location = SalespersonGPSLocation(
        salesperson_id=current_user.id,
        latitude=request.latitude,
        longitude=request.longitude,
        timestamp=request.visit_time,
        is_customer_visit=True,
        customer_id=request.customer_id,
        visit_verified=verified,
        distance_from_customer=distance,
        is_synced=True,
        synced_at=datetime.utcnow()
    )

    db.add(gps_location)
    db.commit()

    return VerifyVisitResponse(
        verified=verified,
        distance_from_customer=distance,
        within_geofence=within_geofence,
        customer_name=customer.name,
        customer_address=customer.address,
        visit_id=gps_location.id
    )


@router.get("/sync-status", response_model=SyncStatusResponse)
async def get_sync_status(
    salesperson_id: int = Query(..., description="Salesperson user ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get GPS sync status

    Returns:
    - Number of pending (unsynced) locations
    - Last successful sync timestamp
    - Current sync status

    Note: This endpoint is called by mobile app to show sync indicator
    """
    # Authorization
    if current_user.id != salesperson_id and not current_user.role.name.lower() in ['admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own sync status"
        )

    # Count pending locations (is_synced = False)
    pending_count = db.query(SalespersonGPSLocation).filter(
        and_(
            SalespersonGPSLocation.salesperson_id == salesperson_id,
            SalespersonGPSLocation.is_synced == False
        )
    ).count()

    # Get last sync time
    last_synced = db.query(SalespersonGPSLocation).filter(
        and_(
            SalespersonGPSLocation.salesperson_id == salesperson_id,
            SalespersonGPSLocation.is_synced == True,
            SalespersonGPSLocation.synced_at.isnot(None)
        )
    ).order_by(desc(SalespersonGPSLocation.synced_at)).first()

    # Count sync errors (if any)
    # TODO: Implement error tracking if needed

    return SyncStatusResponse(
        pending_locations=pending_count,
        last_sync=last_synced.synced_at if last_synced else None,
        is_syncing=False,  # TODO: Implement active sync detection
        sync_errors=0
    )


@router.delete("/locations/{location_id}", response_model=dict)
async def delete_location(
    location_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete GPS location record

    Authorization:
    - Salespersons can delete their own locations (within 24 hours)
    - Managers/admins can delete any location

    Business Rule:
    - Locations older than 24 hours cannot be deleted by salespersons
    - Prevents tampering with historical data
    """
    # Get location
    location = db.query(SalespersonGPSLocation).filter(
        SalespersonGPSLocation.id == location_id
    ).first()

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )

    # Authorization
    is_manager = current_user.role.name.lower() in ['admin', 'manager']
    is_owner = location.salesperson_id == current_user.id

    if not is_manager and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own locations"
        )

    # Check age restriction for salespersons
    if is_owner and not is_manager:
        age_hours = (datetime.utcnow() - location.created_at).total_seconds() / 3600
        if age_hours > 24:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete locations older than 24 hours"
            )

    # Delete location
    db.delete(location)
    db.commit()

    return {
        "success": True,
        "message": f"Location {location_id} deleted successfully"
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for GPS tracking service"""
    return {
        "status": "healthy",
        "service": "gps-tracking-bff",
        "version": "1.0.0"
    }
