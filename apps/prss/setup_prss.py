#!/usr/bin/env python3
"""
Script to setup complete PRSS system structure
Run this to generate all necessary files for the PRSS system
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Schema files content
SCHEMAS_CONTENT = {
    "schemas/__init__.py": '''"""Pydantic schemas for PRSS API"""
from .return_request import *
from .inspection import *
from .maintenance import *
from .warranty import *
from .decision import *
from .accounting import *
from .user import *
from .common import *
''',

    "schemas/common.py": '''"""Common schemas"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    details: Optional[dict] = None


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=100)


class PhotoUpload(BaseModel):
    """Photo upload data"""
    url: str
    filename: str
    size: int
    uploaded_at: datetime
''',

    "schemas/return_request.py": '''"""Return request schemas"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from prss.models.base import ReturnStatus


class ReturnRequestCreate(BaseModel):
    """Create return request"""
    customer_id: int
    sales_order_id: Optional[int] = None
    invoice_id: Optional[int] = None
    product_id: int
    serial_number: Optional[str] = None
    reason_code: str
    reason_description: Optional[str] = None
    photos: List[dict] = []
    videos: List[dict] = []


class ReturnRequestUpdate(BaseModel):
    """Update return request"""
    status: Optional[ReturnStatus] = None
    priority: Optional[int] = None
    photos: Optional[List[dict]] = None


class ReturnRequestResponse(BaseModel):
    """Return request response"""
    id: int
    customer_id: int
    sales_order_id: Optional[int]
    product_id: int
    serial_number: Optional[str]
    status: ReturnStatus
    reason_code: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReturnReceiveRequest(BaseModel):
    """Receive return request"""
    notes: Optional[str] = None
    received_by: int
    condition_photos: List[dict] = []
''',

    "schemas/inspection.py": '''"""Inspection schemas"""
from pydantic import BaseModel
from typing import Optional
from prss.models.base import FindingType, RecommendationType


class InspectionCreate(BaseModel):
    """Create inspection"""
    return_request_id: int
    inspector_id: int
    checklists: dict = {}
    finding: FindingType
    recommendation: RecommendationType
    inspection_photos: list = []
    notes: Optional[str] = None


class InspectionResponse(BaseModel):
    """Inspection response"""
    id: int
    return_request_id: int
    finding: FindingType
    recommendation: RecommendationType

    class Config:
        from_attributes = True
''',

    "schemas/maintenance.py": '''"""Maintenance schemas"""
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class MaintenanceJobStart(BaseModel):
    """Start maintenance job"""
    return_request_id: int
    technician_id: int
    cost_estimate: Optional[Decimal] = None


class MaintenanceJobComplete(BaseModel):
    """Complete maintenance job"""
    outcome: str
    parts_used: list = []
    labor_minutes: int = 0
    actual_cost: Optional[Decimal] = None
    notes: Optional[str] = None
''',

    "schemas/warranty.py": '''"""Warranty schemas"""
from pydantic import BaseModel
from datetime import date
from typing import Optional


class WarrantyCaseCreate(BaseModel):
    """Create warranty case"""
    return_request_id: int
    purchase_date: date
    warranty_expiry_date: date
    policy_id: Optional[int] = None
''',

    "schemas/decision.py": '''"""Decision schemas"""
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from prss.models.base import FinalDecision


class DecisionCreate(BaseModel):
    """Create final decision"""
    return_request_id: int
    final_decision: FinalDecision
    approved_by: int
    reason: Optional[str] = None
    estimated_value: Optional[Decimal] = None
    notes: Optional[str] = None
''',

    "schemas/accounting.py": '''"""Accounting schemas"""
from pydantic import BaseModel
from decimal import Decimal
from prss.models.base import AccountingEffectType


class AccountingEffectCreate(BaseModel):
    """Create accounting effect"""
    return_request_id: int
    effect_type: AccountingEffectType
    amount: Decimal
    currency: str = "SAR"
    notes: str = ""
''',

    "schemas/user.py": '''"""User schemas"""
from pydantic import BaseModel, EmailStr
from prss.models.base import UserRole


class UserCreate(BaseModel):
    """Create user"""
    username: str
    email: EmailStr
    full_name: str
    role: UserRole
    password: str


class Token(BaseModel):
    """JWT Token"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    username: str
    role: UserRole
    scopes: list[str] = []
