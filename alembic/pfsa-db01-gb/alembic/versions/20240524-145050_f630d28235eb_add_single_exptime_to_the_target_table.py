"""Add single_exptime to the target table

Revision ID: f630d28235eb
Revises: 368dce443754
Create Date: 2024-05-24 14:50:50.589144

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f630d28235eb'
down_revision = '368dce443754'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('target', sa.Column('single_exptime', sa.Float(), nullable=True, comment='Individual exposure time (s)'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('target', 'single_exptime')
    # ### end Alembic commands ###