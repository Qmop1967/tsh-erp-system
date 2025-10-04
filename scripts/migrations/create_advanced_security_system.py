"""
Database Migration: Advanced Security System
Creates all tables for hyper-advanced ABAC, RBAC, PBAC, RLS, FLS system

Run this migration to add advanced security features to your TSH ERP database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config.settings import get_database_url
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_advanced_security_tables():
    """Create all advanced security tables"""
    
    engine = create_engine(get_database_url())
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        logger.info("🔐 Creating Advanced Security System Tables...")
        
        # 1. Enhanced Permissions Table
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS advanced_permissions (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) UNIQUE NOT NULL,
                display_name VARCHAR(300),
                description TEXT,
                resource_type VARCHAR(50) NOT NULL,
                action VARCHAR(50) NOT NULL,
                security_level VARCHAR(20) DEFAULT 'internal',
                conditions JSONB,
                constraints JSONB,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER REFERENCES users(id)
            );
            CREATE INDEX IF NOT EXISTS idx_advanced_permissions_name ON advanced_permissions(name);
            CREATE INDEX IF NOT EXISTS idx_advanced_permissions_resource ON advanced_permissions(resource_type);
            CREATE INDEX IF NOT EXISTS idx_advanced_permissions_action ON advanced_permissions(action);
        """))
        
        # 2. Enhanced Roles Table
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS security_roles (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                display_name VARCHAR(200),
                description TEXT,
                parent_role_id INTEGER REFERENCES security_roles(id),
                level INTEGER DEFAULT 0,
                attributes JSONB,
                security_level VARCHAR(20) DEFAULT 'internal',
                max_users INTEGER,
                requires_approval BOOLEAN DEFAULT false,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_security_roles_name ON security_roles(name);
            CREATE INDEX IF NOT EXISTS idx_security_roles_parent ON security_roles(parent_role_id);
        """))
        
        # 3. Role Permission Mappings
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS role_permission_mappings (
                id SERIAL PRIMARY KEY,
                role_id INTEGER NOT NULL REFERENCES security_roles(id) ON DELETE CASCADE,
                permission_id INTEGER NOT NULL REFERENCES advanced_permissions(id) ON DELETE CASCADE,
                conditions JSONB,
                constraints JSONB,
                expires_at TIMESTAMP,
                granted_by INTEGER REFERENCES users(id),
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(role_id, permission_id)
            );
            CREATE INDEX IF NOT EXISTS idx_role_permission_role ON role_permission_mappings(role_id);
            CREATE INDEX IF NOT EXISTS idx_role_permission_permission ON role_permission_mappings(permission_id);
        """))
        
        # 4. User Permission Overrides
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS user_permission_overrides (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                permission_id INTEGER NOT NULL REFERENCES advanced_permissions(id) ON DELETE CASCADE,
                is_granted BOOLEAN DEFAULT true,
                override_reason TEXT,
                conditions JSONB,
                constraints JSONB,
                expires_at TIMESTAMP,
                requires_approval BOOLEAN DEFAULT false,
                approved_by INTEGER REFERENCES users(id),
                approved_at TIMESTAMP,
                granted_by INTEGER REFERENCES users(id),
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_user_permission_user ON user_permission_overrides(user_id);
            CREATE INDEX IF NOT EXISTS idx_user_permission_permission ON user_permission_overrides(permission_id);
        """))
        
        # 5. Security Policies (PBAC)
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS security_policies (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) UNIQUE NOT NULL,
                display_name VARCHAR(300),
                description TEXT,
                policy_document JSONB NOT NULL,
                effect VARCHAR(10) DEFAULT 'allow',
                priority INTEGER DEFAULT 100,
                applies_to_resources JSONB,
                applies_to_actions JSONB,
                applies_to_subjects JSONB,
                conditions JSONB,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER REFERENCES users(id)
            );
            CREATE INDEX IF NOT EXISTS idx_security_policies_name ON security_policies(name);
            CREATE INDEX IF NOT EXISTS idx_security_policies_priority ON security_policies(priority DESC);
        """))
        
        # 6. Policy Permission Mappings
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS policy_permission_mappings (
                id SERIAL PRIMARY KEY,
                policy_id INTEGER NOT NULL REFERENCES security_policies(id) ON DELETE CASCADE,
                permission_id INTEGER NOT NULL REFERENCES advanced_permissions(id) ON DELETE CASCADE,
                effect VARCHAR(10) DEFAULT 'allow',
                conditions JSONB
            );
            CREATE INDEX IF NOT EXISTS idx_policy_permission_policy ON policy_permission_mappings(policy_id);
            CREATE INDEX IF NOT EXISTS idx_policy_permission_permission ON policy_permission_mappings(permission_id);
        """))
        
        # 7. Row-Level Security Rules (RLS)
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS rls_rules (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) UNIQUE NOT NULL,
                description TEXT,
                table_name VARCHAR(100) NOT NULL,
                rule_expression TEXT NOT NULL,
                applies_to_actions JSONB,
                applies_to_roles JSONB,
                applies_to_users JSONB,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER REFERENCES users(id)
            );
            CREATE INDEX IF NOT EXISTS idx_rls_rules_table ON rls_rules(table_name);
        """))
        
        # 8. Field-Level Security Rules (FLS)
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS fls_rules (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) UNIQUE NOT NULL,
                description TEXT,
                table_name VARCHAR(100) NOT NULL,
                column_name VARCHAR(100) NOT NULL,
                is_readable BOOLEAN DEFAULT true,
                is_writable BOOLEAN DEFAULT true,
                is_visible BOOLEAN DEFAULT true,
                masking_pattern VARCHAR(100),
                requires_encryption BOOLEAN DEFAULT false,
                applies_to_roles JSONB,
                applies_to_users JSONB,
                conditions JSONB,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER REFERENCES users(id)
            );
            CREATE INDEX IF NOT EXISTS idx_fls_rules_table_column ON fls_rules(table_name, column_name);
        """))
        
        # 9. Restriction Groups
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS restriction_groups (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) UNIQUE NOT NULL,
                description TEXT,
                restrictions JSONB NOT NULL,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER REFERENCES users(id)
            );
            CREATE INDEX IF NOT EXISTS idx_restriction_groups_name ON restriction_groups(name);
        """))
        
        # 10. Role Restriction Groups
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS role_restriction_groups (
                id SERIAL PRIMARY KEY,
                role_id INTEGER NOT NULL REFERENCES security_roles(id) ON DELETE CASCADE,
                restriction_group_id INTEGER NOT NULL REFERENCES restriction_groups(id) ON DELETE CASCADE,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                applied_by INTEGER REFERENCES users(id)
            );
            CREATE INDEX IF NOT EXISTS idx_role_restriction_role ON role_restriction_groups(role_id);
        """))
        
        # 11. User Restriction Groups
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS user_restriction_groups (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                restriction_group_id INTEGER NOT NULL REFERENCES restriction_groups(id) ON DELETE CASCADE,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                applied_by INTEGER REFERENCES users(id),
                expires_at TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_user_restriction_user ON user_restriction_groups(user_id);
        """))
        
        # 12. MFA Methods
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS mfa_methods (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                factor_type VARCHAR(30) NOT NULL,
                is_primary BOOLEAN DEFAULT false,
                is_enabled BOOLEAN DEFAULT true,
                secret_key TEXT,
                phone_number VARCHAR(20),
                email_address VARCHAR(255),
                device_id VARCHAR(255),
                backup_codes JSONB,
                backup_codes_used JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                use_count INTEGER DEFAULT 0
            );
            CREATE INDEX IF NOT EXISTS idx_mfa_methods_user ON mfa_methods(user_id);
            CREATE INDEX IF NOT EXISTS idx_mfa_methods_type ON mfa_methods(factor_type);
        """))
        
        # 13. MFA Challenges
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS mfa_challenges (
                id VARCHAR(36) PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                mfa_method_id INTEGER NOT NULL REFERENCES mfa_methods(id) ON DELETE CASCADE,
                challenge_code VARCHAR(10),
                challenge_data JSONB,
                is_verified BOOLEAN DEFAULT false,
                attempts INTEGER DEFAULT 0,
                max_attempts INTEGER DEFAULT 3,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '5 minutes'),
                verified_at TIMESTAMP,
                ip_address INET,
                user_agent TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_mfa_challenges_user ON mfa_challenges(user_id);
            CREATE INDEX IF NOT EXISTS idx_mfa_challenges_expires ON mfa_challenges(expires_at);
        """))
        
        # 14. User Devices
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS user_devices (
                id VARCHAR(36) PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                device_name VARCHAR(200),
                device_type VARCHAR(50),
                platform VARCHAR(50),
                browser VARCHAR(100),
                device_fingerprint VARCHAR(255) UNIQUE,
                device_token TEXT,
                status VARCHAR(20) DEFAULT 'pending',
                is_trusted BOOLEAN DEFAULT false,
                last_ip_address INET,
                last_location JSONB,
                allowed_locations JSONB,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                registered_at TIMESTAMP,
                approved_by INTEGER REFERENCES users(id)
            );
            CREATE INDEX IF NOT EXISTS idx_user_devices_user ON user_devices(user_id);
            CREATE INDEX IF NOT EXISTS idx_user_devices_fingerprint ON user_devices(device_fingerprint);
            CREATE INDEX IF NOT EXISTS idx_user_devices_status ON user_devices(status);
        """))
        
        # 15. User Sessions
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id VARCHAR(36) PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                device_id VARCHAR(36) REFERENCES user_devices(id),
                session_token VARCHAR(500) UNIQUE NOT NULL,
                refresh_token VARCHAR(500) UNIQUE,
                status VARCHAR(20) DEFAULT 'active',
                is_mobile BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                terminated_at TIMESTAMP,
                ip_address INET,
                location JSONB,
                user_agent TEXT,
                risk_score FLOAT DEFAULT 0.0,
                risk_level VARCHAR(20) DEFAULT 'low',
                can_be_terminated BOOLEAN DEFAULT true,
                requires_mfa BOOLEAN DEFAULT false
            );
            CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON user_sessions(user_id);
            CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
            CREATE INDEX IF NOT EXISTS idx_user_sessions_status ON user_sessions(status);
            CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at);
        """))
        
        # 16. Session Activities
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS session_activities (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(36) NOT NULL REFERENCES user_sessions(id) ON DELETE CASCADE,
                activity_type VARCHAR(100),
                activity_description TEXT,
                resource_accessed VARCHAR(200),
                ip_address INET,
                location JSONB,
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_session_activities_session ON session_activities(session_id);
            CREATE INDEX IF NOT EXISTS idx_session_activities_type ON session_activities(activity_type);
            CREATE INDEX IF NOT EXISTS idx_session_activities_timestamp ON session_activities(timestamp DESC);
        """))
        
        # 17. Enhanced Audit Logs
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                session_id VARCHAR(36) REFERENCES user_sessions(id),
                action VARCHAR(100) NOT NULL,
                resource_type VARCHAR(50) NOT NULL,
                resource_id VARCHAR(100),
                description TEXT,
                old_values JSONB,
                new_values JSONB,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address INET,
                location JSONB,
                user_agent TEXT,
                method VARCHAR(20),
                endpoint VARCHAR(200),
                branch_id INTEGER REFERENCES branches(id),
                tenant_id INTEGER,
                risk_score FLOAT DEFAULT 0.0,
                is_suspicious BOOLEAN DEFAULT false
            );
            CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
            CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
            CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource_type);
            CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_audit_logs_ip ON audit_logs(ip_address);
            CREATE INDEX IF NOT EXISTS idx_audit_logs_suspicious ON audit_logs(is_suspicious);
        """))
        
        # 18. Security Events
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS security_events (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR(100) NOT NULL,
                severity VARCHAR(20) DEFAULT 'low',
                title VARCHAR(200),
                description TEXT,
                user_id INTEGER REFERENCES users(id),
                session_id VARCHAR(36) REFERENCES user_sessions(id),
                ip_address INET,
                location JSONB,
                event_data JSONB,
                is_resolved BOOLEAN DEFAULT false,
                resolved_by INTEGER REFERENCES users(id),
                resolved_at TIMESTAMP,
                resolution_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_security_events_type ON security_events(event_type);
            CREATE INDEX IF NOT EXISTS idx_security_events_severity ON security_events(severity);
            CREATE INDEX IF NOT EXISTS idx_security_events_user ON security_events(user_id);
            CREATE INDEX IF NOT EXISTS idx_security_events_created ON security_events(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_security_events_resolved ON security_events(is_resolved);
        """))
        
        # 19. Passless Tokens
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS passless_tokens (
                id VARCHAR(36) PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                device_id VARCHAR(36) REFERENCES user_devices(id),
                token_type VARCHAR(50),
                token_hash VARCHAR(255) UNIQUE,
                is_used BOOLEAN DEFAULT false,
                attempts INTEGER DEFAULT 0,
                max_attempts INTEGER DEFAULT 3,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '10 minutes'),
                used_at TIMESTAMP,
                ip_address INET,
                user_agent TEXT,
                location JSONB
            );
            CREATE INDEX IF NOT EXISTS idx_passless_tokens_user ON passless_tokens(user_id);
            CREATE INDEX IF NOT EXISTS idx_passless_tokens_hash ON passless_tokens(token_hash);
            CREATE INDEX IF NOT EXISTS idx_passless_tokens_expires ON passless_tokens(expires_at);
        """))
        
        session.commit()
        logger.info("✅ Advanced Security System tables created successfully!")
        
        # Create some default data
        create_default_security_data(session)
        
    except Exception as e:
        logger.error(f"❌ Error creating advanced security tables: {e}")
        session.rollback()
        raise
    finally:
        session.close()

