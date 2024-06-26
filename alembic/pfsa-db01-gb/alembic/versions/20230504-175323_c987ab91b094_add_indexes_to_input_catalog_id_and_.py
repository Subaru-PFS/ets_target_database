"""Add indexes to input_catalog_id and version

Revision ID: c987ab91b094
Revises: 6aec47e0f339
Create Date: 2023-05-04 17:53:23.315181

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c987ab91b094'
down_revision = '6aec47e0f339'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_index('fluxstd_q3c_ang2ipix_idx', table_name='fluxstd')
    # op.drop_index('sky_q3c_ang2ipix_idx', table_name='sky')
    op.create_index(op.f('ix_sky_input_catalog_id'), 'sky', ['input_catalog_id'], unique=False)
    op.create_index(op.f('ix_sky_version'), 'sky', ['version'], unique=False)
    # op.drop_index('target_q3c_ang2ipix_idx', table_name='target')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.create_index('target_q3c_ang2ipix_idx', 'target', [sa.text('q3c_ang2ipix(ra, "dec")')], unique=False)
    op.drop_index(op.f('ix_sky_version'), table_name='sky')
    op.drop_index(op.f('ix_sky_input_catalog_id'), table_name='sky')
    # op.create_index('sky_q3c_ang2ipix_idx', 'sky', [sa.text('q3c_ang2ipix(ra, "dec")')], unique=False)
    # op.create_index('fluxstd_q3c_ang2ipix_idx', 'fluxstd', [sa.text('q3c_ang2ipix(ra, "dec")')], unique=False)
    # ### end Alembic commands ###
