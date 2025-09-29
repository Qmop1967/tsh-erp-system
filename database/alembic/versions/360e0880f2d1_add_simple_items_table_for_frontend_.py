"""add simple items table for frontend testing

Revision ID: 360e0880f2d1
Revises: 7f4232a6ba23
Create Date: 2025-09-28 10:48:31.328036

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '360e0880f2d1'
down_revision = '7f4232a6ba23'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create items table for simple inventory testing
    op.create_table('items',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('sku', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('quantity_on_hand', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('items')