''',
}

# API files content
API_CONTENT = {
    "api/__init__.py": "",
    "api/v1/__init__.py": "",

    "api/v1/returns.py": '''"""Returns API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from prss.db import get_db
from prss.schemas.return_request import *
from prss.services.return_service import ReturnService
from prss.security.auth import get_current_user

router = APIRouter(prefix="/returns", tags=["returns"])


@router.post("/", response_model=ReturnRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_return_request(
    request: ReturnRequestCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new return request"""
    service = ReturnService(db)
    return service.create_return(request, current_user.id)


@router.get("/{return_id}", response_model=ReturnRequestResponse)
async def get_return_request(
    return_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get return request by ID"""
    service = ReturnService(db)
    return service.get_return(return_id)


@router.post("/{return_id}/receive")
async def receive_return(
    return_id: int,
    request: ReturnReceiveRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Mark return as received"""
    service = ReturnService(db)
    return service.receive_return(return_id, request, current_user.id)


@router.get("/", response_model=List[ReturnRequestResponse])
async def list_returns(
    status: Optional[str] = None,
    serial_number: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List return requests with filters"""
    service = ReturnService(db)
    return service.list_returns(status=status, serial_number=serial_number, skip=skip, limit=limit)
''',

    "api/v1/inspections.py": '''"""Inspection API endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from prss.db import get_db
from prss.schemas.inspection import *
from prss.services.inspection_service import InspectionService
from prss.security.auth import get_current_user, require_role

router = APIRouter(prefix="/returns", tags=["inspections"])


@router.post("/{return_id}/inspect", dependencies=[Depends(require_role(["admin", "inspector"]))])
async def create_inspection(
    return_id: int,
    inspection: InspectionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Submit inspection result"""
    service = InspectionService(db)
    return service.create_inspection(return_id, inspection, current_user.id)
''',

    "api/v1/maintenance.py": '''"""Maintenance API endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from prss.db import get_db
from prss.schemas.maintenance import *
from prss.services.maintenance_service import MaintenanceService
from prss.security.auth import get_current_user, require_role

router = APIRouter(prefix="/returns", tags=["maintenance"])


@router.post("/{return_id}/maintenance/start", dependencies=[Depends(require_role(["admin", "technician"]))])
async def start_maintenance(
    return_id: int,
    job_data: MaintenanceJobStart,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Start maintenance job"""
    service = MaintenanceService(db)
    return service.start_job(return_id, job_data, current_user.id)


@router.post("/{return_id}/maintenance/complete", dependencies=[Depends(require_role(["admin", "technician"]))])
async def complete_maintenance(
    return_id: int,
    job_data: MaintenanceJobComplete,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Complete maintenance job"""
    service = MaintenanceService(db)
    return service.complete_job(return_id, job_data, current_user.id)
''',

    "api/v1/decisions.py": '''"""Decision API endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from prss.db import get_db
from prss.schemas.decision import *
from prss.services.decision_service import DecisionService
from prss.security.auth import get_current_user, require_role

router = APIRouter(prefix="/returns", tags=["decisions"])


@router.post("/{return_id}/decide", dependencies=[Depends(require_role(["admin", "warranty_officer"]))])
async def make_decision(
    return_id: int,
    decision: DecisionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Make final decision on return"""
    service = DecisionService(db)
    return service.create_decision(return_id, decision, current_user.id)


@router.post("/{return_id}/transfer-to-inventory", dependencies=[Depends(require_role(["admin"]))])
async def transfer_to_inventory(
    return_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Transfer approved return to main inventory"""
    service = DecisionService(db)
    return service.transfer_to_inventory(return_id, current_user.id)
''',

    "api/v1/reports.py": '''"""Reports API endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from prss.db import get_db
from prss.services.report_service import ReportService
from prss.security.auth import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/kpis")
async def get_kpis(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get KPI metrics"""
    service = ReportService(db)
    return service.get_kpis()


@router.get("/defect-rate")
async def get_defect_rate(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get defect rate analysis"""
    service = ReportService(db)
    return service.get_defect_rate()


@router.get("/top-reasons")
async def get_top_return_reasons(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get top return reasons"""
    service = ReportService(db)
    return service.get_top_reasons(limit)
''',
}

# Services content
SERVICES_CONTENT = {
    "services/__init__.py": "",

    "services/return_service.py": '''"""Return request business logic"""
from sqlalchemy.orm import Session
from prss.models.all_models import ReturnRequest, ReturnInventoryMove
from prss.models.base import ReturnStatus, InventoryZone
from prss.schemas.return_request import ReturnRequestCreate
from fastapi import HTTPException


class ReturnService:
    def __init__(self, db: Session):
        self.db = db

    def create_return(self, data: ReturnRequestCreate, user_id: int):
        """Create new return request"""
        return_req = ReturnRequest(
            **data.model_dump(),
            created_by=user_id,
            status=ReturnStatus.SUBMITTED
        )
        self.db.add(return_req)
        self.db.commit()
        self.db.refresh(return_req)

        # Create initial inventory move
        move = ReturnInventoryMove(
            return_request_id=return_req.id,
            to_zone=InventoryZone.RECEIVED,
            qty=1,
            moved_by=user_id
        )
        self.db.add(move)
        self.db.commit()

        return return_req

    def get_return(self, return_id: int):
        """Get return by ID"""
        return_req = self.db.query(ReturnRequest).filter(ReturnRequest.id == return_id).first()
        if not return_req:
            raise HTTPException(status_code=404, detail="Return request not found")
        return return_req

    def receive_return(self, return_id: int, data, user_id: int):
        """Mark return as received"""
        return_req = self.get_return(return_id)
        return_req.status = ReturnStatus.RECEIVED
        self.db.commit()
        return {"message": "Return marked as received"}

    def list_returns(self, status=None, serial_number=None, skip=0, limit=50):
        """List returns with filters"""
        query = self.db.query(ReturnRequest)
        if status:
            query = query.filter(ReturnRequest.status == status)
        if serial_number:
            query = query.filter(ReturnRequest.serial_number == serial_number)
        return query.offset(skip).limit(limit).all()
''',

    "services/inspection_service.py": '''"""Inspection business logic"""
from sqlalchemy.orm import Session
from prss.models.all_models import Inspection, ReturnRequest
from prss.models.base import ReturnStatus
from prss.schemas.inspection import InspectionCreate


class InspectionService:
    def __init__(self, db: Session):
        self.db = db

    def create_inspection(self, return_id: int, data: InspectionCreate, user_id: int):
        """Create inspection record"""
        inspection = Inspection(**data.model_dump())
        self.db.add(inspection)

        # Update return status
        return_req = self.db.query(ReturnRequest).filter(ReturnRequest.id == return_id).first()
        return_req.status = ReturnStatus.INSPECTING

        self.db.commit()
        return {"message": "Inspection recorded"}
''',

    "services/maintenance_service.py": '''"""Maintenance business logic"""
from sqlalchemy.orm import Session
from prss.models.all_models import MaintenanceJob, ReturnRequest
from prss.models.base import ReturnStatus
import secrets


class MaintenanceService:
    def __init__(self, db: Session):
        self.db = db

    def start_job(self, return_id: int, data, user_id: int):
        """Start maintenance job"""
        job_card_no = f"MNT-{secrets.token_hex(4).upper()}"
        job = MaintenanceJob(
            return_request_id=return_id,
            technician_id=user_id,
            job_card_no=job_card_no
        )
        self.db.add(job)

        # Update return status
        return_req = self.db.query(ReturnRequest).filter(ReturnRequest.id == return_id).first()
        return_req.status = ReturnStatus.TO_REPAIR

        self.db.commit()
        return {"job_card_no": job_card_no}

    def complete_job(self, return_id: int, data, user_id: int):
        """Complete maintenance job"""
        job = self.db.query(MaintenanceJob).filter(
            MaintenanceJob.return_request_id == return_id
        ).first()

        if job:
            job.outcome = data.outcome
            job.parts_used = data.parts_used
            job.labor_minutes = data.labor_minutes
            job.actual_cost = data.actual_cost
            job.notes = data.notes

            self.db.commit()

        return {"message": "Maintenance job completed"}
''',

    "services/decision_service.py": '''"""Decision business logic"""
from sqlalchemy.orm import Session
from prss.models.all_models import Decision, ReturnRequest, OutboxEvent
from prss.models.base import ReturnStatus, FinalDecision, OutboxStatus
from prss.schemas.decision import DecisionCreate
import json


class DecisionService:
    def __init__(self, db: Session):
        self.db = db

    def create_decision(self, return_id: int, data: DecisionCreate, user_id: int):
        """Create final decision"""
        decision = Decision(**data.model_dump(), approved_by=user_id)
        self.db.add(decision)

        # Update return status
        return_req = self.db.query(ReturnRequest).filter(ReturnRequest.id == return_id).first()
        return_req.status = ReturnStatus.AWAITING_DECISION

        # Create outbox event
        event = OutboxEvent(
            topic="prss.return.finalized",
            payload=json.dumps({
                "return_request_id": return_id,
                "final_decision": data.final_decision.value,
                "product_id": return_req.product_id
            }),
            status=OutboxStatus.PENDING
        )
        self.db.add(event)

        self.db.commit()
        return {"message": "Decision recorded"}

    def transfer_to_inventory(self, return_id: int, user_id: int):
        """Transfer to inventory system"""
        # This would call the inventory integration client
        return {"message": "Transfer initiated", "transfer_ref": f"INV-T-{return_id}"}
''',

    "services/report_service.py": '''"""Report generation service"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from prss.models.all_models import ReturnRequest, Inspection
from prss.models.base import FindingType


class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def get_kpis(self):
        """Get KPI metrics"""
        total = self.db.query(func.count(ReturnRequest.id)).scalar()
        return {
            "total_returns": total,
            "avg_processing_time_hours": 24.5,
            "defect_rate": 0.15
        }

    def get_defect_rate(self):
        """Calculate defect rate"""
        defects = self.db.query(func.count(Inspection.id)).filter(
            Inspection.finding.in_([FindingType.COSMETIC_DEFECT, FindingType.FUNCTIONAL_DEFECT])
        ).scalar()
        total = self.db.query(func.count(Inspection.id)).scalar()

        return {
            "defect_count": defects,
            "total_inspections": total,
            "defect_rate": defects / total if total > 0 else 0
        }

    def get_top_reasons(self, limit=5):
        """Get top return reasons"""
        results = self.db.query(
            ReturnRequest.reason_code,
            func.count(ReturnRequest.id).label("count")
        ).group_by(ReturnRequest.reason_code).order_by(func.count(ReturnRequest.id).desc()).limit(limit).all()

        return [{"reason": r[0], "count": r[1]} for r in results]
''',
}

# Integration clients
INTEGRATION_CONTENT = {
    "integration/__init__.py": "",

    "integration/base_client.py": '''"""Base HTTP client for integrations"""
import httpx
from prss.config import settings


class BaseClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    async def post(self, endpoint: str, data: dict):
        """POST request"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}{endpoint}",
                json=data,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def get(self, endpoint: str, params: dict = None):
        """GET request"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}{endpoint}",
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
''',

    "integration/inventory_client.py": '''"""Inventory system integration client"""
from .base_client import BaseClient
from prss.config import settings


class InventoryClient(BaseClient):
    def __init__(self):
        super().__init__(
            settings.inventory_api_base,
            settings.inventory_api_token
        )

    async def create_transfer(self, data: dict):
        """Create inventory transfer"""
        return await self.post("/transfers", data)

    async def get_product(self, product_id: int):
        """Get product details"""
        return await self.get(f"/products/{product_id}")
''',

    "integration/sales_client.py": '''"""Sales system integration client"""
from .base_client import BaseClient
from prss.config import settings


class SalesClient(BaseClient):
    def __init__(self):
        super().__init__(
            settings.sales_api_base,
            settings.sales_api_token
        )

    async def create_credit_note(self, data: dict):
        """Create credit note"""
        return await self.post("/credit-notes", data)

    async def get_order(self, order_id: int):
        """Get sales order"""
        return await self.get(f"/orders/{order_id}")
''',

    "integration/accounting_client.py": '''"""Accounting system integration client"""
from .base_client import BaseClient
from prss.config import settings


class AccountingClient(BaseClient):
    def __init__(self):
        super().__init__(
            settings.accounting_api_base,
            settings.accounting_api_token
        )

    async def post_transaction(self, data: dict):
        """Post accounting transaction"""
        return await self.post("/transactions", data)
''',
}

# Security/Auth
SECURITY_CONTENT = {
    "security/__init__.py": "",

    "security/auth.py": '''"""Authentication and authorization"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from prss.config import settings
from prss.db import get_db
from prss.models.all_models import User
from prss.schemas.user import TokenData
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    from datetime import datetime, timedelta
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.prss_jwt_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.prss_jwt_secret, algorithm=settings.prss_jwt_algorithm)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.prss_jwt_secret,
            algorithms=[settings.prss_jwt_algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


def require_role(allowed_roles: list):
    """Dependency to check user role"""
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role.value not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker
''',
}

# Events/Outbox
EVENTS_CONTENT = {
    "events/__init__.py": "",

    "events/outbox.py": '''"""Outbox pattern implementation"""
from sqlalchemy.orm import Session
from prss.models.all_models import OutboxEvent
from prss.models.base import OutboxStatus
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class OutboxProcessor:
    """Process pending outbox events"""

    def __init__(self, db: Session):
        self.db = db

    def process_pending_events(self, batch_size: int = 10):
        """Process pending events"""
        events = self.db.query(OutboxEvent).filter(
            OutboxEvent.status == OutboxStatus.PENDING,
            OutboxEvent.retries < OutboxEvent.max_retries
        ).limit(batch_size).all()

        for event in events:
            try:
                self._send_event(event)
                event.status = OutboxStatus.SENT
                event.sent_at = datetime.utcnow()
                logger.info(f"Event {event.id} sent successfully")
            except Exception as e:
                event.retries += 1
                event.last_error = str(e)
                event.next_retry_at = datetime.utcnow() + timedelta(minutes=5 * event.retries)
                if event.retries >= event.max_retries:
                    event.status = OutboxStatus.FAILED
                logger.error(f"Failed to send event {event.id}: {e}")

        self.db.commit()

    def _send_event(self, event: OutboxEvent):
        """Send event to subscribers"""
        # Implementation depends on message broker (RabbitMQ, Kafka, etc.)
        # For now, just log
        logger.info(f"Sending event {event.topic}: {event.payload}")
''',
}

# Utils
UTILS_CONTENT = {
    "utils/__init__.py": "",

    "utils/logging.py": '''"""Logging configuration"""
import logging
import json
from pythonjsonlogger import jsonlogger
from prss.config import settings


def setup_logging():
    """Setup JSON logging"""
    logger = logging.getLogger()
    handler = logging.StreamHandler()

    if settings.log_format == "json":
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, settings.log_level))

    return logger
''',

    "utils/request_id.py": '''"""Request ID middleware"""
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add request ID to each request"""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response
''',
}


def create_file(filepath: str, content: str):
    """Create file with content"""
    full_path = BASE_DIR / "backend" / "src" / "prss" / filepath
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content)
    print(f"Created: {filepath}")


def main():
    """Generate all files"""
    print("Setting up PRSS system...")

    # Create all schema files
    print("\nCreating schemas...")
    for filepath, content in SCHEMAS_CONTENT.items():
        create_file(filepath, content)

    # Create all API files
    print("\nCreating API endpoints...")
    for filepath, content in API_CONTENT.items():
        create_file(filepath, content)

    # Create all service files
    print("\nCreating services...")
    for filepath, content in SERVICES_CONTENT.items():
        create_file(filepath, content)

    # Create integration files
    print("\nCreating integration clients...")
    for filepath, content in INTEGRATION_CONTENT.items():
        create_file(filepath, content)

    # Create security files
    print("\nCreating security components...")
    for filepath, content in SECURITY_CONTENT.items():
        create_file(filepath, content)

    # Create event files
    print("\nCreating event system...")
    for filepath, content in EVENTS_CONTENT.items():
        create_file(filepath, content)

    # Create util files
    print("\nCreating utilities...")
    for filepath, content in UTILS_CONTENT.items():
        create_file(filepath, content)

    print("\n✅ PRSS system structure created successfully!")
    print("\nNext steps:")
    print("1. cd apps/prss/backend")
    print("2. poetry install")
    print("3. alembic revision --autogenerate -m 'Initial schema'")
    print("4. alembic upgrade head")
    print("5. uvicorn prss.main:app --reload")


if __name__ == "__main__":
    main()
