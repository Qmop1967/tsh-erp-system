"""Add advanced security and multi-tenancy models

Revision ID: add_security_multitenancy
Revises: (previous revision)
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_security_multitenancy'
down_revision = None  # Set to your latest revision
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create tenants table
    op.create_table('tenants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=True),
        sa.Column('subdomain', sa.String(length=100), nullable=True),
        sa.Column('subscription_tier', sa.String(length=50), nullable=True),
        sa.Column('max_users', sa.Integer(), nullable=True),
        sa.Column('max_branches', sa.Integer(), nullable=True),
        sa.Column('max_storage_gb', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('settings', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('subdomain')
    )
    op.create_index(op.f('ix_tenants_id'), 'tenants', ['id'], unique=False)

    # Create tenant_settings table
    op.create_table('tenant_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('is_encrypted', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create permissions table
    op.create_table('permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('resource_type', postgresql.ENUM('BRANCH', 'USER', 'PRODUCT', 'INVENTORY', 'SALES', 'CUSTOMER', 'FINANCIAL', 'REPORTS', 'SETTINGS', name='resourcetype'), nullable=False),
        sa.Column('permission_type', postgresql.ENUM('CREATE', 'READ', 'UPDATE', 'DELETE', 'APPROVE', 'EXPORT', 'IMPORT', name='permissiontype'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_permissions_id'), 'permissions', ['id'], unique=False)

    # Create role_permissions table
    op.create_table('role_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.Column('granted_by', sa.Integer(), nullable=True),
        sa.Column('granted_at', sa.DateTime(), nullable=True),
        sa.Column('conditions', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.ForeignKeyConstraint(['granted_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create user_permissions table
    op.create_table('user_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.Column('is_granted', sa.Boolean(), nullable=True),
        sa.Column('granted_by', sa.Integer(), nullable=True),
        sa.Column('granted_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('conditions', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['granted_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.String(length=100), nullable=True),
        sa.Column('old_values', sa.Text(), nullable=True),
        sa.Column('new_values', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('branch_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Add tenant_id to existing tables for multi-tenancy
    op.add_column('branches', sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('password_salt', sa.String(length=64), nullable=True))
    
    # Add foreign key constraints
    op.create_foreign_key(None, 'branches', 'tenants', ['tenant_id'], ['id'])
    op.create_foreign_key(None, 'users', 'tenants', ['tenant_id'], ['id'])
    
    # Create indexes for performance
    op.create_index('ix_branches_tenant_id', 'branches', ['tenant_id'], unique=False)
    op.create_index('ix_users_tenant_id', 'users', ['tenant_id'], unique=False)
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'], unique=False)
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'], unique=False)
    op.create_index('ix_audit_logs_resource_type', 'audit_logs', ['resource_type'], unique=False)

    # Insert default permissions
    permissions_data = [
        # User management
        ('create_user', 'Create new users', 'USER', 'CREATE'),
        ('read_user', 'View user information', 'USER', 'READ'),
        ('update_user', 'Update user information', 'USER', 'UPDATE'),
        ('delete_user', 'Delete users', 'USER', 'DELETE'),
        
        # Permission management
        ('grant_permissions', 'Grant permissions to users', 'USER', 'APPROVE'),
        ('revoke_permissions', 'Revoke permissions from users', 'USER', 'APPROVE'),
        ('view_user_permissions', 'View user permissions', 'USER', 'READ'),
        
        # Backup management
        ('create_backup', 'Create system backups', 'SETTINGS', 'CREATE'),
        ('schedule_backup', 'Schedule automatic backups', 'SETTINGS', 'UPDATE'),
        ('initiate_restore', 'Initiate backup restore', 'SETTINGS', 'APPROVE'),
        ('approve_restore', 'Approve backup restore requests', 'SETTINGS', 'APPROVE'),
        
        # Security and audit
        ('view_audit_logs', 'View system audit logs', 'SETTINGS', 'READ'),
        ('view_security_alerts', 'View security alerts', 'SETTINGS', 'READ'),
        ('view_system_health', 'View system health status', 'SETTINGS', 'READ'),
        ('view_performance_metrics', 'View performance metrics', 'SETTINGS', 'READ'),
        
        # Tenant management
        ('view_tenant_info', 'View tenant information', 'SETTINGS', 'READ'),
        ('view_usage_stats', 'View usage statistics', 'SETTINGS', 'READ'),
        
        # Branch management
        ('create_branch', 'Create new branches', 'BRANCH', 'CREATE'),
        ('read_branch', 'View branch information', 'BRANCH', 'READ'),
        ('update_branch', 'Update branch information', 'BRANCH', 'UPDATE'),
        ('delete_branch', 'Delete branches', 'BRANCH', 'DELETE'),
        
        # Product management
        ('create_product', 'Create new products', 'PRODUCT', 'CREATE'),
        ('read_product', 'View product information', 'PRODUCT', 'READ'),
        ('update_product', 'Update product information', 'PRODUCT', 'UPDATE'),
        ('delete_product', 'Delete products', 'PRODUCT', 'DELETE'),
        ('export_products', 'Export product data', 'PRODUCT', 'EXPORT'),
        ('import_products', 'Import product data', 'PRODUCT', 'IMPORT'),
        
        # Inventory management
        ('create_inventory', 'Create inventory items', 'INVENTORY', 'CREATE'),
        ('read_inventory', 'View inventory information', 'INVENTORY', 'READ'),
        ('update_inventory', 'Update inventory information', 'INVENTORY', 'UPDATE'),
        ('delete_inventory', 'Delete inventory items', 'INVENTORY', 'DELETE'),
        ('approve_inventory', 'Approve inventory changes', 'INVENTORY', 'APPROVE'),
        
        # Sales management
        ('create_sales', 'Create sales orders', 'SALES', 'CREATE'),
        ('read_sales', 'View sales information', 'SALES', 'READ'),
        ('update_sales', 'Update sales orders', 'SALES', 'UPDATE'),
        ('delete_sales', 'Delete sales orders', 'SALES', 'DELETE'),
        ('approve_sales', 'Approve sales orders', 'SALES', 'APPROVE'),
        
        # Customer management
        ('create_customer', 'Create new customers', 'CUSTOMER', 'CREATE'),
        ('read_customer', 'View customer information', 'CUSTOMER', 'READ'),
        ('update_customer', 'Update customer information', 'CUSTOMER', 'UPDATE'),
        ('delete_customer', 'Delete customers', 'CUSTOMER', 'DELETE'),
        
        # Financial management
        ('create_financial', 'Create financial records', 'FINANCIAL', 'CREATE'),
        ('read_financial', 'View financial information', 'FINANCIAL', 'READ'),
        ('update_financial', 'Update financial records', 'FINANCIAL', 'UPDATE'),
        ('delete_financial', 'Delete financial records', 'FINANCIAL', 'DELETE'),
        ('approve_financial', 'Approve financial transactions', 'FINANCIAL', 'APPROVE'),
        
        # Reports
        ('read_reports', 'View system reports', 'REPORTS', 'READ'),
        ('export_reports', 'Export reports', 'REPORTS', 'EXPORT'),
    ]
    
    # Insert permissions
    permissions_table = sa.table('permissions',
        sa.column('name', sa.String),
        sa.column('description', sa.String),
        sa.column('resource_type', sa.String),
        sa.column('permission_type', sa.String),
        sa.column('is_active', sa.Boolean),
        sa.column('created_at', sa.DateTime)
    )
    
    for name, desc, resource, perm_type in permissions_data:
        op.execute(
            permissions_table.insert().values(
                name=name,
                description=desc,
                resource_type=resource,
                permission_type=perm_type,
                is_active=True,
                created_at=sa.func.now()
            )
        )

def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('audit_logs')
    op.drop_table('user_permissions')
    op.drop_table('role_permissions')
    op.drop_table('permissions')
    op.drop_table('tenant_settings')
    op.drop_table('tenants')
    
    # Remove added columns
    op.drop_column('users', 'password_salt')
    op.drop_column('users', 'tenant_id')
    op.drop_column('branches', 'tenant_id')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS resourcetype')
    op.execute('DROP TYPE IF EXISTS permissiontype')
