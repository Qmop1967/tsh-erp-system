"""Merge security and main branches

Revision ID: 6f31f5b15936
Revises: 700e3f25897c, add_security_multitenancy
Create Date: 2025-08-14 14:09:23.916214

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f31f5b15936'
down_revision = ('700e3f25897c', 'add_security_multitenancy')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 