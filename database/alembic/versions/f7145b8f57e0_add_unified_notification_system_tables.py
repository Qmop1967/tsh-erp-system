"""add_unified_notification_system_tables

Revision ID: f7145b8f57e0
Revises: 8579948f044e
Create Date: 2025-10-24 02:10:03.261010

Enterprise-grade unified notification system with:
- Multi-channel delivery (in-app, push, email, SMS, WebSocket)
- Template-based notifications with variable substitution
- User preferences with quiet hours
- Real-time WebSocket support
- Priority-based filtering
- Grouping and archiving
- Audit logging

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f7145b8f57e0'
down_revision = '8579948f044e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='medium'),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('icon', sa.String(length=100), nullable=True),
        sa.Column('color', sa.String(length=20), nullable=True),
        sa.Column('action_url', sa.String(length=500), nullable=True),
        sa.Column('action_label', sa.String(length=100), nullable=True),
        sa.Column('actions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('meta_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_archived', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('channels', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='["in_app"]'),
        sa.Column('sent_via', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('delivery_status', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('related_entity_type', sa.String(length=50), nullable=True),
        sa.Column('related_entity_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_created_at'), 'notifications', ['created_at'], unique=False)
    op.create_index(op.f('ix_notifications_is_archived'), 'notifications', ['is_archived'], unique=False)
    op.create_index(op.f('ix_notifications_is_read'), 'notifications', ['is_read'], unique=False)
    op.create_index(op.f('ix_notifications_related_entity_id'), 'notifications', ['related_entity_id'], unique=False)
    op.create_index(op.f('ix_notifications_related_entity_type'), 'notifications', ['related_entity_type'], unique=False)
    op.create_index(op.f('ix_notifications_tenant_id'), 'notifications', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_notifications_type'), 'notifications', ['type'], unique=False)
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'], unique=False)

    # Create notification_templates table
    op.create_table(
        'notification_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('title_template', sa.String(length=500), nullable=False),
        sa.Column('message_template', sa.Text(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='medium'),
        sa.Column('default_channels', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='["in_app"]'),
        sa.Column('icon', sa.String(length=100), nullable=True),
        sa.Column('color', sa.String(length=20), nullable=True),
        sa.Column('default_action_url', sa.String(length=500), nullable=True),
        sa.Column('default_action_label', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_notification_templates_code'), 'notification_templates', ['code'], unique=True)

    # Create notification_preferences table
    op.create_table(
        'notification_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('quiet_hours_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('quiet_hours_start', sa.String(length=5), nullable=True),
        sa.Column('quiet_hours_end', sa.String(length=5), nullable=True),
        sa.Column('enable_in_app', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('enable_push', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('enable_email', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('enable_sms', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('type_preferences', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('min_priority', sa.String(length=20), nullable=False, server_default='low'),
        sa.Column('fcm_tokens', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('apns_tokens', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('email_address', sa.String(length=255), nullable=True),
        sa.Column('email_digest_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('email_digest_frequency', sa.String(length=20), nullable=False, server_default='daily'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_notification_preferences_user_id'), 'notification_preferences', ['user_id'], unique=True)

    # Create notification_groups table
    op.create_table(
        'notification_groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_expanded', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_notification_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_groups_user_id'), 'notification_groups', ['user_id'], unique=False)

    # Create notification_logs table
    op.create_table(
        'notification_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('notification_id', sa.Integer(), nullable=False),
        sa.Column('channel', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('meta_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['notification_id'], ['notifications.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_logs_notification_id'), 'notification_logs', ['notification_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_notification_logs_notification_id'), table_name='notification_logs')
    op.drop_table('notification_logs')

    op.drop_index(op.f('ix_notification_groups_user_id'), table_name='notification_groups')
    op.drop_table('notification_groups')

    op.drop_index(op.f('ix_notification_preferences_user_id'), table_name='notification_preferences')
    op.drop_table('notification_preferences')

    op.drop_index(op.f('ix_notification_templates_code'), table_name='notification_templates')
    op.drop_table('notification_templates')

    op.drop_index(op.f('ix_notifications_user_id'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_type'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_tenant_id'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_related_entity_type'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_related_entity_id'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_is_read'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_is_archived'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_created_at'), table_name='notifications')
    op.drop_table('notifications') 