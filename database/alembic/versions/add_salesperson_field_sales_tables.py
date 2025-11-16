"""Add salesperson GPS tracking, commission, and target tables for field sales app

Revision ID: add_salesperson_field_sales
Revises: f7145b8f57e0
Create Date: 2025-11-15 22:00:00.000000

This migration creates the complete backend infrastructure for App 06 - TSH Field Sales Rep:
- GPS tracking for 12 travel salespersons
- Commission management (2.25% automatic calculation)
- Sales targets and leaderboards
- Daily performance summaries

Business Context:
- $35,000 USD weekly cash flow from travel sales
- Real-time route monitoring and fraud prevention
- Automated commission calculations
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import NUMERIC
from datetime import datetime

# revision identifiers
revision = 'add_salesperson_field_sales'
down_revision = 'f7145b8f57e0'  # Latest migration
branch_labels = None
depends_on = None


def upgrade():
    """Create salesperson feature tables"""

    # ========================================================================
    # GPS Location Tracking Table
    # ========================================================================
    op.create_table(
        'salesperson_gps_locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('location_uuid', sa.String(length=36), nullable=True),

        # Salesperson tracking
        sa.Column('salesperson_id', sa.Integer(), nullable=False),

        # GPS coordinates (8 decimal places = ~1mm accuracy)
        sa.Column('latitude', NUMERIC(10, 8), nullable=False),
        sa.Column('longitude', NUMERIC(11, 8), nullable=False),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('altitude', sa.Float(), nullable=True),
        sa.Column('speed', sa.Float(), nullable=True),
        sa.Column('heading', sa.Float(), nullable=True),

        # Timing
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=True, default=datetime.utcnow),

        # Activity context
        sa.Column('activity_type', sa.String(length=50), nullable=True),
        sa.Column('is_customer_visit', sa.Boolean(), nullable=True, default=False),
        sa.Column('customer_id', sa.Integer(), nullable=True),
        sa.Column('visit_verified', sa.Boolean(), nullable=True, default=False),
        sa.Column('distance_from_customer', sa.Float(), nullable=True),

        # Battery and device info
        sa.Column('battery_level', sa.Integer(), nullable=True),
        sa.Column('is_charging', sa.Boolean(), nullable=True),
        sa.Column('device_id', sa.String(length=100), nullable=True),

        # Sync status
        sa.Column('is_synced', sa.Boolean(), nullable=True, default=False),
        sa.Column('synced_at', sa.DateTime(), nullable=True),

        # Audit
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['salesperson_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.UniqueConstraint('location_uuid')
    )

    # Indexes for performance
    op.create_index('idx_gps_salesperson', 'salesperson_gps_locations', ['salesperson_id'])
    op.create_index('idx_gps_timestamp', 'salesperson_gps_locations', ['timestamp'])
    op.create_index('idx_gps_customer_visit', 'salesperson_gps_locations', ['is_customer_visit'])
    op.create_index('idx_gps_sync_status', 'salesperson_gps_locations', ['is_synced'])
    op.create_index('idx_gps_created_at', 'salesperson_gps_locations', ['created_at'])
    op.create_index('idx_gps_location_uuid', 'salesperson_gps_locations', ['location_uuid'])

    # ========================================================================
    # Commission Tracking Table
    # ========================================================================
    op.create_table(
        'salesperson_commissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('commission_uuid', sa.String(length=36), nullable=True),

        # Salesperson
        sa.Column('salesperson_id', sa.Integer(), nullable=False),
        sa.Column('salesperson_name', sa.String(length=100), nullable=False),

        # Period tracking
        sa.Column('period_type', sa.String(length=20), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),

        # Financial calculations
        sa.Column('total_sales_amount', NUMERIC(12, 2), nullable=False, default=0),
        sa.Column('commission_rate', NUMERIC(5, 2), nullable=True, default=2.25),
        sa.Column('calculated_commission', NUMERIC(12, 2), nullable=False, default=0),
        sa.Column('approved_commission', NUMERIC(12, 2), nullable=True),

        # Order details
        sa.Column('total_orders', sa.Integer(), nullable=True, default=0),
        sa.Column('total_customers', sa.Integer(), nullable=True, default=0),
        sa.Column('avg_order_value', NUMERIC(12, 2), nullable=True, default=0),

        # Status and workflow
        sa.Column('status', sa.String(length=20), nullable=True, default='pending'),
        sa.Column('is_paid', sa.Boolean(), nullable=True, default=False),
        sa.Column('paid_date', sa.Date(), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('payment_reference', sa.String(length=100), nullable=True),

        # Integration with money transfers
        sa.Column('transfer_id', sa.Integer(), nullable=True),

        # Approval workflow
        sa.Column('calculated_by', sa.Integer(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(), nullable=True),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('paid_by', sa.Integer(), nullable=True),
        sa.Column('paid_at', sa.DateTime(), nullable=True),

        # Notes
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('manager_notes', sa.Text(), nullable=True),

        # Sync status
        sa.Column('is_synced', sa.Boolean(), nullable=True, default=False),
        sa.Column('synced_at', sa.DateTime(), nullable=True),

        # Audit
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['salesperson_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['transfer_id'], ['money_transfers.id'], ),
        sa.ForeignKeyConstraint(['calculated_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['paid_by'], ['users.id'], ),
        sa.UniqueConstraint('commission_uuid')
    )

    # Indexes
    op.create_index('idx_commission_salesperson', 'salesperson_commissions', ['salesperson_id'])
    op.create_index('idx_commission_period_start', 'salesperson_commissions', ['period_start'])
    op.create_index('idx_commission_period_end', 'salesperson_commissions', ['period_end'])
    op.create_index('idx_commission_status', 'salesperson_commissions', ['status'])
    op.create_index('idx_commission_paid', 'salesperson_commissions', ['is_paid'])
    op.create_index('idx_commission_created_at', 'salesperson_commissions', ['created_at'])

    # ========================================================================
    # Sales Targets Table
    # ========================================================================
    op.create_table(
        'salesperson_targets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('target_uuid', sa.String(length=36), nullable=True),

        # Salesperson
        sa.Column('salesperson_id', sa.Integer(), nullable=False),
        sa.Column('salesperson_name', sa.String(length=100), nullable=False),

        # Target period
        sa.Column('period_type', sa.String(length=20), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),

        # Target metrics
        sa.Column('target_revenue_iqd', NUMERIC(12, 2), nullable=True, default=0),
        sa.Column('target_revenue_usd', NUMERIC(12, 2), nullable=True, default=0),
        sa.Column('target_orders', sa.Integer(), nullable=True, default=0),
        sa.Column('target_customers', sa.Integer(), nullable=True, default=0),

        # Achievement tracking
        sa.Column('achieved_revenue_iqd', NUMERIC(12, 2), nullable=True, default=0),
        sa.Column('achieved_revenue_usd', NUMERIC(12, 2), nullable=True, default=0),
        sa.Column('achieved_orders', sa.Integer(), nullable=True, default=0),
        sa.Column('achieved_customers', sa.Integer(), nullable=True, default=0),

        # Progress percentages (auto-calculated)
        sa.Column('revenue_progress_percentage', NUMERIC(5, 2), nullable=True, default=0),
        sa.Column('orders_progress_percentage', NUMERIC(5, 2), nullable=True, default=0),
        sa.Column('customers_progress_percentage', NUMERIC(5, 2), nullable=True, default=0),
        sa.Column('overall_progress_percentage', NUMERIC(5, 2), nullable=True, default=0),

        # Status
        sa.Column('is_achieved', sa.Boolean(), nullable=True, default=False),
        sa.Column('achievement_date', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),

        # Bonus configuration
        sa.Column('bonus_enabled', sa.Boolean(), nullable=True, default=False),
        sa.Column('bonus_percentage', NUMERIC(5, 2), nullable=True),
        sa.Column('bonus_amount', NUMERIC(12, 2), nullable=True),
        sa.Column('bonus_paid', sa.Boolean(), nullable=True, default=False),

        # Management
        sa.Column('set_by', sa.Integer(), nullable=True),
        sa.Column('set_at', sa.DateTime(), nullable=True, default=datetime.utcnow),

        # Notes
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),

        # Audit
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['salesperson_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['set_by'], ['users.id'], ),
        sa.UniqueConstraint('target_uuid')
    )

    # Indexes
    op.create_index('idx_target_salesperson', 'salesperson_targets', ['salesperson_id'])
    op.create_index('idx_target_period_start', 'salesperson_targets', ['period_start'])
    op.create_index('idx_target_period_end', 'salesperson_targets', ['period_end'])
    op.create_index('idx_target_achieved', 'salesperson_targets', ['is_achieved'])
    op.create_index('idx_target_active', 'salesperson_targets', ['is_active'])
    op.create_index('idx_target_created_at', 'salesperson_targets', ['created_at'])

    # ========================================================================
    # Daily Performance Summary Table
    # ========================================================================
    op.create_table(
        'salesperson_daily_summaries',
        sa.Column('id', sa.Integer(), nullable=False),

        # Salesperson and date
        sa.Column('salesperson_id', sa.Integer(), nullable=False),
        sa.Column('summary_date', sa.Date(), nullable=False),

        # Sales metrics
        sa.Column('total_sales_iqd', NUMERIC(12, 2), nullable=True, default=0),
        sa.Column('total_sales_usd', NUMERIC(12, 2), nullable=True, default=0),
        sa.Column('total_orders', sa.Integer(), nullable=True, default=0),
        sa.Column('total_customers_visited', sa.Integer(), nullable=True, default=0),
        sa.Column('avg_order_value', NUMERIC(12, 2), nullable=True, default=0),

        # Commission
        sa.Column('daily_commission', NUMERIC(12, 2), nullable=True, default=0),

        # GPS tracking
        sa.Column('total_distance_km', NUMERIC(8, 2), nullable=True, default=0),
        sa.Column('total_time_hours', NUMERIC(6, 2), nullable=True, default=0),
        sa.Column('gps_points_count', sa.Integer(), nullable=True, default=0),

        # Activity
        sa.Column('customer_visits', sa.Integer(), nullable=True, default=0),
        sa.Column('verified_visits', sa.Integer(), nullable=True, default=0),

        # Money transfers
        sa.Column('transfers_made', sa.Integer(), nullable=True, default=0),
        sa.Column('total_transferred_usd', NUMERIC(12, 2), nullable=True, default=0),

        # Performance ranking
        sa.Column('daily_rank', sa.Integer(), nullable=True),

        # Calculated at
        sa.Column('calculated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['salesperson_id'], ['users.id'], )
    )

    # Indexes
    op.create_index('idx_daily_summary_salesperson', 'salesperson_daily_summaries', ['salesperson_id'])
    op.create_index('idx_daily_summary_date', 'salesperson_daily_summaries', ['summary_date'])

    # Unique constraint: one summary per salesperson per day
    op.create_index('idx_daily_summary_unique', 'salesperson_daily_summaries', ['salesperson_id', 'summary_date'], unique=True)


def downgrade():
    """Drop salesperson feature tables"""

    # Drop tables in reverse order to respect foreign keys
    op.drop_table('salesperson_daily_summaries')
    op.drop_table('salesperson_targets')
    op.drop_table('salesperson_commissions')
    op.drop_table('salesperson_gps_locations')
