"""add_zoho_sync_fields_users_customers

Revision ID: zoho_sync_001
Revises: 185267bccfd3
Create Date: 2025-11-16

Add Zoho sync fields to users and customers tables to track:
- Zoho user IDs for mapping salespersons
- Zoho contact IDs and owner IDs for customer relationships
- Last sync timestamps for both tables
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'zoho_sync_001'
down_revision: Union[str, None] = '185267bccfd3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Zoho sync fields to users and customers tables"""

    # Add Zoho sync fields to users table
    op.add_column('users', sa.Column('zoho_user_id', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('zoho_last_sync', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_users_zoho_user_id'), 'users', ['zoho_user_id'], unique=True)

    # Add Zoho sync fields to customers table
    op.add_column('customers', sa.Column('zoho_contact_id', sa.String(length=100), nullable=True))
    op.add_column('customers', sa.Column('zoho_owner_id', sa.String(length=100), nullable=True))
    op.add_column('customers', sa.Column('zoho_last_sync', postgresql.TIMESTAMP(timezone=True), nullable=True))
    op.create_index(op.f('ix_customers_zoho_contact_id'), 'customers', ['zoho_contact_id'], unique=True)
    op.create_index(op.f('ix_customers_zoho_owner_id'), 'customers', ['zoho_owner_id'], unique=False)


def downgrade() -> None:
    """Remove Zoho sync fields from users and customers tables"""

    # Remove from customers table
    op.drop_index(op.f('ix_customers_zoho_owner_id'), table_name='customers')
    op.drop_index(op.f('ix_customers_zoho_contact_id'), table_name='customers')
    op.drop_column('customers', 'zoho_last_sync')
    op.drop_column('customers', 'zoho_owner_id')
    op.drop_column('customers', 'zoho_contact_id')

    # Remove from users table
    op.drop_index(op.f('ix_users_zoho_user_id'), table_name='users')
    op.drop_column('users', 'zoho_last_sync')
    op.drop_column('users', 'zoho_user_id')
