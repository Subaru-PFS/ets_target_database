"""add index target.input_catalog_id

Revision ID: 3923581e4392
Revises: fc8ea63b8c9d
Create Date: 2025-07-31 21:27:20.574882

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3923581e4392'
down_revision = 'fc8ea63b8c9d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('target_input_catalog_id_idx', 'target', ['input_catalog_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('target_input_catalog_id_idx', table_name='target')
    # ### end Alembic commands ###
