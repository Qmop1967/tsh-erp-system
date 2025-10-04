"""
Advanced Security Configuration for TSH ERP System

This module contains all security configuration settings including:
- Security policies
- Risk thresholds
- MFA settings
- Session management
- Audit settings
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import os

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityConfig:
    """Main security configuration"""
    
    # === GENERAL SECURITY ===
    ENCRYPTION_KEY: str = os.getenv('SECURITY_ENCRYPTION_KEY', 'your-256-bit-encryption-key-here')
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-here')
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # === PASSWORD POLICY ===
    PASSWORD_MIN_LENGTH: int = 12
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SYMBOLS: bool = True
    PASSWORD_HISTORY_COUNT: int = 5  # Remember last 5 passwords
    PASSWORD_EXPIRY_DAYS: int = 90
    PASSWORD_MAX_ATTEMPTS: int = 5
    PASSWORD_LOCKOUT_DURATION: int = 30  # minutes
    
    # === MFA SETTINGS ===
    MFA_ENABLED: bool = True
    MFA_REQUIRED_FOR_ADMINS: bool = True
    MFA_CODE_LENGTH: int = 6
    MFA_CODE_EXPIRY_MINUTES: int = 5
    MFA_MAX_ATTEMPTS: int = 3
    MFA_BACKUP_CODES_COUNT: int = 10
    
    # === SESSION MANAGEMENT ===
    SESSION_TIMEOUT_MINUTES: int = 60
    SESSION_ABSOLUTE_TIMEOUT_HOURS: int = 24
    MAX_CONCURRENT_SESSIONS: int = 3
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Strict"
    
    # === DEVICE MANAGEMENT ===
    DEVICE_REGISTRATION_REQUIRES_APPROVAL: bool = True
    DEVICE_TRUST_DURATION_DAYS: int = 30
    MAX_DEVICES_PER_USER: int = 5
    DEVICE_FINGERPRINTING_ENABLED: bool = True
    
    # === RISK ASSESSMENT ===
    RISK_SCORE_THRESHOLDS: Dict[str, float] = {
        'low': 0.3,
        'medium': 0.6,
        'high': 0.8,
        'critical': 0.9
    }
    
    # Risk factors and their weights
    RISK_FACTORS: Dict[str, float] = {
        'unusual_time': 0.2,
        'weekend_access': 0.1,
        'new_location': 0.3,
        'new_device': 0.2,
        'high_risk_action': 0.3,
        'sensitive_resource': 0.2,
        'multiple_failed_attempts': 0.4,
        'suspicious_ip': 0.4,
        'unusual_user_agent': 0.1,
        'rapid_requests': 0.2
    }
    
    # === AUDIT LOGGING ===
    AUDIT_LOG_ALL_ACTIONS: bool = True
    AUDIT_LOG_RETENTION_DAYS: int = 365
    AUDIT_LOG_ENCRYPTION: bool = True
    AUDIT_LOG_INCLUDE_REQUEST_BODY: bool = False  # For sensitive data protection
    AUDIT_LOG_INCLUDE_RESPONSE_BODY: bool = False
    
    # === SECURITY MONITORING ===
    SECURITY_MONITORING_ENABLED: bool = True
    FAILED_LOGIN_THRESHOLD: int = 5
    FAILED_LOGIN_WINDOW_MINUTES: int = 15
    SUSPICIOUS_ACTIVITY_THRESHOLD: int = 10
    AUTOMATIC_ACCOUNT_LOCKOUT: bool = True
    SECURITY_ALERT_EMAIL_ENABLED: bool = True
    
    # === RATE LIMITING ===
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 100
    RATE_LIMIT_BURST_SIZE: int = 200
    RATE_LIMIT_BAN_DURATION_MINUTES: int = 60
    
    # === GEOLOCATION SECURITY ===
    GEOLOCATION_ENABLED: bool = True
    GEOLOCATION_REQUIRED: bool = False
    ALLOWED_COUNTRIES: List[str] = ['SA', 'AE', 'QA', 'KW', 'BH', 'OM']  # GCC countries
    BLOCKED_COUNTRIES: List[str] = []
    VPN_DETECTION_ENABLED: bool = True
    TOR_BLOCKING_ENABLED: bool = True
    
    # === API SECURITY ===
    API_KEY_REQUIRED: bool = True
    API_RATE_LIMITING: bool = True
    API_REQUEST_SIGNING: bool = False
    API_ENCRYPTION_REQUIRED: bool = False
    CORS_ALLOWED_ORIGINS: List[str] = ['http://localhost:3000', 'http://localhost:5173']
    
    # === DATA PROTECTION ===
    DATA_ENCRYPTION_AT_REST: bool = True
    DATA_ENCRYPTION_IN_TRANSIT: bool = True
    SENSITIVE_DATA_MASKING: bool = True
    PII_DETECTION_ENABLED: bool = True
    DATA_RETENTION_DAYS: int = 2555  # 7 years
    
    # === COMPLIANCE ===
    GDPR_COMPLIANCE: bool = True
    CCPA_COMPLIANCE: bool = True
    SOX_COMPLIANCE: bool = True
    ISO27001_COMPLIANCE: bool = True
    
    # === ADVANCED FEATURES ===
    BEHAVIORAL_ANALYSIS_ENABLED: bool = True
    MACHINE_LEARNING_RISK_SCORING: bool = False  # Requires ML models
    ZERO_TRUST_MODE: bool = False
    CONTINUOUS_AUTHENTICATION: bool = False

# Global security configuration instance
security_config = SecurityConfig()

# === SECURITY POLICIES ===

class SecurityPolicies:
    """Predefined security policies"""
    
    @staticmethod
    def get_default_policies() -> List[Dict[str, Any]]:
        """Get default security policies"""
        return [
            {
                "name": "admin_full_access",
                "display_name": "Administrator Full Access",
                "description": "Grants full system access to administrators",
                "policy_document": {
                    "version": "1.0",
                    "rules": [
                        {
                            "effect": "allow",
                            "actions": ["*"],
                            "resources": ["*"],
                            "conditions": {
                                "user": {
                                    "roles": ["admin"]
                                }
                            }
                        }
                    ]
                },
                "effect": "allow",
                "priority": 1000
            },
            {
                "name": "business_hours_only",
                "display_name": "Business Hours Access Only",
                "description": "Restricts access to business hours (9 AM - 6 PM)",
                "policy_document": {
                    "version": "1.0",
                    "rules": [
                        {
                            "effect": "deny",
                            "actions": ["*"],
                            "resources": ["*"],
                            "conditions": {
                                "time": {
                                    "hour_not_between": [9, 18]
                                }
                            }
                        }
                    ]
                },
                "effect": "deny",
                "priority": 500,
                "applies_to_roles": ["employee", "salesperson", "cashier"]
            },
            {
                "name": "financial_data_protection",
                "display_name": "Financial Data Protection",
                "description": "Strict access control for financial resources",
                "policy_document": {
                    "version": "1.0",
                    "rules": [
                        {
                            "effect": "deny",
                            "actions": ["read", "update", "delete"],
                            "resources": ["financial", "accounting", "payroll"],
                            "conditions": {
                                "user": {
                                    "roles_not_in": ["admin", "accountant", "finance_manager"]
                                }
                            }
                        }
                    ]
                },
                "effect": "deny",
                "priority": 800
            },
            {
                "name": "high_risk_actions_mfa",
                "display_name": "MFA Required for High-Risk Actions",
                "description": "Requires MFA for sensitive operations",
                "policy_document": {
                    "version": "1.0",
                    "rules": [
                        {
                            "effect": "allow",
                            "actions": ["delete", "approve", "export", "manage"],
                            "resources": ["*"],
                            "conditions": {
                                "mfa": {
                                    "required": True,
                                    "max_age_minutes": 5
                                }
                            }
                        }
                    ]
                },
                "effect": "allow",
                "priority": 900
            },
            {
                "name": "geolocation_restriction",
                "display_name": "Geographic Access Restriction",
                "description": "Restricts access based on geographic location",
                "policy_document": {
                    "version": "1.0",
                    "rules": [
                        {
                            "effect": "deny",
                            "actions": ["*"],
                            "resources": ["*"],
                            "conditions": {
                                "location": {
                                    "country_not_in": ["SA", "AE", "QA", "KW", "BH", "OM"]
                                }
                            }
                        }
                    ]
                },
                "effect": "deny",
                "priority": 700
            }
        ]
    
    @staticmethod
    def get_default_restriction_groups() -> List[Dict[str, Any]]:
        """Get default restriction groups"""
        return [
            {
                "name": "standard_employee_restrictions",
                "description": "Standard restrictions for regular employees",
                "restrictions": {
                    "time": {
                        "allowed_hours": list(range(7, 20)),  # 7 AM to 8 PM
                        "blocked_days": []  # No blocked days
                    },
                    "location": {
                        "allowed_countries": ["SA", "AE", "QA", "KW", "BH", "OM"]
                    },
                    "actions": {
                        "blocked_actions": ["delete", "export", "manage"]
                    },
                    "resources": {
                        "blocked_resources": ["system", "hr.salary", "financial.sensitive"]
                    }
                }
            },
            {
                "name": "high_privilege_restrictions",
                "description": "Restrictions for high-privilege users",
                "restrictions": {
                    "time": {
                        "require_mfa_outside_hours": [9, 18]
                    },
                    "location": {
                        "require_approval_new_location": True
                    },
                    "session": {
                        "max_concurrent_sessions": 2,
                        "session_timeout_minutes": 30
                    }
                }
            },
            {
                "name": "sensitive_data_restrictions",
                "description": "Additional restrictions for sensitive data access",
                "restrictions": {
                    "audit": {
                        "log_all_actions": True,
                        "require_justification": True
                    },
                    "approval": {
                        "require_manager_approval": True
                    },
                    "session": {
                        "no_concurrent_sessions": True,
                        "session_recording": True
                    }
                }
            }
        ]

# === RLS RULES ===

class RLSRules:
    """Row-Level Security rules"""
    
    @staticmethod
    def get_default_rules() -> List[Dict[str, Any]]:
        """Get default RLS rules"""
        return [
            {
                "name": "branch_isolation",
                "description": "Users can only access data from their assigned branch",
                "table_name": "sales_orders",
                "rule_expression": "branch_id = {branch_id}",
                "applies_to_actions": ["read", "update", "delete"],
                "applies_to_roles": [2, 3, 4, 5, 6, 7]  # Non-admin roles
            },
            {
                "name": "user_own_data",
                "description": "Users can only access their own personal data",
                "table_name": "user_profiles",
                "rule_expression": "user_id = {user_id}",
                "applies_to_actions": ["read", "update"],
                "applies_to_roles": [2, 3, 4, 5, 6, 7, 8]
            },
            {
                "name": "tenant_isolation",
                "description": "Multi-tenant data isolation",
                "table_name": "customers",
                "rule_expression": "tenant_id = {tenant_id}",
                "applies_to_actions": ["read", "update", "delete"],
                "applies_to_roles": [1, 2, 3, 4, 5, 6, 7, 8]
            },
            {
                "name": "active_records_only",
                "description": "Hide soft-deleted records from non-admin users",
                "table_name": "users",
                "rule_expression": "is_active = true OR deleted_at IS NULL",
                "applies_to_actions": ["read"],
                "applies_to_roles": [2, 3, 4, 5, 6, 7, 8]
            }
        ]

# === FLS RULES ===

class FLSRules:
    """Field-Level Security rules"""
    
    @staticmethod
    def get_default_rules() -> List[Dict[str, Any]]:
        """Get default FLS rules"""
        return [
            {
                "name": "hide_salary_from_non_hr",
                "description": "Hide salary information from non-HR users",
                "table_name": "employees",
                "column_name": "salary",
                "is_visible": False,
                "applies_to_roles": [2, 3, 4, 5, 6, 8]  # All except admin and HR
            },
            {
                "name": "mask_ssn_for_non_hr",
                "description": "Mask SSN for non-HR users",
                "table_name": "employees",
                "column_name": "ssn",
                "is_readable": True,
                "masking_pattern": "show_last_4",
                "applies_to_roles": [2, 3, 4, 5, 6, 8]
            },
            {
                "name": "readonly_financial_for_non_accountants",
                "description": "Make financial data read-only for non-accountants",
                "table_name": "financial_transactions",
                "column_name": "amount",
                "is_writable": False,
                "applies_to_roles": [2, 3, 4, 5, 7, 8]  # All except admin and accountant
            },
            {
                "name": "hide_customer_credit_card",
                "description": "Hide customer credit card information",
                "table_name": "customers",
                "column_name": "credit_card_number",
                "is_visible": True,
                "masking_pattern": "show_last_4",
                "requires_encryption": True,
                "applies_to_roles": [2, 3, 4, 5, 6, 7, 8]
            }
        ]

# === SECURITY SETTINGS BY ENVIRONMENT ===

class EnvironmentSettings:
    """Environment-specific security settings"""
    
    @staticmethod
    def get_production_settings() -> Dict[str, Any]:
        """Production security settings - maximum security"""
        return {
            "SESSION_TIMEOUT_MINUTES": 30,
            "MFA_REQUIRED_FOR_ADMINS": True,
            "PASSWORD_MIN_LENGTH": 14,
            "FAILED_LOGIN_THRESHOLD": 3,
            "RATE_LIMIT_REQUESTS_PER_MINUTE": 60,
            "AUDIT_LOG_ALL_ACTIONS": True,
            "GEOLOCATION_REQUIRED": True,
            "VPN_DETECTION_ENABLED": True,
            "TOR_BLOCKING_ENABLED": True,
            "ZERO_TRUST_MODE": True,
            "CONTINUOUS_AUTHENTICATION": True
        }
    
    @staticmethod
    def get_staging_settings() -> Dict[str, Any]:
        """Staging security settings - balanced security"""
        return {
            "SESSION_TIMEOUT_MINUTES": 60,
            "MFA_REQUIRED_FOR_ADMINS": True,
            "PASSWORD_MIN_LENGTH": 12,
            "FAILED_LOGIN_THRESHOLD": 5,
            "RATE_LIMIT_REQUESTS_PER_MINUTE": 100,
            "AUDIT_LOG_ALL_ACTIONS": True,
            "GEOLOCATION_REQUIRED": False,
            "VPN_DETECTION_ENABLED": False,
            "TOR_BLOCKING_ENABLED": False
        }
    
    @staticmethod
    def get_development_settings() -> Dict[str, Any]:
        """Development security settings - relaxed for development"""
        return {
            "SESSION_TIMEOUT_MINUTES": 480,  # 8 hours
            "MFA_REQUIRED_FOR_ADMINS": False,
            "PASSWORD_MIN_LENGTH": 8,
            "FAILED_LOGIN_THRESHOLD": 10,
            "RATE_LIMIT_REQUESTS_PER_MINUTE": 1000,
            "AUDIT_LOG_ALL_ACTIONS": False,
            "GEOLOCATION_REQUIRED": False,
            "VPN_DETECTION_ENABLED": False,
            "TOR_BLOCKING_ENABLED": False
        }

# === SECURITY VALIDATORS ===

class SecurityValidators:
    """Security validation functions"""
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """Validate password against security policy"""
        errors = []
        
        if len(password) < security_config.PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {security_config.PASSWORD_MIN_LENGTH} characters long")
        
        if security_config.PASSWORD_REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if security_config.PASSWORD_REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if security_config.PASSWORD_REQUIRE_NUMBERS and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if security_config.PASSWORD_REQUIRE_SYMBOLS and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one special character")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "strength": "strong" if len(errors) == 0 else "weak"
        }
    
    @staticmethod
    def validate_session_risk(session_data: Dict[str, Any]) -> float:
        """Calculate session risk score"""
        risk_score = 0.0
        
        # Add risk factors
        for factor, weight in security_config.RISK_FACTORS.items():
            if session_data.get(factor, False):
                risk_score += weight
        
        return min(1.0, risk_score)  # Cap at 1.0
    
    @staticmethod
    def get_required_mfa_factors(risk_score: float, user_role: str) -> List[str]:
        """Get required MFA factors based on risk and role"""
        factors = []
        
        # Always require password
        factors.append("password")
        
        # Admin users always need MFA
        if user_role == "admin" or security_config.MFA_REQUIRED_FOR_ADMINS:
            factors.append("totp")
        
        # High risk requires additional factors
        if risk_score >= security_config.RISK_SCORE_THRESHOLDS["high"]:
            factors.extend(["totp", "push_notification"])
        
        # Critical risk requires all factors
        if risk_score >= security_config.RISK_SCORE_THRESHOLDS["critical"]:
            factors.extend(["sms", "biometric"])
        
        return list(set(factors))  # Remove duplicates
