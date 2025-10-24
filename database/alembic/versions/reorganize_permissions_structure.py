"""reorganize permissions structure with application access

Revision ID: b1c2d3e4f5g6
Revises: 360e0880f2d1, a1b2c3d4e5f6
Create Date: 2025-01-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b1c2d3e4f5g6'
down_revision = ('360e0880f2d1', 'a1b2c3d4e5f6')
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Reorganize permissions table structure to support:
    1. Module-based organization
    2. Action-based granularity
    3. Application access control
    4. Better categorization
    """

    # Add new columns to permissions table
    op.add_column('permissions', sa.Column('code', sa.String(length=100), nullable=True))
    op.add_column('permissions', sa.Column('module', sa.String(length=50), nullable=True))
    op.add_column('permissions', sa.Column('action', sa.String(length=50), nullable=True))
    op.add_column('permissions', sa.Column('display_order', sa.Integer(), server_default='0', nullable=False))
    op.add_column('permissions', sa.Column('updated_at', sa.DateTime(), nullable=True))

    # Rename 'name' to have more space for descriptive names
    op.alter_column('permissions', 'name',
                    existing_type=sa.String(length=100),
                    type_=sa.String(length=200),
                    nullable=False)

    # Migrate existing data: create code from name
    # This will be a simple migration - in production you'd want more sophisticated mapping
    op.execute("""
        UPDATE permissions
        SET code = LOWER(REPLACE(name, ' ', '_')),
            module = COALESCE(category, 'settings'),
            action = 'view',
            updated_at = NOW()
        WHERE code IS NULL
    """)

    # Now make code not nullable and add unique constraint
    op.alter_column('permissions', 'code', nullable=False)
    op.create_index(op.f('ix_permissions_code'), 'permissions', ['code'], unique=True)

    # Add indexes for better query performance
    op.create_index(op.f('ix_permissions_module'), 'permissions', ['module'])
    op.create_index(op.f('ix_permissions_action'), 'permissions', ['action'])

    # Drop old columns that are no longer needed (if they existed)
    # op.drop_column('permissions', 'resource_type')  # Replaced by module
    # op.drop_column('permissions', 'permission_type')  # Replaced by action


def downgrade() -> None:
    """Revert the changes"""

    # Remove indexes
    op.drop_index(op.f('ix_permissions_action'), table_name='permissions')
    op.drop_index(op.f('ix_permissions_module'), table_name='permissions')
    op.drop_index(op.f('ix_permissions_code'), table_name='permissions')

    # Remove new columns
    op.drop_column('permissions', 'updated_at')
    op.drop_column('permissions', 'display_order')
    op.drop_column('permissions', 'action')
    op.drop_column('permissions', 'module')
    op.drop_column('permissions', 'code')

    # Revert name column length
    op.alter_column('permissions', 'name',
                    existing_type=sa.String(length=200),
                    type_=sa.String(length=100),
                    nullable=False)