def create_default_security_data(session):
    """Create default security policies and restrictions"""
    
    logger.info("🔧 Creating default security data...")
    
    try:
        # 1. Default Security Policy - Admin Full Access
        session.execute(text("""
            INSERT INTO security_policies (name, display_name, description, policy_document, effect, priority)
            VALUES (
                'admin_full_access',
                'Administrator Full Access',
                'Grants full system access to administrators',
                '{"rules": [{"effect": "allow", "actions": ["*"], "resources": ["*"]}]}',
                'allow',
                1000
            ) ON CONFLICT (name) DO NOTHING;
        """))
        
        # 2. Default Restriction Group - Time-based Access
        session.execute(text("""
            INSERT INTO restriction_groups (name, description, restrictions)
            VALUES (
                'business_hours_only',
                'Restrict access to business hours only',
                '{"time": {"allowed_hours": [9, 10, 11, 12, 13, 14, 15, 16, 17]}}'
            ) ON CONFLICT (name) DO NOTHING;
        """))
        
        # 3. Default Restriction Group - Location-based Access
        session.execute(text("""
            INSERT INTO restriction_groups (name, description, restrictions)
            VALUES (
                'office_locations_only',
                'Restrict access to office locations only',
                '{"location": {"allowed_countries": ["SA", "AE", "QA"]}, "ip": {"allowed_networks": ["192.168.0.0/16", "10.0.0.0/8"]}}'
            ) ON CONFLICT (name) DO NOTHING;
        """))
        
        # 4. Default RLS Rule - Branch Isolation
        session.execute(text("""
            INSERT INTO rls_rules (name, description, table_name, rule_expression, applies_to_actions)
            VALUES (
                'branch_isolation',
                'Users can only access data from their assigned branch',
                'sales_orders',
                'branch_id = {branch_id}',
                '["read", "update", "delete"]'
            ) ON CONFLICT (name) DO NOTHING;
        """))
        
        # 5. Default FLS Rule - Sensitive Financial Data
        session.execute(text("""
            INSERT INTO fls_rules (name, description, table_name, column_name, is_readable, is_writable, masking_pattern, applies_to_roles)
            VALUES (
                'mask_salary_data',
                'Mask salary information for non-HR users',
                'employees',
                'salary',
                true,
                false,
                'show_last_2',
                '[2, 3, 4, 5, 6, 7]'
            ) ON CONFLICT (name) DO NOTHING;
        """))
        
        session.commit()
        logger.info("✅ Default security data created successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error creating default security data: {e}")
        session.rollback()
        raise

if __name__ == "__main__":
    print("🚀 TSH ERP Advanced Security System Migration")
    print("=" * 50)
    
    try:
        create_advanced_security_tables()
        print("\n🎉 Migration completed successfully!")
        print("\nAdvanced Security Features Available:")
        print("✅ Attribute-Based Access Control (ABAC)")
        print("✅ Role-Based Access Control (RBAC)")
        print("✅ Policy-Based Access Control (PBAC)")
        print("✅ Row-Level Security (RLS)")
        print("✅ Field-Level Security (FLS)")
        print("✅ Multi-Factor Authentication (MFA)")
        print("✅ Device Management")
        print("✅ Session Control")
        print("✅ Centralized Audit Logging")
        print("✅ Security Event Monitoring")
        print("✅ Passless Authentication")
        print("✅ Risk-Based Access Control")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)
