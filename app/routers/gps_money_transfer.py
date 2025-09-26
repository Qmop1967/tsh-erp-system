from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from pydantic import BaseModel
from enum import Enum
import json
import asyncio
from math import radians, cos, sin, asin, sqrt
import uuid

from app.db.database import get_db
from app.models import (
    User, Customer, Product, InventoryItem, SalesOrder, SalesInvoice, 
    MoneyTransfer, Branch, Warehouse, StockMovement
)
from app.db.database import Base
from sqlalchemy import func, desc, and_, or_, Column, Integer, String, Text, DateTime, Boolean, Numeric, ForeignKey, JSON
from sqlalchemy.orm import relationship

router = APIRouter()

class GPSStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPICIOUS = "suspicious"
    EMERGENCY = "emergency"
    OFFLINE = "offline"

class TransferStatus(str, Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    VERIFIED = "verified"
    SUSPICIOUS = "suspicious"
    FAILED = "failed"

class AlertType(str, Enum):
    GEOFENCE_VIOLATION = "geofence_violation"
    SPEED_VIOLATION = "speed_violation"
    ROUTE_DEVIATION = "route_deviation"
    PROLONGED_STOP = "prolonged_stop"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    EMERGENCY_BUTTON = "emergency_button"
    DEVICE_OFFLINE = "device_offline"

class GPSLocation(BaseModel):
    salesperson_id: int
    latitude: float
    longitude: float
    accuracy: float
    speed: Optional[float] = 0.0
    heading: Optional[float] = 0.0
    timestamp: datetime
    battery_level: Optional[int] = 100
    is_moving: bool = False

class MoneyTransferGPS(BaseModel):
    transfer_id: int
    salesperson_id: int
    customer_id: int
    amount: float
    transfer_platform: str
    reference_number: str
    pickup_location: Dict[str, float]
    delivery_location: Dict[str, float]
    notes: Optional[str] = None

class GeofenceArea(BaseModel):
    name: str
    center_lat: float
    center_lng: float
    radius_meters: int
    area_type: str  # "allowed", "restricted", "customer_zone"
    active: bool = True

class SuspiciousActivityReport(BaseModel):
    salesperson_id: int
    alert_type: AlertType
    description: str
    location: Dict[str, float]
    severity: str  # "low", "medium", "high", "critical"
    additional_data: Optional[Dict[str, Any]] = None

class RouteOptimization(BaseModel):
    salesperson_id: int
    date: date
    customer_locations: List[Dict[str, Any]]
    optimize_for: str = "distance"  # "distance", "time", "priority"

@router.post("/gps/location/update")
async def update_gps_location(
    location: GPSLocation,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    📍 Real-time GPS location update for travel salespersons
    Processes location data and triggers alerts if needed
    """
    
    try:
        # Create location record
        gps_record = SalespersonLocation(
            salesperson_id=location.salesperson_id,
            latitude=location.latitude,
            longitude=location.longitude,
            accuracy=location.accuracy,
            speed=location.speed,
            heading=location.heading,
            battery_level=location.battery_level,
            is_moving=location.is_moving,
            timestamp=location.timestamp,
            created_at=datetime.now()
        )
        
        db.add(gps_record)
        
        # Update salesperson current status
        salesperson = db.query(TravelSalesperson).filter(
            TravelSalesperson.id == location.salesperson_id
        ).first()
        
        if salesperson:
            salesperson.current_latitude = location.latitude
            salesperson.current_longitude = location.longitude
            salesperson.last_location_update = location.timestamp
            salesperson.current_speed = location.speed
            salesperson.battery_level = location.battery_level
            salesperson.gps_status = GPSStatus.ACTIVE.value
        
        # Background tasks for alert processing
        background_tasks.add_task(
            process_location_alerts, 
            location, 
            db
        )
        
        db.commit()
        
        return {
            "status": "success",
            "location_id": gps_record.id,
            "alerts_processed": True,
            "timestamp": location.timestamp.isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update GPS location: {str(e)}")

@router.get("/gps/tracking/live")
async def get_live_tracking_data(
    db: Session = Depends(get_db)
):
    """
    🔴 Real-time tracking dashboard for all travel salespersons
    """
    
    try:
        # Get all active travel salespersons with their latest locations
        salespersons = db.query(TravelSalesperson).filter(
            TravelSalesperson.is_active == True
        ).all()
        
        tracking_data = []
        
        for salesperson in salespersons:
            # Get latest location
            latest_location = db.query(SalespersonLocation).filter(
                SalespersonLocation.salesperson_id == salesperson.id
            ).order_by(desc(SalespersonLocation.timestamp)).first()
            
            # Get active transfers
            active_transfers = db.query(MoneyTransfer).filter(
                MoneyTransfer.salesperson_id == salesperson.id,
                MoneyTransfer.status.in_([TransferStatus.PENDING.value, TransferStatus.IN_TRANSIT.value])
            ).count()
            
            # Get today's transfers
            today = date.today()
            today_transfers = db.query(func.sum(MoneyTransfer.amount)).filter(
                MoneyTransfer.salesperson_id == salesperson.id,
                MoneyTransfer.transfer_date == today,
                MoneyTransfer.status == TransferStatus.VERIFIED.value
            ).scalar() or 0
            
            # Calculate time since last update
            time_since_update = None
            if latest_location:
                time_since_update = (datetime.now() - latest_location.timestamp).total_seconds() / 60  # minutes
            
            # Determine status
            status = GPSStatus.ACTIVE.value
            if not latest_location or time_since_update > 30:
                status = GPSStatus.OFFLINE.value
            elif time_since_update > 15:
                status = GPSStatus.INACTIVE.value
            
            # Get recent alerts
            recent_alerts = db.query(GPSAlert).filter(
                GPSAlert.salesperson_id == salesperson.id,
                GPSAlert.created_at >= datetime.now() - timedelta(hours=1),
                GPSAlert.resolved == False
            ).count()
            
            tracking_data.append({
                "salesperson_id": salesperson.id,
                "name": salesperson.name,
                "phone": salesperson.phone,
                "current_location": {
                    "latitude": float(latest_location.latitude) if latest_location else None,
                    "longitude": float(latest_location.longitude) if latest_location else None,
                    "accuracy": float(latest_location.accuracy) if latest_location else None,
                    "speed": float(latest_location.speed) if latest_location else 0,
                    "timestamp": latest_location.timestamp.isoformat() if latest_location else None
                },
                "status": status,
                "battery_level": latest_location.battery_level if latest_location else 0,
                "time_since_update": time_since_update,
                "active_transfers": active_transfers,
                "today_amount": float(today_transfers),
                "recent_alerts": recent_alerts,
                "route_efficiency": calculate_route_efficiency(salesperson.id, db),
                "is_moving": latest_location.is_moving if latest_location else False
            })
        
        return {
            "tracking_data": tracking_data,
            "total_salespersons": len(salespersons),
            "active_count": len([s for s in tracking_data if s["status"] == GPSStatus.ACTIVE.value]),
            "offline_count": len([s for s in tracking_data if s["status"] == GPSStatus.OFFLINE.value]),
            "total_today_amount": sum(s["today_amount"] for s in tracking_data),
            "total_active_transfers": sum(s["active_transfers"] for s in tracking_data),
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get live tracking data: {str(e)}")

@router.post("/gps/money-transfer/create")
async def create_gps_money_transfer(
    transfer: MoneyTransferGPS,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    💰 Create money transfer with GPS tracking
    Includes route planning and real-time monitoring
    """
    
    try:
        # Create money transfer record
        money_transfer = MoneyTransfer(
            transfer_number=f"MT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}",
            salesperson_id=transfer.salesperson_id,
            customer_id=transfer.customer_id,
            amount=transfer.amount,
            transfer_platform=transfer.transfer_platform,
            reference_number=transfer.reference_number,
            status=TransferStatus.PENDING.value,
            transfer_date=date.today(),
            notes=transfer.notes,
            created_at=datetime.now()
        )
        
        db.add(money_transfer)
        db.flush()
        
        # Create GPS tracking route
        route_record = TransferRoute(
            transfer_id=money_transfer.id,
            pickup_latitude=transfer.pickup_location["latitude"],
            pickup_longitude=transfer.pickup_location["longitude"],
            delivery_latitude=transfer.delivery_location["latitude"],
            delivery_longitude=transfer.delivery_location["longitude"],
            estimated_distance=calculate_distance(
                transfer.pickup_location["latitude"],
                transfer.pickup_location["longitude"],
                transfer.delivery_location["latitude"],
                transfer.delivery_location["longitude"]
            ),
            estimated_duration=30,  # minutes - can be calculated based on distance
            status="planned",
            created_at=datetime.now()
        )
        
        db.add(route_record)
        
        # Create geofence for delivery location
        delivery_geofence = GeofenceAlert(
            transfer_id=money_transfer.id,
            center_latitude=transfer.delivery_location["latitude"],
            center_longitude=transfer.delivery_location["longitude"],
            radius_meters=500,  # 500m radius
            alert_type="delivery_zone",
            is_active=True,
            created_at=datetime.now()
        )
        
        db.add(delivery_geofence)
        
        # Background task for route optimization
        background_tasks.add_task(
            optimize_transfer_route,
            money_transfer.id,
            transfer.salesperson_id,
            db
        )
        
        db.commit()
        
        return {
            "transfer_id": money_transfer.id,
            "transfer_number": money_transfer.transfer_number,
            "status": money_transfer.status,
            "estimated_distance": route_record.estimated_distance,
            "estimated_duration": route_record.estimated_duration,
            "geofence_created": True,
            "message": "Money transfer created with GPS tracking enabled"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create GPS money transfer: {str(e)}")

@router.get("/gps/alerts/active")
async def get_active_alerts(
    salesperson_id: Optional[int] = Query(None),
    alert_type: Optional[AlertType] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """
    🚨 Get active GPS alerts and suspicious activities
    """
    
    query = db.query(GPSAlert).filter(GPSAlert.resolved == False).order_by(desc(GPSAlert.created_at))
    
    if salesperson_id:
        query = query.filter(GPSAlert.salesperson_id == salesperson_id)
    
    if alert_type:
        query = query.filter(GPSAlert.alert_type == alert_type.value)
    
    if severity:
        query = query.filter(GPSAlert.severity == severity)
    
    alerts = query.limit(limit).all()
    
    formatted_alerts = []
    for alert in alerts:
        formatted_alerts.append({
            "id": alert.id,
            "salesperson_id": alert.salesperson_id,
            "salesperson_name": alert.salesperson.name if alert.salesperson else "Unknown",
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "description": alert.description,
            "location": {
                "latitude": float(alert.latitude),
                "longitude": float(alert.longitude)
            },
            "additional_data": alert.additional_data,
            "created_at": alert.created_at.isoformat(),
            "time_ago": (datetime.now() - alert.created_at).total_seconds() / 60  # minutes
        })
    
    return {
        "alerts": formatted_alerts,
        "total_count": len(formatted_alerts),
        "critical_count": len([a for a in formatted_alerts if a["severity"] == "critical"]),
        "high_count": len([a for a in formatted_alerts if a["severity"] == "high"]),
        "last_updated": datetime.now().isoformat()
    }

@router.post("/gps/geofence/create")
async def create_geofence(
    geofence: GeofenceArea,
    db: Session = Depends(get_db)
):
    """
    📍 Create geofence area for monitoring
    """
    
    try:
        geofence_record = Geofence(
            name=geofence.name,
            center_latitude=geofence.center_lat,
            center_longitude=geofence.center_lng,
            radius_meters=geofence.radius_meters,
            area_type=geofence.area_type,
            is_active=geofence.active,
            created_at=datetime.now()
        )
        
        db.add(geofence_record)
        db.commit()
        
        return {
            "geofence_id": geofence_record.id,
            "name": geofence.name,
            "status": "created",
            "area_coverage": f"{geofence.radius_meters}m radius"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create geofence: {str(e)}")

@router.get("/gps/reports/daily/{salesperson_id}")
async def get_daily_gps_report(
    salesperson_id: int,
    report_date: date = Query(...),
    db: Session = Depends(get_db)
):
    """
    📊 Generate comprehensive daily GPS report for salesperson
    """
    
    try:
        start_date = datetime.combine(report_date, datetime.min.time())
        end_date = start_date + timedelta(days=1)
        
        # Get all locations for the day
        locations = db.query(SalespersonLocation).filter(
            SalespersonLocation.salesperson_id == salesperson_id,
            SalespersonLocation.timestamp >= start_date,
            SalespersonLocation.timestamp < end_date
        ).order_by(SalespersonLocation.timestamp).all()
        
        if not locations:
            return {
                "salesperson_id": salesperson_id,
                "date": report_date.isoformat(),
                "total_distance": 0,
                "total_time": 0,
                "locations_count": 0,
                "transfers": [],
                "alerts": [],
                "efficiency_score": 0
            }
        
        # Calculate total distance traveled
        total_distance = 0.0
        for i in range(1, len(locations)):
            prev_loc = locations[i-1]
            curr_loc = locations[i]
            distance = calculate_distance(
                float(prev_loc.latitude), float(prev_loc.longitude),
                float(curr_loc.latitude), float(curr_loc.longitude)
            )
            total_distance += distance
        
        # Calculate time spent
        total_time = (locations[-1].timestamp - locations[0].timestamp).total_seconds() / 3600  # hours
        
        # Get transfers for the day
        transfers = db.query(MoneyTransfer).filter(
            MoneyTransfer.salesperson_id == salesperson_id,
            MoneyTransfer.transfer_date == report_date
        ).all()
        
        transfer_data = [
            {
                "transfer_id": t.id,
                "transfer_number": t.transfer_number,
                "amount": float(t.amount),
                "status": t.status,
                "platform": t.transfer_platform,
                "created_at": t.created_at.isoformat()
            } for t in transfers
        ]
        
        # Get alerts for the day
        alerts = db.query(GPSAlert).filter(
            GPSAlert.salesperson_id == salesperson_id,
            GPSAlert.created_at >= start_date,
            GPSAlert.created_at < end_date
        ).all()
        
        alert_data = [
            {
                "alert_id": a.id,
                "alert_type": a.alert_type,
                "severity": a.severity,
                "description": a.description,
                "created_at": a.created_at.isoformat()
            } for a in alerts
        ]
        
        # Calculate efficiency score
        efficiency_score = calculate_efficiency_score(
            total_distance, total_time, len(transfers), len(alerts)
        )
        
        return {
            "salesperson_id": salesperson_id,
            "date": report_date.isoformat(),
            "total_distance": round(total_distance, 2),
            "total_time": round(total_time, 2),
            "average_speed": round(total_distance / total_time if total_time > 0 else 0, 2),
            "locations_count": len(locations),
            "transfers": transfer_data,
            "total_transfer_amount": sum(t.amount for t in transfers),
            "alerts": alert_data,
            "alerts_count": len(alerts),
            "efficiency_score": efficiency_score,
            "route_points": [
                {
                    "latitude": float(loc.latitude),
                    "longitude": float(loc.longitude),
                    "timestamp": loc.timestamp.isoformat(),
                    "speed": float(loc.speed) if loc.speed else 0
                } for loc in locations[::10]  # Sample every 10th point for visualization
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate GPS report: {str(e)}")

@router.post("/gps/emergency/trigger")
async def trigger_emergency_alert(
    salesperson_id: int,
    location: Dict[str, float],
    message: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    🚨 Emergency button - immediate alert for salesperson safety
    """
    
    try:
        # Create emergency alert
        emergency_alert = GPSAlert(
            salesperson_id=salesperson_id,
            alert_type=AlertType.EMERGENCY_BUTTON.value,
            severity="critical",
            description=f"EMERGENCY: {message}" if message else "EMERGENCY: Help requested by salesperson",
            latitude=location["latitude"],
            longitude=location["longitude"],
            additional_data={
                "emergency": True,
                "timestamp": datetime.now().isoformat(),
                "message": message
            },
            resolved=False,
            created_at=datetime.now()
        )
        
        db.add(emergency_alert)
        
        # Update salesperson status
        salesperson = db.query(TravelSalesperson).filter(
            TravelSalesperson.id == salesperson_id
        ).first()
        
        if salesperson:
            salesperson.gps_status = GPSStatus.EMERGENCY.value
        
        db.commit()
        
        # Here you would typically send immediate notifications
        # via SMS, WhatsApp, email to admin and security team
        
        return {
            "alert_id": emergency_alert.id,
            "status": "emergency_triggered",
            "salesperson_id": salesperson_id,
            "location": location,
            "timestamp": datetime.now().isoformat(),
            "message": "Emergency alert sent to admin and security team"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to trigger emergency alert: {str(e)}")

# Helper Functions

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two GPS coordinates in kilometers"""
    # Haversine formula
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Earth's radius in kilometers
    return c * r

def calculate_route_efficiency(salesperson_id: int, db: Session) -> float:
    """Calculate route efficiency score for salesperson"""
    # Get today's data
    today = date.today()
    start_date = datetime.combine(today, datetime.min.time())
    end_date = start_date + timedelta(days=1)
    
    # Get locations and transfers
    locations = db.query(SalespersonLocation).filter(
        SalespersonLocation.salesperson_id == salesperson_id,
        SalespersonLocation.timestamp >= start_date,
        SalespersonLocation.timestamp < end_date
    ).count()
    
    transfers = db.query(MoneyTransfer).filter(
        MoneyTransfer.salesperson_id == salesperson_id,
        MoneyTransfer.transfer_date == today
    ).count()
    
    # Simple efficiency calculation
    if locations == 0:
        return 0.0
    
    efficiency = (transfers / locations * 100) if locations > 0 else 0
    return min(efficiency, 100.0)

def calculate_efficiency_score(distance: float, time: float, transfers: int, alerts: int) -> float:
    """Calculate overall efficiency score"""
    base_score = 100.0
    
    # Deduct points for excessive distance without transfers
    if transfers > 0:
        distance_per_transfer = distance / transfers
        if distance_per_transfer > 50:  # 50km per transfer seems excessive
            base_score -= (distance_per_transfer - 50) * 0.5
    
    # Deduct points for alerts
    base_score -= alerts * 5
    
    # Bonus for transfers
    base_score += transfers * 2
    
    return max(0.0, min(100.0, base_score))

async def process_location_alerts(location: GPSLocation, db: Session):
    """Background task to process location-based alerts"""
    try:
        # Check for geofence violations
        geofences = db.query(Geofence).filter(Geofence.is_active == True).all()
        
        for geofence in geofences:
            distance = calculate_distance(
                location.latitude, location.longitude,
                float(geofence.center_latitude), float(geofence.center_longitude)
            )
            
            # Convert distance to meters
            distance_meters = distance * 1000
            
            # Check if outside allowed area or inside restricted area
            if geofence.area_type == "restricted" and distance_meters <= geofence.radius_meters:
                # Inside restricted area
                create_alert(
                    db, location.salesperson_id, AlertType.GEOFENCE_VIOLATION,
                    f"Entered restricted area: {geofence.name}",
                    location.latitude, location.longitude, "high"
                )
            elif geofence.area_type == "allowed" and distance_meters > geofence.radius_meters:
                # Outside allowed area
                create_alert(
                    db, location.salesperson_id, AlertType.GEOFENCE_VIOLATION,
                    f"Left allowed area: {geofence.name}",
                    location.latitude, location.longitude, "medium"
                )
        
        # Check for speed violations
        if location.speed and location.speed > 120:  # 120 km/h speed limit
            create_alert(
                db, location.salesperson_id, AlertType.SPEED_VIOLATION,
                f"Speed violation: {location.speed} km/h",
                location.latitude, location.longitude, "high"
            )
        
        db.commit()
        
    except Exception as e:
        print(f"Error processing location alerts: {e}")
        db.rollback()

def create_alert(db: Session, salesperson_id: int, alert_type: AlertType, 
                description: str, lat: float, lng: float, severity: str):
    """Create GPS alert"""
    alert = GPSAlert(
        salesperson_id=salesperson_id,
        alert_type=alert_type.value,
        severity=severity,
        description=description,
        latitude=lat,
        longitude=lng,
        resolved=False,
        created_at=datetime.now()
    )
    db.add(alert)

async def optimize_transfer_route(transfer_id: int, salesperson_id: int, db: Session):
    """Background task for route optimization"""
    try:
        # Get transfer details
        transfer = db.query(MoneyTransfer).filter(MoneyTransfer.id == transfer_id).first()
        if not transfer:
            return
        
        # Get route
        route = db.query(TransferRoute).filter(TransferRoute.transfer_id == transfer_id).first()
        if not route:
            return
        
        # Simple optimization - calculate optimal route based on current location
        # In production, this would use real routing APIs like Google Maps
        
        route.optimized = True
        route.optimization_completed_at = datetime.now()
        
        db.commit()
        
    except Exception as e:
        print(f"Error optimizing route: {e}")
        db.rollback()

# Database Models for GPS Tracking

class TravelSalesperson(Base):
    __tablename__ = "travel_salespersons"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    employee_id = Column(String, unique=True)
    current_latitude = Column(Numeric(10, 7))
    current_longitude = Column(Numeric(10, 7))
    last_location_update = Column(DateTime)
    current_speed = Column(Numeric(5, 2))
    battery_level = Column(Integer)
    gps_status = Column(String, default="active")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

class SalespersonLocation(Base):
    __tablename__ = "salesperson_locations"
    
    id = Column(Integer, primary_key=True, index=True)
    salesperson_id = Column(Integer, ForeignKey("travel_salespersons.id"))
    latitude = Column(Numeric(10, 7), nullable=False)
    longitude = Column(Numeric(10, 7), nullable=False)
    accuracy = Column(Numeric(8, 2))
    speed = Column(Numeric(5, 2))
    heading = Column(Numeric(5, 2))
    battery_level = Column(Integer)
    is_moving = Column(Boolean, default=False)
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    salesperson = relationship("TravelSalesperson")

class TransferRoute(Base):
    __tablename__ = "transfer_routes"
    
    id = Column(Integer, primary_key=True, index=True)
    transfer_id = Column(Integer, ForeignKey("money_transfers.id"))
    pickup_latitude = Column(Numeric(10, 7))
    pickup_longitude = Column(Numeric(10, 7))
    delivery_latitude = Column(Numeric(10, 7))
    delivery_longitude = Column(Numeric(10, 7))
    estimated_distance = Column(Numeric(8, 2))  # km
    estimated_duration = Column(Integer)  # minutes
    actual_distance = Column(Numeric(8, 2))
    actual_duration = Column(Integer)
    optimized = Column(Boolean, default=False)
    optimization_completed_at = Column(DateTime)
    status = Column(String, default="planned")
    created_at = Column(DateTime, default=datetime.now)

class GPSAlert(Base):
    __tablename__ = "gps_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    salesperson_id = Column(Integer, ForeignKey("travel_salespersons.id"))
    alert_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)  # low, medium, high, critical
    description = Column(Text)
    latitude = Column(Numeric(10, 7))
    longitude = Column(Numeric(10, 7))
    additional_data = Column(JSON)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolved_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    salesperson = relationship("TravelSalesperson")

class Geofence(Base):
    __tablename__ = "geofences"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    center_latitude = Column(Numeric(10, 7), nullable=False)
    center_longitude = Column(Numeric(10, 7), nullable=False)
    radius_meters = Column(Integer, nullable=False)
    area_type = Column(String, nullable=False)  # allowed, restricted, customer_zone
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

class GeofenceAlert(Base):
    __tablename__ = "geofence_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    transfer_id = Column(Integer, ForeignKey("money_transfers.id"))
    center_latitude = Column(Numeric(10, 7))
    center_longitude = Column(Numeric(10, 7))
    radius_meters = Column(Integer)
    alert_type = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now) 