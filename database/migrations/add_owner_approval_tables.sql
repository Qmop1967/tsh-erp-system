-- Migration: Add Owner Approval Tables
-- Date: 2025-01-15
-- Description: Creates tables for Owner Approval system in TSH Security Console

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types for approval system
DO $$
BEGIN
    -- ApprovalMethod enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'approvalmethod') THEN
        CREATE TYPE approvalmethod AS ENUM (
            'push', 'qr', 'sms', 'manual', 'biometric'
        );
    END IF;

    -- ApprovalStatus enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'approvalstatus') THEN
        CREATE TYPE approvalstatus AS ENUM (
            'pending', 'approved', 'denied', 'expired', 'cancelled'
        );
    END IF;

    -- ApprovalType enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'approvaltype') THEN
        CREATE TYPE approvaltype AS ENUM (
            'login_suspicious', 'high_value_transaction', 'sensitive_data_access',
            'user_role_change', 'system_config_change', 'bulk_operation',
            'device_trust', 'emergency_access', 'financial_report', 'data_export'
        );
    END IF;

    -- RiskLevel enum (if not already exists from advanced_security)
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'owner_risk_level') THEN
        CREATE TYPE owner_risk_level AS ENUM (
            'low', 'medium', 'high', 'critical'
        );
    END IF;
END $$;

-- Owner Approvals Table
CREATE TABLE IF NOT EXISTS owner_approvals (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::varchar,

    -- Request information
    requester_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    approval_type approvaltype NOT NULL,
    risk_level owner_risk_level DEFAULT 'medium',

    -- Approval credentials
    approval_code VARCHAR(6) NOT NULL,
    qr_payload TEXT,
    method approvalmethod DEFAULT 'push',

    -- Status tracking
    status approvalstatus DEFAULT 'pending',

    -- Application context
    app_id VARCHAR(100),
    request_description TEXT,
    request_description_ar TEXT,

    -- Device information (requester)
    device_info JSONB,
    device_fingerprint VARCHAR(255),
    user_agent VARCHAR(500),

    -- Location information (requester)
    ip_address VARCHAR(45),
    geolocation JSONB,

    -- Timing
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    resolved_at TIMESTAMP WITH TIME ZONE,

    -- Resolution details
    resolved_by INTEGER REFERENCES users(id),
    resolution_reason TEXT,
    resolution_reason_ar TEXT,

    -- Owner device info (when approved/denied)
    owner_device_info JSONB,
    owner_ip_address VARCHAR(45),
    owner_geolocation JSONB,

    -- Additional metadata
    metadata JSONB,
    notification_sent BOOLEAN DEFAULT FALSE,
    notification_sent_at TIMESTAMP WITH TIME ZONE,
    reminder_count INTEGER DEFAULT 0
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_owner_approvals_status ON owner_approvals(status);
CREATE INDEX IF NOT EXISTS idx_owner_approvals_code ON owner_approvals(approval_code);
CREATE INDEX IF NOT EXISTS idx_owner_approvals_requester ON owner_approvals(requester_id);
CREATE INDEX IF NOT EXISTS idx_owner_approvals_created ON owner_approvals(created_at);
CREATE INDEX IF NOT EXISTS idx_owner_approvals_expires ON owner_approvals(expires_at);
CREATE INDEX IF NOT EXISTS idx_owner_approvals_risk ON owner_approvals(risk_level);
CREATE INDEX IF NOT EXISTS idx_owner_approvals_type ON owner_approvals(approval_type);

-- Approval Audit Log Table
CREATE TABLE IF NOT EXISTS approval_audit_logs (
    id SERIAL PRIMARY KEY,
    approval_id VARCHAR(36) NOT NULL REFERENCES owner_approvals(id) ON DELETE CASCADE,

    -- Action details
    action VARCHAR(100) NOT NULL,
    actor_id INTEGER REFERENCES users(id),

    -- Context
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    device_info JSONB,
    geolocation JSONB,

    -- Details
    old_status approvalstatus,
    new_status approvalstatus,
    notes TEXT,

    -- Timestamp
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for audit log
CREATE INDEX IF NOT EXISTS idx_approval_audit_approval ON approval_audit_logs(approval_id);
CREATE INDEX IF NOT EXISTS idx_approval_audit_action ON approval_audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_approval_audit_timestamp ON approval_audit_logs(timestamp);

-- Owner Security Settings Table
CREATE TABLE IF NOT EXISTS owner_security_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,

    -- Approval settings
    require_biometric BOOLEAN DEFAULT TRUE,
    auto_approve_low_risk BOOLEAN DEFAULT FALSE,
    default_expiration_minutes INTEGER DEFAULT 10,
    max_pending_approvals INTEGER DEFAULT 10,

    -- Notification preferences
    enable_push_notifications BOOLEAN DEFAULT TRUE,
    enable_sms_notifications BOOLEAN DEFAULT FALSE,
    enable_email_notifications BOOLEAN DEFAULT TRUE,
    quiet_hours_start VARCHAR(5),
    quiet_hours_end VARCHAR(5),
    emergency_override_quiet_hours BOOLEAN DEFAULT TRUE,

    -- Security restrictions
    allowed_approval_ips JSONB,
    require_geofence BOOLEAN DEFAULT FALSE,
    allowed_locations JSONB,

    -- Session settings
    session_timeout_minutes INTEGER DEFAULT 30,
    max_concurrent_sessions INTEGER DEFAULT 2,

    -- Audit settings
    log_all_views BOOLEAN DEFAULT TRUE,
    retain_audit_days INTEGER DEFAULT 365,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for security settings
CREATE INDEX IF NOT EXISTS idx_owner_settings_user ON owner_security_settings(user_id);

-- Comments for documentation
COMMENT ON TABLE owner_approvals IS 'Stores approval requests requiring Owner/Director authorization';
COMMENT ON TABLE approval_audit_logs IS 'Complete audit trail for all approval-related actions';
COMMENT ON TABLE owner_security_settings IS 'Security settings specific to Owner/Director role';

COMMENT ON COLUMN owner_approvals.approval_code IS '6-digit code for manual approval verification';
COMMENT ON COLUMN owner_approvals.qr_payload IS 'Signed JWT payload for QR code scanning';
COMMENT ON COLUMN owner_approvals.risk_level IS 'Risk assessment: low, medium, high, critical';
COMMENT ON COLUMN owner_approvals.geolocation IS 'JSON containing lat, lng, accuracy, address';

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON owner_approvals TO tsh_app_user;
-- GRANT SELECT, INSERT ON approval_audit_logs TO tsh_app_user;
-- GRANT SELECT, INSERT, UPDATE ON owner_security_settings TO tsh_app_user;
-- GRANT USAGE, SELECT ON SEQUENCE approval_audit_logs_id_seq TO tsh_app_user;
-- GRANT USAGE, SELECT ON SEQUENCE owner_security_settings_id_seq TO tsh_app_user;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Owner Approval tables created successfully!';
    RAISE NOTICE 'Tables created: owner_approvals, approval_audit_logs, owner_security_settings';
    RAISE NOTICE 'Indexes created for optimal query performance';
END $$;
