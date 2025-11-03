"""unified_online_store_erp_phase1_foundation

This migration merges TSH Online Store with TSH ERP System.
It adds ERP foundation tables without breaking existing online store functionality.

Phase 1: Foundation Tables
- currencies (with default IQD)
- branches (with Main Branch)
- departments
- warehouses
- roles (Admin, Manager, Salesperson, etc.)
- permissions
- Enhanced security tables (login_attempts, security_events)

Revision ID: 185267bccfd3
Revises: None (standalone migration)
Create Date: 2025-10-30 15:13:26.531579

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '185267bccfd3'
down_revision = None  # Standalone migration - no dependencies on previous ERP migrations
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Phase 1: Create foundation tables for unified Online Store + ERP system.
    Safe to run on existing database - checks for existing tables.
    """
    conn = op.get_bind()

    # ========== CURRENCIES TABLE ==========
    # Check if currencies table exists
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'currencies')"
    )).scalar()

    if not result:
        op.create_table('currencies',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('code', sa.String(length=3), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('symbol', sa.String(length=10), nullable=True),
            sa.Column('exchange_rate', sa.Numeric(precision=15, scale=6), nullable=False, server_default='1.0'),
            sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
            sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('code')
        )

        # Insert default currency - Iraqi Dinar
        op.execute("""
            INSERT INTO currencies (code, name, symbol, exchange_rate, is_active)
            VALUES ('IQD', 'Iraqi Dinar', 'د.ع', 1.0, true)
        """)

    # ========== BRANCHES TABLE ==========
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'branches')"
    )).scalar()

    if not result:
        op.create_table('branches',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=200), nullable=False),
            sa.Column('code', sa.String(length=50), nullable=False),
            sa.Column('address', sa.Text(), nullable=True),
            sa.Column('city', sa.String(length=100), nullable=True),
            sa.Column('phone', sa.String(length=50), nullable=True),
            sa.Column('email', sa.String(length=200), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
            sa.Column('currency_id', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
            sa.ForeignKeyConstraint(['currency_id'], ['currencies.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('code')
        )

        # Insert default branch
        op.execute("""
            INSERT INTO branches (name, code, is_active, currency_id)
            VALUES ('Main Branch', 'MAIN', true, 1)
        """)

    # ========== DEPARTMENTS TABLE ==========
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'departments')"
    )).scalar()

    if not result:
        op.create_table('departments',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=200), nullable=False),
            sa.Column('code', sa.String(length=50), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('manager_id', sa.Integer(), nullable=True),
            sa.Column('branch_id', sa.Integer(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
            sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
            sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('code')
        )

    # ========== WAREHOUSES TABLE ==========
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'warehouses')"
    )).scalar()

    if not result:
        op.create_table('warehouses',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=200), nullable=False),
            sa.Column('code', sa.String(length=50), nullable=False),
            sa.Column('address', sa.Text(), nullable=True),
            sa.Column('branch_id', sa.Integer(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
            sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
            sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('code')
        )

    # ========== ROLES TABLE ==========
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'roles')"
    )).scalar()

    if not result:
        op.create_table('roles',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
            sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )

        # Insert default roles
        op.execute("""
            INSERT INTO roles (name, description) VALUES
            ('Admin', 'Full system access'),
            ('Manager', 'Branch and department management'),
            ('Salesperson', 'Sales and customer management'),
            ('Cashier', 'POS and retail operations'),
            ('Inventory Manager', 'Stock and warehouse management'),
            ('Accountant', 'Financial operations'),
            ('HR Manager', 'Human resources management'),
            ('Viewer', 'Read-only access')
        """)

    # ========== PERMISSIONS TABLE ==========
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'permissions')"
    )).scalar()

    if not result:
        op.create_table('permissions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('code', sa.String(length=100), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('module', sa.String(length=50), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('code')
        )

    # ========== ROLE_PERMISSIONS TABLE ==========
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'role_permissions')"
    )).scalar()

    if not result:
        op.create_table('role_permissions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('role_id', sa.Integer(), nullable=False),
            sa.Column('permission_id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
            sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ),
            sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('role_id', 'permission_id', name='uq_role_permission')
        )

    # ========== LOGIN_ATTEMPTS TABLE (for security tracking) ==========
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'login_attempts')"
    )).scalar()

    if not result:
        op.create_table('login_attempts',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('email', sa.String(length=255), nullable=False),
            sa.Column('ip_address', sa.String(length=45), nullable=True),
            sa.Column('user_agent', sa.Text(), nullable=True),
            sa.Column('success', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('failure_reason', sa.String(length=255), nullable=True),
            sa.Column('attempted_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.Column('country', sa.String(length=100), nullable=True),
            sa.Column('city', sa.String(length=100), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_login_attempts_email', 'login_attempts', ['email'])
        op.create_index('idx_login_attempts_attempted_at', 'login_attempts', ['attempted_at'])

    # ========== SECURITY_EVENTS TABLE ==========
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'security_events')"
    )).scalar()

    if not result:
        op.create_table('security_events',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('event_type', sa.String(length=100), nullable=False),
            sa.Column('severity', sa.String(length=20), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('ip_address', sa.String(length=45), nullable=True),
            sa.Column('user_agent', sa.Text(), nullable=True),
            sa.Column('event_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.Column('resolved', sa.Boolean(), nullable=True, server_default='false'),
            sa.Column('resolved_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_security_events_event_type', 'security_events', ['event_type'])
        op.create_index('idx_security_events_severity', 'security_events', ['severity'])
        op.create_index('idx_security_events_created_at', 'security_events', ['created_at'])

    # ========== EXTEND EXISTING TABLES (if columns don't exist) ==========

    # Add ERP fields to existing users table
    result = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='users' AND column_name='role_id'"
    )).scalar()

    if not result:
        op.add_column('users', sa.Column('role_id', sa.Integer(), nullable=True))
        op.create_foreign_key('fk_users_role', 'users', 'roles', ['role_id'], ['id'])

    result = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='users' AND column_name='branch_id'"
    )).scalar()

    if not result:
        op.add_column('users', sa.Column('branch_id', sa.Integer(), nullable=True))
        op.create_foreign_key('fk_users_branch', 'users', 'branches', ['branch_id'], ['id'])

    result = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='users' AND column_name='is_active'"
    )).scalar()

    if not result:
        op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'))

    result = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='users' AND column_name='password'"
    )).scalar()

    if not result:
        op.add_column('users', sa.Column('password', sa.String(length=255), nullable=True))

    # Set default branch for existing users
    op.execute("UPDATE users SET branch_id = 1 WHERE branch_id IS NULL")

    print("✅ Phase 1 Migration Complete: Foundation tables created successfully!")
    print("📋 Created: currencies, branches, departments, warehouses, roles, permissions")
    print("🔒 Created: login_attempts, security_events")
    print("✨ Extended: users table with role_id, branch_id, is_active, password")


def downgrade() -> None:
    """Rollback Phase 1 migration"""
    # Remove added columns from users table
    op.drop_constraint('fk_users_branch', 'users', type_='foreignkey')
    op.drop_constraint('fk_users_role', 'users', type_='foreignkey')
    op.drop_column('users', 'password')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'branch_id')
    op.drop_column('users', 'role_id')

    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('security_events')
    op.drop_table('login_attempts')
    op.drop_table('role_permissions')
    op.drop_table('permissions')
    op.drop_table('roles')
    op.drop_table('warehouses')
    op.drop_table('departments')
    op.drop_table('branches')
    op.drop_table('currencies') 