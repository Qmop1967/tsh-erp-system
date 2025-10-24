"""update_permissions_schema_to_new_structure

Revision ID: 4c129201dab2
Revises: b1c2d3e4f5g6
Create Date: 2025-10-21 14:49:46.621692

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c129201dab2'
down_revision = 'b1c2d3e4f5g6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Convert enum columns to varchar to allow string manipulation
    op.execute("ALTER TABLE permissions ALTER COLUMN resource_type TYPE VARCHAR(50) USING resource_type::text")
    op.execute("ALTER TABLE permissions ALTER COLUMN permission_type TYPE VARCHAR(50) USING permission_type::text")

    # Step 2: Add new columns
    op.add_column('permissions', sa.Column('code', sa.String(length=100), nullable=True))
    op.add_column('permissions', sa.Column('module', sa.String(length=50), nullable=True))
    op.add_column('permissions', sa.Column('action', sa.String(length=50), nullable=True))
    op.add_column('permissions', sa.Column('category', sa.String(length=100), nullable=True))
    op.add_column('permissions', sa.Column('display_order', sa.Integer(), nullable=True, server_default='0'))

    # Step 3: Migrate data from old columns to new columns
    op.execute("""
        UPDATE permissions
        SET module = COALESCE(resource_type, 'user_management'),
            action = COALESCE(permission_type, 'view'),
            code = LOWER(CONCAT(COALESCE(resource_type, 'user_management'), '.', name, '.', COALESCE(permission_type, 'view')))
        WHERE code IS NULL
    """)

    # Step 4: Make new columns non-nullable after migration
    op.alter_column('permissions', 'code', nullable=False)
    op.alter_column('permissions', 'module', nullable=False)
    op.alter_column('permissions', 'action', nullable=False)

    # Step 5: Create indexes
    op.create_index(op.f('ix_permissions_code'), 'permissions', ['code'], unique=True)
    op.create_index(op.f('ix_permissions_module'), 'permissions', ['module'], unique=False)
    op.create_index(op.f('ix_permissions_action'), 'permissions', ['action'], unique=False)

    # Step 6: Drop old columns
    op.drop_column('permissions', 'resource_type')
    op.drop_column('permissions', 'permission_type')


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_permissions_action'), table_name='permissions')
    op.drop_index(op.f('ix_permissions_module'), table_name='permissions')
    op.drop_index(op.f('ix_permissions_code'), table_name='permissions')

    # Add back old columns
    op.add_column('permissions', sa.Column('permission_type', sa.String(length=50), nullable=True))
    op.add_column('permissions', sa.Column('resource_type', sa.String(length=50), nullable=True))

    # Migrate data back
    op.execute("""
        UPDATE permissions
        SET permission_type = action,
            resource_type = module
    """)

    # Drop new columns
    op.drop_column('permissions', 'display_order')
    op.drop_column('permissions', 'category')
    op.drop_column('permissions', 'action')
    op.drop_column('permissions', 'module')
    op.drop_column('permissions', 'code') 