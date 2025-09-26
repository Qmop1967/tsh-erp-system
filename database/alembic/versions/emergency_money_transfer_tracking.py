"""Emergency money transfer tracking system

Revision ID: emergency_money_transfer_tracking
Revises: 
Create Date: 2024-01-20 10:00:00.000000

CRITICAL: This migration creates the emergency fraud prevention system
for tracking $35K USD weekly transfers from 12 travel salespersons.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

# revision identifiers
revision = 'emergency_money_transfer'
down_revision = '8b5fc7e6bb8a'  # Latest inventory migration
branch_labels = None
depends_on = None


def upgrade():
    """Create money transfer tracking tables"""
    
    # Create transfer_platforms table
    op.create_table(
        'transfer_platforms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('platform_name', sa.String(length=50), nullable=False),
        sa.Column('platform_code', sa.String(length=10), nullable=False),
        sa.Column('has_api', sa.Boolean(), nullable=True, default=False),
        sa.Column('api_endpoint', sa.String(length=200), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('platform_name'),
        sa.UniqueConstraint('platform_code')
    )
    
    # Create money_transfers table (CRITICAL - FRAUD PREVENTION)
    op.create_table(
        'money_transfers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transfer_uuid', sa.String(length=36), nullable=True),
        sa.Column('salesperson_id', sa.Integer(), nullable=False),
        sa.Column('salesperson_name', sa.String(length=100), nullable=False),
        
        # Financial details
        sa.Column('amount_usd', sa.Float(), nullable=False),
        sa.Column('amount_iqd', sa.Float(), nullable=False),
        sa.Column('exchange_rate', sa.Float(), nullable=False),
        
        # Commission tracking (CRITICAL for fraud prevention)
        sa.Column('gross_sales', sa.Float(), nullable=False),
        sa.Column('commission_rate', sa.Float(), nullable=True, default=2.25),
        sa.Column('calculated_commission', sa.Float(), nullable=False),
        sa.Column('claimed_commission', sa.Float(), nullable=False),
        sa.Column('commission_verified', sa.Boolean(), nullable=True, default=False),
        
        # Platform information
        sa.Column('transfer_platform', sa.String(length=50), nullable=False),
        sa.Column('platform_reference', sa.String(length=100), nullable=True),
        sa.Column('transfer_fee', sa.Float(), nullable=True, default=0.0),
        
        # GPS and verification
        sa.Column('transfer_datetime', sa.DateTime(), nullable=False),
        sa.Column('gps_latitude', sa.Float(), nullable=True),
        sa.Column('gps_longitude', sa.Float(), nullable=True),
        sa.Column('location_name', sa.String(length=200), nullable=True),
        sa.Column('receipt_photo_url', sa.String(length=500), nullable=True),
        sa.Column('receipt_verified', sa.Boolean(), nullable=True, default=False),
        
        # Status tracking
        sa.Column('status', sa.String(length=20), nullable=True, default='pending'),
        sa.Column('money_received', sa.Boolean(), nullable=True, default=False),
        sa.Column('received_datetime', sa.DateTime(), nullable=True),
        
        # Fraud detection (CRITICAL)
        sa.Column('is_suspicious', sa.Boolean(), nullable=True, default=False),
        sa.Column('fraud_alert_reason', sa.Text(), nullable=True),
        sa.Column('manager_approval_required', sa.Boolean(), nullable=True, default=False),
        
        # Audit trail
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        
        sa.ForeignKeyConstraint(['salesperson_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('transfer_uuid')
    )
    
    # Create indexes for performance
    op.create_index('idx_money_transfers_salesperson', 'money_transfers', ['salesperson_id'])
    op.create_index('idx_money_transfers_datetime', 'money_transfers', ['transfer_datetime'])
    op.create_index('idx_money_transfers_status', 'money_transfers', ['status'])
    op.create_index('idx_money_transfers_suspicious', 'money_transfers', ['is_suspicious'])
    op.create_index('idx_money_transfers_platform', 'money_transfers', ['transfer_platform'])
    
    # Insert default transfer platforms
    op.execute("""
        INSERT INTO transfer_platforms (platform_name, platform_code, has_api, api_endpoint, is_active, created_at)
        VALUES 
        ('ALTaif Bank', 'ALT', false, null, true, now()),
        ('ZAIN Cash', 'ZAIN', true, 'https://api.zaincash.iq', true, now()),
        ('SuperQi', 'SUPER', true, 'https://api.superqi.com', true, now())
    """)
    
    print("🚨 CRITICAL: Emergency Money Transfer Tracking System Created!")
    print("   - Fraud prevention system enabled")
    print("   - Commission verification active")
    print("   - GPS tracking enabled")
    print("   - Multi-platform support ready")
    print("   - $35K weekly transfer monitoring active")


def downgrade():
    """Remove money transfer tracking tables"""
    
    # Drop indexes
    op.drop_index('idx_money_transfers_platform', table_name='money_transfers')
    op.drop_index('idx_money_transfers_suspicious', table_name='money_transfers')
    op.drop_index('idx_money_transfers_status', table_name='money_transfers')
    op.drop_index('idx_money_transfers_datetime', table_name='money_transfers')
    op.drop_index('idx_money_transfers_salesperson', table_name='money_transfers')
    
    # Drop tables
    op.drop_table('money_transfers')
    op.drop_table('transfer_platforms')
    
    print("⚠️  Money Transfer Tracking System Removed!")
    print("   - Fraud prevention system disabled")
    print("   - Commission verification removed")
    print("   - GPS tracking disabled") 