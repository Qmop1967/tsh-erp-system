"""
MFA Mobile Application Service for TSH ERP System
Advanced Multi-Factor Authentication and Device Management

This service provides:
- Mobile MFA authentication
- Device registration and approval
- Session management from mobile
- Location-based access control
- Push notifications for access requests
- Passless authentication
"""

from typing import Dict, List, Any, Optional, Union
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
import secrets
import hashlib
import pyotp
import qrcode
import io
import base64
from PIL import Image
import requests
from dataclasses import dataclass

from app.models.advanced_security import *
from app.models.user import User
from app.services.advanced_security_service import AdvancedSecurityService, AccessContext

@dataclass
class MFARequest:
    """MFA request from main application"""
    request_id: str
    user_id: int
    description: str
    ip_address: str
    location: Dict
    user_agent: str
    risk_level: str
    expires_at: datetime

@dataclass
class DeviceInfo:
    """Device information for registration"""
    name: str
    type: str  # mobile, tablet, desktop
    platform: str  # iOS, Android, Windows, etc.
    version: str
    model: str
    manufacturer: str
    app_version: str

class MFAMobileService:
    """MFA Mobile Application Service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.security_service = AdvancedSecurityService(db)
    
    # === DEVICE REGISTRATION ===
    
    def register_mobile_device(self, user_id: int, device_info: DeviceInfo, 
                              push_token: str, context: AccessContext) -> Dict:
        """Register mobile device for MFA""""
        try:
            # Create device fingerprint
            fingerprint_data = f"{device_info.platform}{device_info.model}{device_info.manufacturer}"
            device_fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()
            
            # Check if device already exists
            existing_device = self.db.query(UserDevice).filter(
                and_(
                    UserDevice.user_id == user_id,
                    UserDevice.device_fingerprint == device_fingerprint
                )
            ).first()
            
            if existing_device:
                # Update existing device
                existing_device.device_token = push_token
                existing_device.last_seen = datetime.utcnow()
                existing_device.last_ip_address = context.ip_address
                self.db.commit()
                
                return {
                    "success": True,
                    "device_id": existing_device.id,
                    "status": existing_device.status.value,
                    "requires_approval": existing_device.status == DeviceStatus.PENDING
                }
            
            # Get location from IP
            location = self.security_service._get_location_from_ip(context.ip_address)
            
            # Create new device
            device = UserDevice(
                user_id=user_id,
                device_name=device_info.name,
                device_type=device_info.type,
                platform=device_info.platform,
                browser=f"{device_info.platform} {device_info.version}",
                device_fingerprint=device_fingerprint,
                device_token=push_token,
                last_ip_address=context.ip_address,
                last_location=location,
                status=DeviceStatus.PENDING
            )
            
            self.db.add(device)
            self.db.commit()
            
            # Log security event
            self.security_service._log_security_event(
                "mobile_device_registration",
                RiskLevel.MEDIUM,
                f"Mobile device registered: {device_info.name}",
                user_id=user_id,
                context=context,
                event_data={
                    "device_name": device_info.name,
                    "platform": device_info.platform,
                    "model": device_info.model
                }
            )
            
            # Send approval notification to admin
            self._notify_admins_device_approval_needed(device)
            
            return {
                "success": True,
                "device_id": device.id,
                "status": "pending",
                "requires_approval": True,
                "message": "Device registered successfully. Waiting for admin approval."
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def approve_mobile_device(self, device_id: str, approver_id: int) -> Dict:
        """Approve mobile device"""
        try:
            device = self.db.query(UserDevice).filter(UserDevice.id == device_id).first()
            if not device:
                return {"success": False, "error": "Device not found"}
            
            device.status = DeviceStatus.ACTIVE
            device.is_trusted = True
            device.approved_by = approver_id
            device.registered_at = datetime.utcnow()
            
            self.db.commit()
            
            # Send approval notification to user
            self._send_device_approved_notification(device)
            
            return {
                "success": True,
                "message": "Device approved successfully"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_pending_devices(self) -> List[Dict]:
        """Get devices pending approval"""
        devices = self.db.query(UserDevice).join(User).filter(
            UserDevice.status == DeviceStatus.PENDING
        ).all()
        
        result = []
        for device in devices:
            result.append({
                "device_id": device.id,
                "user_id": device.user_id,
                "user_email": device.user.email,
                "user_name": device.user.full_name,
                "device_name": device.device_name,
                "device_type": device.device_type,
                "platform": device.platform,
                "location": device.last_location,
                "ip_address": device.last_ip_address,
                "first_seen": device.first_seen.isoformat(),
                "risk_assessment": self._assess_device_risk(device)
            })
        
        return result
    
    # === MFA SETUP ===
    
    def setup_totp(self, user_id: int) -> Dict:
        """Setup TOTP (Time-based One-Time Password) for user"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Check if TOTP already exists
            existing_totp = self.db.query(MFAMethod).filter(
                and_(
                    MFAMethod.user_id == user_id,
                    MFAMethod.factor_type == AuthFactor.TOTP
                )
            ).first()
            
            if existing_totp:
                return {"success": False, "error": "TOTP already configured"}
            
            # Generate secret key
            secret_key = pyotp.random_base32()
            
            # Create TOTP URI for QR code
            totp_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(
                name=user.email,
                issuer_name="TSH ERP System"
            )
            
            # Generate QR code
            qr_code_data = self._generate_qr_code(totp_uri)
            
            # Create MFA method (but don't enable until verified)
            mfa_method = MFAMethod(
                user_id=user_id,
                factor_type=AuthFactor.TOTP,
                secret_key=secret_key,
                is_enabled=False  # Enable after verification
            )
            
            self.db.add(mfa_method)
            self.db.commit()
            
            return {
                "success": True,
                "secret_key": secret_key,
                "qr_code": qr_code_data,
                "totp_uri": totp_uri,
                "mfa_method_id": mfa_method.id
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def verify_totp_setup(self, mfa_method_id: int, verification_code: str) -> Dict:
        """Verify TOTP setup"""
        try:
            mfa_method = self.db.query(MFAMethod).filter(MFAMethod.id == mfa_method_id).first()
            if not mfa_method:
                return {"success": False, "error": "MFA method not found"}
            
            # Verify the code
            totp = pyotp.TOTP(mfa_method.secret_key)
            if totp.verify(verification_code):
                # Enable the method
                mfa_method.is_enabled = True
                
                # Generate backup codes
                backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
                mfa_method.backup_codes = backup_codes
                mfa_method.backup_codes_used = []
                
                self.db.commit()
                
                return {
                    "success": True,
                    "backup_codes": backup_codes,
                    "message": "TOTP configured successfully"
                }
            else:
                return {"success": False, "error": "Invalid verification code"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def setup_push_notifications(self, user_id: int, device_id: str) -> Dict:
        """Setup push notification MFA"""
        try:
            device = self.db.query(UserDevice).filter(
                and_(
                    UserDevice.id == device_id,
                    UserDevice.user_id == user_id,
                    UserDevice.status == DeviceStatus.ACTIVE
                )
            ).first()
            
            if not device or not device.device_token:
                return {"success": False, "error": "Active device with push token required"}
            
            # Check if push MFA already exists
            existing_push = self.db.query(MFAMethod).filter(
                and_(
                    MFAMethod.user_id == user_id,
                    MFAMethod.factor_type == AuthFactor.PUSH_NOTIFICATION
                )
            ).first()
            
            if existing_push:
                # Update device ID
                existing_push.device_id = device_id
                existing_push.is_enabled = True
            else:
                # Create new push MFA method
                mfa_method = MFAMethod(
                    user_id=user_id,
                    factor_type=AuthFactor.PUSH_NOTIFICATION,
                    device_id=device_id,
                    is_enabled=True
                )
                self.db.add(mfa_method)
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "Push notification MFA configured successfully"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # === MFA AUTHENTICATION ===
    
    def create_mfa_request(self, user_id: int, description: str, context: AccessContext) -> str:
        """Create MFA request for push notification"""
        request_id = secrets.token_urlsafe(16)
        
        # Store MFA request (you might want to use Redis for this)
        mfa_request = MFARequest(
            request_id=request_id,
            user_id=user_id,
            description=description,
            ip_address=context.ip_address,
            location=context.location or {},
            user_agent=context.user_agent,
            risk_level=self.security_service._get_risk_level(
                self.security_service._calculate_risk_score(context)
            ).value,
            expires_at=datetime.utcnow() + timedelta(minutes=5)
        )
        
        # Store in database temporarily (in production, use Redis)
        # For now, we'll use the session activity table
        from app.models.advanced_security import SessionActivity
        activity = SessionActivity(
            session_id=context.session_id,
            activity_type="mfa_request",
            activity_description=json.dumps({
                "request_id": request_id,
                "description": description,
                "expires_at": mfa_request.expires_at.isoformat()
            }),
            ip_address=context.ip_address,
            location=context.location,
            user_agent=context.user_agent
        )
        
        self.db.add(activity)
        self.db.commit()
        
        # Send push notification
        self._send_mfa_push_notification(user_id, mfa_request)
        
        return request_id
    
    def handle_mfa_response(self, request_id: str, user_id: int, approved: bool, 
                           device_id: str) -> Dict:
        """Handle MFA response from mobile app"""
        try:
            # Find the MFA request
            activity = self.db.query(SessionActivity).filter(
                SessionActivity.activity_type == "mfa_request"
            ).filter(
                SessionActivity.activity_description.contains(request_id)
            ).first()
            
            if not activity:
                return {"success": False, "error": "MFA request not found"}
            
            # Parse request data
            request_data = json.loads(activity.activity_description)
            expires_at = datetime.fromisoformat(request_data["expires_at"])
            
            if datetime.utcnow() > expires_at:
                return {"success": False, "error": "MFA request expired"}
            
            # Verify device belongs to user
            device = self.db.query(UserDevice).filter(
                and_(
                    UserDevice.id == device_id,
                    UserDevice.user_id == user_id,
                    UserDevice.status == DeviceStatus.ACTIVE
                )
            ).first()
            
            if not device:
                return {"success": False, "error": "Invalid device"}
            
            # Log the response
            self.security_service._log_audit(
                "mfa_response",
                "authentication",
                request_id,
                AccessContext(
                    user_id=user_id,
                    resource_type="authentication",
                    action="mfa_verify",
                    device_id=device_id
                ),
                new_values={"approved": approved}
            )
            
            # Mark request as handled
            activity.activity_description = json.dumps({
                **request_data,
                "handled": True,
                "approved": approved,
                "handled_at": datetime.utcnow().isoformat()
            })
            
            self.db.commit()
            
            return {
                "success": True,
                "approved": approved,
                "message": f"MFA request {'approved' if approved else 'denied'}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_pending_mfa_requests(self, user_id: int) -> List[Dict]:
        """Get pending MFA requests for user"""
        activities = self.db.query(SessionActivity).filter(
            SessionActivity.activity_type == "mfa_request"
        ).all()
        
        pending_requests = []
        for activity in activities:
            try:
                request_data = json.loads(activity.activity_description)
                
                # Skip if already handled
                if request_data.get("handled"):
                    continue
                
                # Skip if expired
                expires_at = datetime.fromisoformat(request_data["expires_at"])
                if datetime.utcnow() > expires_at:
                    continue
                
                # Get session user
                session = self.db.query(UserSession).filter(
                    UserSession.id == activity.session_id
                ).first()
                
                if session and session.user_id == user_id:
                    pending_requests.append({
                        "request_id": request_data["request_id"],
                        "description": request_data["description"],
                        "ip_address": activity.ip_address,
                        "location": activity.location,
                        "user_agent": activity.user_agent,
                        "timestamp": activity.timestamp.isoformat(),
                        "expires_at": request_data["expires_at"]
                    })
                    
            except (json.JSONDecodeError, KeyError):
                continue
        
        return pending_requests
    
    # === SESSION MANAGEMENT ===
    
    def get_user_sessions(self, user_id: int) -> List[Dict]:
        """Get all active sessions for user"""
        sessions = self.db.query(UserSession).filter(
            and_(
                UserSession.user_id == user_id,
                UserSession.status == SessionStatus.ACTIVE,
                UserSession.expires_at > datetime.utcnow()
            )
        ).order_by(UserSession.last_activity.desc()).all()
        
        result = []
        for session in sessions:
            device_info = {}
            if session.device:
                device_info = {
                    "device_id": session.device.id,
                    "device_name": session.device.device_name,
                    "device_type": session.device.device_type,
                    "platform": session.device.platform,
                    "is_trusted": session.device.is_trusted
                }
            
            result.append({
                "session_id": session.id,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "expires_at": session.expires_at.isoformat() if session.expires_at else None,
                "ip_address": session.ip_address,
                "location": session.location,
                "risk_level": session.risk_level.value,
                "is_mobile": session.is_mobile,
                "device": device_info,
                "is_current": session.id == session.id  # You'd need to pass current session ID
            })
        
        return result
    
    def terminate_session(self, session_id: str, terminated_by: int) -> Dict:
        """Terminate a specific session"""
        try:
            session = self.db.query(UserSession).filter(UserSession.id == session_id).first()
            if not session:
                return {"success": False, "error": "Session not found"}
            
            session.status = SessionStatus.TERMINATED
            session.terminated_at = datetime.utcnow()
            
            self.db.commit()
            
            # Log session termination
            self.security_service._log_audit(
                "session_terminated",
                "session",
                session_id,
                AccessContext(
                    user_id=terminated_by,
                    resource_type="session",
                    action="terminate"
                )
            )
            
            return {"success": True, "message": "Session terminated successfully"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def terminate_all_other_sessions(self, user_id: int, current_session_id: str) -> Dict:
        """Terminate all other sessions for user"""
        try:
            sessions = self.db.query(UserSession).filter(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.id != current_session_id,
                    UserSession.status == SessionStatus.ACTIVE
                )
            ).all()
            
            count = 0
            for session in sessions:
                session.status = SessionStatus.TERMINATED
                session.terminated_at = datetime.utcnow()
                count += 1
            
            self.db.commit()
            
            return {
                "success": True,
                "message": f"Terminated {count} sessions"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # === PASSLESS AUTHENTICATION ===
    
    def create_passless_token(self, email: str, token_type: str, context: AccessContext) -> Dict:
        """Create passless authentication token"""
        try:
            # Find user by email
            user = self.db.query(User).filter(User.email == email).first()
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Generate token
            token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # Create passless token record
            passless_token = PasslessToken(
                user_id=user.id,
                token_type=token_type,
                token_hash=token_hash,
                ip_address=context.ip_address,
                user_agent=context.user_agent,
                location=context.location
            )
            
            self.db.add(passless_token)
            self.db.commit()
            
            if token_type == "magic_link":
                # Send magic link via email
                magic_link = f"https://your-app.com/auth/magic-link?token={token}"
                self._send_magic_link_email(user.email, magic_link)
                
                return {
                    "success": True,
                    "message": "Magic link sent to your email"
                }
                
            elif token_type == "qr_code":
                # Generate QR code for mobile app
                qr_data = {
                    "token": token,
                    "user_id": user.id,
                    "expires_at": passless_token.expires_at.isoformat()
                }
                qr_code_data = self._generate_qr_code(json.dumps(qr_data))
                
                return {
                    "success": True,
                    "qr_code": qr_code_data,
                    "expires_at": passless_token.expires_at.isoformat()
                }
            
            return {"success": False, "error": "Invalid token type"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def verify_passless_token(self, token: str, context: AccessContext) -> Dict:
        """Verify passless authentication token"""
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            passless_token = self.db.query(PasslessToken).filter(
                and_(
                    PasslessToken.token_hash == token_hash,
                    PasslessToken.is_used == False,
                    PasslessToken.expires_at > datetime.utcnow()
                )
            ).first()
            
            if not passless_token:
                return {"success": False, "error": "Invalid or expired token"}
            
            # Check attempts
            passless_token.attempts += 1
            if passless_token.attempts > passless_token.max_attempts:
                self.db.commit()
                return {"success": False, "error": "Too many attempts"}
            
            # Mark as used
            passless_token.is_used = True
            passless_token.used_at = datetime.utcnow()
            
            self.db.commit()
            
            # Create session for user
            session_id = self.security_service.create_session(
                passless_token.user_id,
                passless_token.device_id,
                context
            )
            
            return {
                "success": True,
                "user_id": passless_token.user_id,
                "session_id": session_id,
                "message": "Authentication successful"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # === UTILITY METHODS ===
    
    def _generate_qr_code(self, data: str) -> str:
        """Generate QR code and return as base64 string"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def _assess_device_risk(self, device: UserDevice) -> Dict:
        """Assess risk level of device registration"""
        risk_score = 0.0
        risk_factors = []
        
        # New device from new location
        if not device.last_location:
            risk_score += 0.2
            risk_factors.append("Unknown location")
        
        # Mobile device (generally higher risk)
        if device.device_type == "mobile":
            risk_score += 0.1
            risk_factors.append("Mobile device")
        
        # First time registration
        risk_score += 0.3
        risk_factors.append("New device")
        
        return {
            "risk_score": min(1.0, risk_score),
            "risk_level": self.security_service._get_risk_level(risk_score).value,
            "risk_factors": risk_factors
        }
    
    def _send_mfa_push_notification(self, user_id: int, mfa_request: MFARequest):
        """Send push notification for MFA request"""
        # Get user's push-enabled devices
        devices = self.db.query(UserDevice).filter(
            and_(
                UserDevice.user_id == user_id,
                UserDevice.status == DeviceStatus.ACTIVE,
                UserDevice.device_token.isnot(None)
            )
        ).all()
        
        for device in devices:
            # Send push notification
            # This would integrate with your push notification service (FCM, APNS, etc.)
            self._send_push_notification(
                device.device_token,
                "TSH ERP - Authentication Request",
                f"Approve access request: {mfa_request.description}",
                {
                    "type": "mfa_request",
                    "request_id": mfa_request.request_id,
                    "description": mfa_request.description,
                    "risk_level": mfa_request.risk_level
                }
            )
    
    def _send_push_notification(self, device_token: str, title: str, body: str, data: Dict):
        """Send push notification to device"""
        # Implement push notification sending
        # This would use FCM for Android, APNS for iOS
        pass
    
    def _send_magic_link_email(self, email: str, magic_link: str):
        """Send magic link via email"""
        # Implement email sending
        pass
    
    def _send_device_approved_notification(self, device: UserDevice):
        """Send device approval notification"""
        if device.device_token:
            self._send_push_notification(
                device.device_token,
                "TSH ERP - Device Approved",
                "Your device has been approved for access",
                {"type": "device_approved"}
            )
    
    def _notify_admins_device_approval_needed(self, device: UserDevice):
        """Notify administrators that device approval is needed"""
        # Get admin users
        admin_users = self.db.query(User).join(Role).filter(
            Role.name == "Admin"
        ).all()
        
        for admin in admin_users:
            # Send notification (email, push, etc.)
            pass
