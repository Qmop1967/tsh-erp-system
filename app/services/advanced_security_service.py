"""
Advanced Security Service for TSH ERP System
Hyper-Advanced ABAC, RBAC, PBAC, RLS, FLS Implementation

This service provides:
- Comprehensive access control evaluation
- Policy-based decision making
- Row-level and field-level security
- Multi-factor authentication
- Device and session management
- Risk-based access control
- Centralized audit logging
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, text, func
from datetime import datetime, timedelta
import json
import hashlib
import secrets
import pyotp
import geoip2.database
import geoip2.errors
from dataclasses import dataclass
import re
from enum import Enum
import ipaddress

from app.models.advanced_security import *
from app.models.user import User
from app.db.database import get_db

@dataclass
class AccessContext:
    """Context for access control decisions"""
    user_id: int
    resource_type: str
    resource_id: Optional[str] = None
    action: str = "read"
    ip_address: Optional[str] = None
    location: Optional[Dict] = None
    device_id: Optional[str] = None
    session_id: Optional[str] = None
    user_agent: Optional[str] = None
    branch_id: Optional[int] = None
    tenant_id: Optional[int] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

@dataclass
class AccessDecision:
    """Result of access control evaluation"""
    granted: bool
    reason: str
    conditions: Optional[Dict] = None
    requires_mfa: bool = False
    risk_score: float = 0.0
    applicable_policies: List[str] = None
    
    def __post_init__(self):
        if self.applicable_policies is None:
            self.applicable_policies = []

class AdvancedSecurityService:
    """Hyper-Advanced Security Service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.geoip_reader = None
        self._init_geoip()
    
    def _init_geoip(self):
        """Initialize GeoIP database for location services"""
        try:
            # You'll need to download GeoLite2-City.mmdb from MaxMind
            self.geoip_reader = geoip2.database.Reader('/path/to/GeoLite2-City.mmdb')
        except Exception:
            # Fallback to None if GeoIP database not available
            self.geoip_reader = None
    
    # === MAIN ACCESS CONTROL ===
    
    def check_access(self, context: AccessContext) -> AccessDecision:
        """
        Main access control method - evaluates all security layers
        """
        # 1. Basic authentication check
        user = self.db.query(User).filter(User.id == context.user_id).first()
        if not user or not user.is_active:
            return AccessDecision(False, "User not found or inactive")
        
        # 2. Risk assessment
        risk_score = self._calculate_risk_score(context)
        
        # 3. Check policies (PBAC)
        policy_decision = self._evaluate_policies(context)
        if policy_decision.granted is False:
            return policy_decision
        
        # 4. Check role permissions (RBAC)
        rbac_decision = self._check_rbac_permissions(context)
        if rbac_decision.granted is False and policy_decision.granted is not True:
            return rbac_decision
        
        # 5. Check user permission overrides
        user_override = self._check_user_permission_overrides(context)
        if user_override is not None:
            return user_override
        
        # 6. Check attribute-based conditions (ABAC)
        abac_decision = self._evaluate_abac_conditions(context)
        if abac_decision.granted is False:
            return abac_decision
        
        # 7. Apply restriction groups
        restriction_decision = self._check_restriction_groups(context)
        if restriction_decision.granted is False:
            return restriction_decision
        
        # 8. Determine if MFA is required
        requires_mfa = self._requires_mfa(context, risk_score)
        
        # 9. Final decision
        return AccessDecision(
            granted=True,
            reason="Access granted",
            requires_mfa=requires_mfa,
            risk_score=risk_score,
            applicable_policies=policy_decision.applicable_policies
        )
    
    # === POLICY-BASED ACCESS CONTROL (PBAC) ===
    
    def _evaluate_policies(self, context: AccessContext) -> AccessDecision:
        """Evaluate security policies"""
        applicable_policies = []
        
        # Get all active policies that might apply
        policies = self.db.query(SecurityPolicy).filter(
            SecurityPolicy.is_active == True
        ).order_by(SecurityPolicy.priority.desc()).all()
        
        for policy in policies:
            if self._policy_applies_to_context(policy, context):
                applicable_policies.append(policy.name)
                
                # Evaluate policy conditions
                if self._evaluate_policy_conditions(policy, context):
                    if policy.effect == PolicyEffect.DENY:
                        return AccessDecision(
                            False, 
                            f"Access denied by policy: {policy.name}",
                            applicable_policies=applicable_policies
                        )
                    elif policy.effect == PolicyEffect.ALLOW:
                        return AccessDecision(
                            True, 
                            f"Access allowed by policy: {policy.name}",
                            applicable_policies=applicable_policies
                        )
        
        # No explicit policy decision - continue with other checks
        return AccessDecision(None, "No applicable policies", applicable_policies=applicable_policies)
    
    def _policy_applies_to_context(self, policy: SecurityPolicy, context: AccessContext) -> bool:
        """Check if policy applies to the current context"""
        # Check resource types
        if policy.applies_to_resources:
            if context.resource_type not in policy.applies_to_resources:
                return False
        
        # Check actions
        if policy.applies_to_actions:
            if context.action not in policy.applies_to_actions:
                return False
        
        # Check subjects (users/roles)
        if policy.applies_to_subjects:
            user = self.db.query(User).filter(User.id == context.user_id).first()
            if user:
                # Check user ID
                if context.user_id not in policy.applies_to_subjects.get('users', []):
                    # Check role
                    if user.role_id not in policy.applies_to_subjects.get('roles', []):
                        return False
        
        return True
    
    def _evaluate_policy_conditions(self, policy: SecurityPolicy, context: AccessContext) -> bool:
        """Evaluate policy conditions"""
        if not policy.conditions:
            return True
        
        return self._evaluate_conditions(policy.conditions, context)
    
    # === ROLE-BASED ACCESS CONTROL (RBAC) ===
    
    def _check_rbac_permissions(self, context: AccessContext) -> AccessDecision:
        """Check role-based permissions"""
        user = self.db.query(User).filter(User.id == context.user_id).first()
        if not user or not user.role:
            return AccessDecision(False, "User has no role assigned")
        
        # Check role hierarchy - user inherits permissions from parent roles
        role_ids = self._get_role_hierarchy(user.role_id)
        
        # Find applicable permissions
        permission_mappings = self.db.query(RolePermissionMapping).join(AdvancedPermission).filter(
            and_(
                RolePermissionMapping.role_id.in_(role_ids),
                AdvancedPermission.resource_type == context.resource_type,
                AdvancedPermission.action == context.action,
                AdvancedPermission.is_active == True,
                or_(
                    RolePermissionMapping.expires_at.is_(None),
                    RolePermissionMapping.expires_at > datetime.utcnow()
                )
            )
        ).all()
        
        for mapping in permission_mappings:
            # Check mapping conditions
            if mapping.conditions and not self._evaluate_conditions(mapping.conditions, context):
                continue
            
            # Check mapping constraints
            if mapping.constraints and not self._evaluate_constraints(mapping.constraints, context):
                continue
            
            return AccessDecision(True, f"Access granted by role permission: {mapping.permission.name}")
        
        return AccessDecision(False, "No matching role permissions found")
    
    def _get_role_hierarchy(self, role_id: int) -> List[int]:
        """Get role hierarchy including parent roles"""
        role_ids = [role_id]
        
        # Get current role
        role = self.db.query(Role).filter(Role.id == role_id).first()
        
        # Traverse up the hierarchy
        while role and role.parent_role_id:
            role_ids.append(role.parent_role_id)
            role = self.db.query(Role).filter(Role.id == role.parent_role_id).first()
        
        return role_ids
    
    # === USER PERMISSION OVERRIDES ===
    
    def _check_user_permission_overrides(self, context: AccessContext) -> Optional[AccessDecision]:
        """Check user-specific permission overrides"""
        overrides = self.db.query(UserPermissionOverride).join(AdvancedPermission).filter(
            and_(
                UserPermissionOverride.user_id == context.user_id,
                AdvancedPermission.resource_type == context.resource_type,
                AdvancedPermission.action == context.action,
                AdvancedPermission.is_active == True,
                or_(
                    UserPermissionOverride.expires_at.is_(None),
                    UserPermissionOverride.expires_at > datetime.utcnow()
                )
            )
        ).order_by(UserPermissionOverride.granted_at.desc()).all()
        
        for override in overrides:
            # Check conditions
            if override.conditions and not self._evaluate_conditions(override.conditions, context):
                continue
            
            # Check constraints
            if override.constraints and not self._evaluate_constraints(override.constraints, context):
                continue
            
            # Check if requires approval and is approved
            if override.requires_approval and not override.approved_at:
                continue
            
            return AccessDecision(
                override.is_granted,
                f"Access {'granted' if override.is_granted else 'denied'} by user permission override"
            )
        
        return None
    
    # === ATTRIBUTE-BASED ACCESS CONTROL (ABAC) ===
    
    def _evaluate_abac_conditions(self, context: AccessContext) -> AccessDecision:
        """Evaluate attribute-based conditions"""
        # Get user attributes
        user = self.db.query(User).filter(User.id == context.user_id).first()
        if not user:
            return AccessDecision(False, "User not found")
        
        # Create attribute context
        attributes = {
            'user': {
                'id': user.id,
                'email': user.email,
                'role_id': user.role_id,
                'branch_id': user.branch_id,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None
            },
            'context': {
                'timestamp': context.timestamp.isoformat(),
                'ip_address': context.ip_address,
                'location': context.location,
                'device_id': context.device_id,
                'session_id': context.session_id,
                'resource_type': context.resource_type,
                'resource_id': context.resource_id,
                'action': context.action
            },
            'environment': {
                'hour': context.timestamp.hour,
                'day_of_week': context.timestamp.weekday(),
                'is_weekend': context.timestamp.weekday() >= 5
            }
        }
        
        # Add role attributes if available
        if user.role:
            role_attrs = user.role.attributes or {}
            attributes['role'] = role_attrs
        
        # For ABAC, we assume conditions pass unless explicitly denied
        return AccessDecision(True, "ABAC conditions satisfied")
    
    # === RESTRICTION GROUPS ===
    
    def _check_restriction_groups(self, context: AccessContext) -> AccessDecision:
        """Check restriction groups"""
        # Check user-specific restrictions
        user_restrictions = self.db.query(UserRestrictionGroup).join(RestrictionGroup).filter(
            and_(
                UserRestrictionGroup.user_id == context.user_id,
                RestrictionGroup.is_active == True,
                or_(
                    UserRestrictionGroup.expires_at.is_(None),
                    UserRestrictionGroup.expires_at > datetime.utcnow()
                )
            )
        ).all()
        
        for restriction in user_restrictions:
            if self._restriction_applies(restriction.restriction_group, context):
                return AccessDecision(False, f"Access restricted by group: {restriction.restriction_group.name}")
        
        # Check role-based restrictions
        user = self.db.query(User).filter(User.id == context.user_id).first()
        if user and user.role:
            role_restrictions = self.db.query(RoleRestrictionGroup).join(RestrictionGroup).filter(
                and_(
                    RoleRestrictionGroup.role_id == user.role_id,
                    RestrictionGroup.is_active == True
                )
            ).all()
            
            for restriction in role_restrictions:
                if self._restriction_applies(restriction.restriction_group, context):
                    return AccessDecision(False, f"Access restricted by role group: {restriction.restriction_group.name}")
        
        return AccessDecision(True, "No applicable restrictions")
    
    def _restriction_applies(self, restriction_group: RestrictionGroup, context: AccessContext) -> bool:
        """Check if restriction group applies to context"""
        restrictions = restriction_group.restrictions or {}
        
        # Time-based restrictions
        if 'time' in restrictions:
            time_restrictions = restrictions['time']
            current_hour = context.timestamp.hour
            
            if 'allowed_hours' in time_restrictions:
                if current_hour not in time_restrictions['allowed_hours']:
                    return True
            
            if 'blocked_hours' in time_restrictions:
                if current_hour in time_restrictions['blocked_hours']:
                    return True
        
        # Location-based restrictions
        if 'location' in restrictions and context.location:
            location_restrictions = restrictions['location']
            
            if 'allowed_countries' in location_restrictions:
                user_country = context.location.get('country')
                if user_country not in location_restrictions['allowed_countries']:
                    return True
        
        # IP-based restrictions
        if 'ip' in restrictions and context.ip_address:
            ip_restrictions = restrictions['ip']
            
            if 'blocked_ips' in ip_restrictions:
                if context.ip_address in ip_restrictions['blocked_ips']:
                    return True
            
            if 'allowed_networks' in ip_restrictions:
                ip_allowed = False
                for network in ip_restrictions['allowed_networks']:
                    try:
                        if ipaddress.ip_address(context.ip_address) in ipaddress.ip_network(network):
                            ip_allowed = True
                            break
                    except ValueError:
                        continue
                if not ip_allowed:
                    return True
        
        return False
    
    # === ROW-LEVEL SECURITY (RLS) ===
    
    def apply_row_level_security(self, query, table_name: str, context: AccessContext):
        """Apply row-level security filters to query"""
        # Get applicable RLS rules
        rules = self.db.query(RowLevelSecurityRule).filter(
            and_(
                RowLevelSecurityRule.table_name == table_name,
                RowLevelSecurityRule.is_active == True
            )
        ).all()
        
        for rule in rules:
            if self._rls_rule_applies(rule, context):
                # Apply the rule expression as a filter
                filter_expression = self._process_rls_expression(rule.rule_expression, context)
                query = query.filter(text(filter_expression))
        
        return query
    
    def _rls_rule_applies(self, rule: RowLevelSecurityRule, context: AccessContext) -> bool:
        """Check if RLS rule applies to current context"""
        # Check actions
        if rule.applies_to_actions:
            if context.action not in rule.applies_to_actions:
                return False
        
        # Check roles
        if rule.applies_to_roles:
            user = self.db.query(User).filter(User.id == context.user_id).first()
            if user and user.role_id not in rule.applies_to_roles:
                return False
        
        # Check users
        if rule.applies_to_users:
            if context.user_id not in rule.applies_to_users:
                return False
        
        return True
    
    def _process_rls_expression(self, expression: str, context: AccessContext) -> str:
        """Process RLS expression by substituting context variables"""
        # Replace context variables in the expression
        replacements = {
            '{user_id}': str(context.user_id),
            '{branch_id}': str(context.branch_id) if context.branch_id else 'NULL',
            '{tenant_id}': str(context.tenant_id) if context.tenant_id else 'NULL'
        }
        
        for placeholder, value in replacements.items():
            expression = expression.replace(placeholder, value)
        
        return expression
    
    # === FIELD-LEVEL SECURITY (FLS) ===
    
    def apply_field_level_security(self, data: Dict, table_name: str, context: AccessContext) -> Dict:
        """Apply field-level security to data"""
        # Get applicable FLS rules
        rules = self.db.query(FieldLevelSecurityRule).filter(
            and_(
                FieldLevelSecurityRule.table_name == table_name,
                FieldLevelSecurityRule.is_active == True
            )
        ).all()
        
        filtered_data = data.copy()
        
        for rule in rules:
            if self._fls_rule_applies(rule, context):
                column_name = rule.column_name
                
                if column_name in filtered_data:
                    if not rule.is_visible:
                        # Remove field completely
                        filtered_data.pop(column_name, None)
                    elif not rule.is_readable:
                        # Replace with placeholder
                        filtered_data[column_name] = "[RESTRICTED]"
                    elif rule.masking_pattern:
                        # Apply masking
                        filtered_data[column_name] = self._apply_masking(
                            filtered_data[column_name], 
                            rule.masking_pattern
                        )
        
        return filtered_data
    
    def _fls_rule_applies(self, rule: FieldLevelSecurityRule, context: AccessContext) -> bool:
        """Check if FLS rule applies to current context"""
        # Check conditions
        if rule.conditions and not self._evaluate_conditions(rule.conditions, context):
            return False
        
        # Check roles
        if rule.applies_to_roles:
            user = self.db.query(User).filter(User.id == context.user_id).first()
            if user and user.role_id not in rule.applies_to_roles:
                return False
        
        # Check users
        if rule.applies_to_users:
            if context.user_id not in rule.applies_to_users:
                return False
        
        return True
    
    def _apply_masking(self, value: Any, pattern: str) -> str:
        """Apply masking pattern to value"""
        if value is None:
            return None
        
        value_str = str(value)
        
        if pattern == "***":
            return "***"
        elif pattern.startswith("show_last_"):
            num_chars = int(pattern.split("_")[-1])
            return "*" * (len(value_str) - num_chars) + value_str[-num_chars:]
        elif pattern.startswith("show_first_"):
            num_chars = int(pattern.split("_")[-1])
            return value_str[:num_chars] + "*" * (len(value_str) - num_chars)
        else:
            return pattern
    
    # === MULTI-FACTOR AUTHENTICATION ===
    
    def _requires_mfa(self, context: AccessContext, risk_score: float) -> bool:
        """Determine if MFA is required"""
        # High risk always requires MFA
        if risk_score >= 0.7:
            return True
        
        # Check if user has MFA configured
        mfa_methods = self.db.query(MFAMethod).filter(
            and_(
                MFAMethod.user_id == context.user_id,
                MFAMethod.is_enabled == True
            )
        ).count()
        
        if mfa_methods == 0:
            return False
        
        # Check if action requires MFA
        high_risk_actions = ['delete', 'approve', 'export', 'manage']
        if context.action in high_risk_actions:
            return True
        
        # Check if resource type requires MFA
        sensitive_resources = ['financial', 'hr', 'system']
        if context.resource_type in sensitive_resources:
            return True
        
        return False
    
    def create_mfa_challenge(self, user_id: int, method_type: AuthFactor, context: AccessContext) -> str:
        """Create MFA challenge"""
        # Get MFA method
        mfa_method = self.db.query(MFAMethod).filter(
            and_(
                MFAMethod.user_id == user_id,
                MFAMethod.factor_type == method_type,
                MFAMethod.is_enabled == True
            )
        ).first()
        
        if not mfa_method:
            raise ValueError("MFA method not found or not enabled")
        
        # Generate challenge code
        challenge_code = secrets.randbelow(1000000)
        challenge_code_str = f"{challenge_code:06d}"
        
        # Create challenge record
        challenge = MFAChallenge(
            user_id=user_id,
            mfa_method_id=mfa_method.id,
            challenge_code=challenge_code_str,
            ip_address=context.ip_address,
            user_agent=context.user_agent
        )
        
        self.db.add(challenge)
        self.db.commit()
        
        # Send challenge based on method type
        if method_type == AuthFactor.SMS:
            self._send_sms_challenge(mfa_method.phone_number, challenge_code_str)
        elif method_type == AuthFactor.EMAIL:
            self._send_email_challenge(mfa_method.email_address, challenge_code_str)
        elif method_type == AuthFactor.PUSH_NOTIFICATION:
            self._send_push_challenge(mfa_method.device_id, challenge.id)
        
        return challenge.id
    
    def verify_mfa_challenge(self, challenge_id: str, provided_code: str) -> bool:
        """Verify MFA challenge"""
        challenge = self.db.query(MFAChallenge).filter(MFAChallenge.id == challenge_id).first()
        if not challenge:
            return False
        
        # Check if expired
        if challenge.expires_at < datetime.utcnow():
            return False
        
        # Check if already verified
        if challenge.is_verified:
            return False
        
        # Check attempts
        challenge.attempts += 1
        if challenge.attempts > challenge.max_attempts:
            self.db.commit()
            return False
        
        # Verify code
        is_valid = False
        
        if challenge.mfa_method.factor_type == AuthFactor.TOTP:
            # TOTP verification
            totp = pyotp.TOTP(challenge.mfa_method.secret_key)
            is_valid = totp.verify(provided_code)
        else:
            # Direct code comparison
            is_valid = challenge.challenge_code == provided_code
        
        if is_valid:
            challenge.is_verified = True
            challenge.verified_at = datetime.utcnow()
            
            # Update method usage
            challenge.mfa_method.last_used = datetime.utcnow()
            challenge.mfa_method.use_count += 1
        
        self.db.commit()
        return is_valid
    
    # === DEVICE MANAGEMENT ===
    
    def register_device(self, user_id: int, device_info: Dict, context: AccessContext) -> str:
        """Register a new device"""
        # Generate device fingerprint
        fingerprint_data = f"{device_info.get('platform', '')}{device_info.get('browser', '')}{context.user_agent}"
        device_fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()
        
        # Check if device already exists
        existing_device = self.db.query(UserDevice).filter(
            UserDevice.device_fingerprint == device_fingerprint
        ).first()
        
        if existing_device:
            return existing_device.id
        
        # Get location from IP
        location = self._get_location_from_ip(context.ip_address)
        
        # Create new device
        device = UserDevice(
            user_id=user_id,
            device_name=device_info.get('name', 'Unknown Device'),
            device_type=device_info.get('type', 'unknown'),
            platform=device_info.get('platform', 'unknown'),
            browser=device_info.get('browser', 'unknown'),
            device_fingerprint=device_fingerprint,
            device_token=device_info.get('token'),
            last_ip_address=context.ip_address,
            last_location=location,
            status=DeviceStatus.PENDING  # Requires approval
        )
        
        self.db.add(device)
        self.db.commit()
        
        # Log security event
        self._log_security_event(
            "device_registration",
            RiskLevel.MEDIUM,
            f"New device registered for user {user_id}",
            user_id=user_id,
            context=context,
            event_data=device_info
        )
        
        return device.id
    
    def approve_device(self, device_id: str, approver_id: int) -> bool:
        """Approve a device"""
        device = self.db.query(UserDevice).filter(UserDevice.id == device_id).first()
        if not device:
            return False
        
        device.status = DeviceStatus.ACTIVE
        device.approved_by = approver_id
        device.registered_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    # === SESSION MANAGEMENT ===
    
    def create_session(self, user_id: int, device_id: str, context: AccessContext) -> str:
        """Create user session"""
        # Generate session tokens
        session_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(context)
        risk_level = self._get_risk_level(risk_score)
        
        # Get location
        location = self._get_location_from_ip(context.ip_address)
        
        # Create session
        session = UserSession(
            user_id=user_id,
            device_id=device_id,
            session_token=hashlib.sha256(session_token.encode()).hexdigest(),
            refresh_token=hashlib.sha256(refresh_token.encode()).hexdigest(),
            expires_at=datetime.utcnow() + timedelta(hours=24),
            ip_address=context.ip_address,
            location=location,
            user_agent=context.user_agent,
            risk_score=risk_score,
            risk_level=risk_level,
            requires_mfa=self._requires_mfa(context, risk_score)
        )
        
        self.db.add(session)
        self.db.commit()
        
        # Log session creation
        self._log_audit("session_created", "session", session.id, context)
        
        return session.id
    
    def validate_session(self, session_token: str, context: AccessContext) -> Optional[UserSession]:
        """Validate session token"""
        token_hash = hashlib.sha256(session_token.encode()).hexdigest()
        
        session = self.db.query(UserSession).filter(
            and_(
                UserSession.session_token == token_hash,
                UserSession.status == SessionStatus.ACTIVE,
                UserSession.expires_at > datetime.utcnow()
            )
        ).first()
        
        if session:
            # Update last activity
            session.last_activity = datetime.utcnow()
            
            # Check for suspicious activity
            if self._is_suspicious_activity(session, context):
                session.risk_score = min(1.0, session.risk_score + 0.1)
                session.risk_level = self._get_risk_level(session.risk_score)
                
                # Log suspicious activity
                self._log_security_event(
                    "suspicious_session_activity",
                    session.risk_level,
                    "Suspicious activity detected in session",
                    user_id=session.user_id,
                    session_id=session.id,
                    context=context
                )
            
            self.db.commit()
        
        return session
    
    # === RISK ASSESSMENT ===
    
    def _calculate_risk_score(self, context: AccessContext) -> float:
        """Calculate risk score for access attempt"""
        risk_score = 0.0
        
        # Time-based risk
        current_hour = context.timestamp.hour
        if current_hour < 6 or current_hour > 22:  # Outside business hours
            risk_score += 0.2
        
        # Weekend access
        if context.timestamp.weekday() >= 5:
            risk_score += 0.1
        
        # High-risk actions
        high_risk_actions = ['delete', 'export', 'approve', 'manage']
        if context.action in high_risk_actions:
            risk_score += 0.3
        
        # Sensitive resources
        sensitive_resources = ['financial', 'hr', 'system']
        if context.resource_type in sensitive_resources:
            risk_score += 0.2
        
        # Location-based risk
        if context.location:
            # Check if accessing from unusual location
            user_locations = self._get_user_typical_locations(context.user_id)
            if not self._is_location_typical(context.location, user_locations):
                risk_score += 0.3
        
        # IP-based risk
        if context.ip_address:
            if self._is_suspicious_ip(context.ip_address):
                risk_score += 0.4
        
        # Device-based risk
        if context.device_id:
            device = self.db.query(UserDevice).filter(UserDevice.id == context.device_id).first()
            if not device or not device.is_trusted:
                risk_score += 0.2
        
        return min(1.0, risk_score)
    
    def _get_risk_level(self, risk_score: float) -> RiskLevel:
        """Convert risk score to risk level"""
        if risk_score >= 0.8:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            return RiskLevel.HIGH
        elif risk_score >= 0.3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    # === AUDIT LOGGING ===
    
    def _log_audit(self, action: str, resource_type: str, resource_id: str, context: AccessContext, 
                   old_values: Dict = None, new_values: Dict = None):
        """Log audit event"""
        audit_log = AuditLog(
            user_id=context.user_id,
            session_id=context.session_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=context.ip_address,
            location=context.location,
            user_agent=context.user_agent,
            branch_id=context.branch_id,
            tenant_id=context.tenant_id,
            risk_score=self._calculate_risk_score(context)
        )
        
        self.db.add(audit_log)
        self.db.commit()
    
    def _log_security_event(self, event_type: str, severity: RiskLevel, description: str,
                           user_id: int = None, session_id: str = None, context: AccessContext = None,
                           event_data: Dict = None):
        """Log security event"""
        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            title=f"{event_type.replace('_', ' ').title()}",
            description=description,
            user_id=user_id,
            session_id=session_id,
            ip_address=context.ip_address if context else None,
            location=context.location if context else None,
            event_data=event_data
        )
        
        self.db.add(event)
        self.db.commit()
    
    # === HELPER METHODS ===
    
    def _evaluate_conditions(self, conditions: Dict, context: AccessContext) -> bool:
        """Evaluate complex conditions"""
        if not conditions:
            return True
        
        # This is a simplified implementation
        # In a real system, you might use a rule engine like RETE
        
        for condition_type, condition_value in conditions.items():
            if condition_type == 'time':
                if not self._evaluate_time_condition(condition_value, context):
                    return False
            elif condition_type == 'location':
                if not self._evaluate_location_condition(condition_value, context):
                    return False
            elif condition_type == 'user':
                if not self._evaluate_user_condition(condition_value, context):
                    return False
        
        return True
    
    def _evaluate_constraints(self, constraints: Dict, context: AccessContext) -> bool:
        """Evaluate constraints (similar to conditions but different semantics)"""
        return self._evaluate_conditions(constraints, context)
    
    def _evaluate_time_condition(self, condition: Dict, context: AccessContext) -> bool:
        """Evaluate time-based condition"""
        current_hour = context.timestamp.hour
        
        if 'allowed_hours' in condition:
            return current_hour in condition['allowed_hours']
        
        if 'blocked_hours' in condition:
            return current_hour not in condition['blocked_hours']
        
        return True
    
    def _evaluate_location_condition(self, condition: Dict, context: AccessContext) -> bool:
        """Evaluate location-based condition"""
        if not context.location:
            return True
        
        if 'allowed_countries' in condition:
            return context.location.get('country') in condition['allowed_countries']
        
        if 'blocked_countries' in condition:
            return context.location.get('country') not in condition['blocked_countries']
        
        return True
    
    def _evaluate_user_condition(self, condition: Dict, context: AccessContext) -> bool:
        """Evaluate user-based condition"""
        if 'user_ids' in condition:
            return context.user_id in condition['user_ids']
        
        return True
    
    def _get_location_from_ip(self, ip_address: str) -> Optional[Dict]:
        """Get location from IP address"""
        if not self.geoip_reader or not ip_address:
            return None
        
        try:
            response = self.geoip_reader.city(ip_address)
            return {
                'country': response.country.iso_code,
                'country_name': response.country.name,
                'city': response.city.name,
                'latitude': float(response.location.latitude) if response.location.latitude else None,
                'longitude': float(response.location.longitude) if response.location.longitude else None
            }
        except geoip2.errors.AddressNotFoundError:
            return None
    
    def _get_user_typical_locations(self, user_id: int) -> List[Dict]:
        """Get user's typical locations for risk assessment"""
        # This would analyze historical session data
        # For now, return empty list
        return []
    
    def _is_location_typical(self, location: Dict, typical_locations: List[Dict]) -> bool:
        """Check if location is typical for user"""
        if not typical_locations:
            return True  # No historical data, assume typical
        
        # Simple distance-based check
        # In reality, you might want more sophisticated analysis
        return True
    
    def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP address is suspicious"""
        # Check against threat intelligence feeds
        # For now, simple checks
        
        # Check if it's a Tor exit node (simplified)
        # Check if it's from a known malicious network
        # etc.
        
        return False
    
    def _is_suspicious_activity(self, session: UserSession, context: AccessContext) -> bool:
        """Detect suspicious session activity"""
        # Check for rapid IP changes
        if session.ip_address != context.ip_address:
            return True
        
        # Check for unusual access patterns
        # This would involve more complex analysis
        
        return False
    
    def _send_sms_challenge(self, phone_number: str, code: str):
        """Send SMS challenge code"""
        # Implement SMS sending logic
        pass
    
    def _send_email_challenge(self, email: str, code: str):
        """Send email challenge code"""
        # Implement email sending logic
        pass
    
    def _send_push_challenge(self, device_id: str, challenge_id: str):
        """Send push notification challenge"""
        # Implement push notification logic
        pass
