"""set single_exptime un-nullable

Revision ID: 1027c2966c63
Revises: f630d28235eb
Create Date: 2024-05-24 14:58:17.757023

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1027c2966c63'
down_revision = 'f630d28235eb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('target', 'single_exptime',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False,
               existing_comment='Individual exposure time (s)')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('target', 'single_exptime',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=True,
               existing_comment='Individual exposure time (s)')
    # ### end Alembic commands ###