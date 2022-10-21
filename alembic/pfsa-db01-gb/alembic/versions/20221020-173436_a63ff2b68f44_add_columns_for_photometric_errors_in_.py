"""Add columns for photometric errors in the fluxstd table

Revision ID: a63ff2b68f44
Revises: 99f7f6b4c0d1
Create Date: 2022-10-20 17:34:36.681006

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a63ff2b68f44'
down_revision = '99f7f6b4c0d1'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
