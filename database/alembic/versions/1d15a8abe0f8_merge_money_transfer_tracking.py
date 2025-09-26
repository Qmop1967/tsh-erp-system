"""merge money transfer tracking

Revision ID: 1d15a8abe0f8
Revises: 6163f7adfc75, emergency_money_transfer_tracking
Create Date: 2025-07-05 22:43:01.916769

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d15a8abe0f8'
down_revision = ('6163f7adfc75', 'emergency_money_transfer')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 