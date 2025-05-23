"""add total fluxes

Revision ID: fc8ea63b8c9d
Revises: 5b40ed8dcd48
Create Date: 2025-05-05 16:21:26.652825

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc8ea63b8c9d'
down_revision = '5b40ed8dcd48'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('target', sa.Column('total_flux_g', sa.Float(), nullable=True, comment='g-band total flux (nJy)'))
    op.add_column('target', sa.Column('total_flux_r', sa.Float(), nullable=True, comment='r-band total flux (nJy)'))
    op.add_column('target', sa.Column('total_flux_i', sa.Float(), nullable=True, comment='i-band total flux (nJy)'))
    op.add_column('target', sa.Column('total_flux_z', sa.Float(), nullable=True, comment='z-band total flux (nJy)'))
    op.add_column('target', sa.Column('total_flux_y', sa.Float(), nullable=True, comment='y-band total flux (nJy)'))
    op.add_column('target', sa.Column('total_flux_j', sa.Float(), nullable=True, comment='J band total flux (nJy)'))
    op.add_column('target', sa.Column('total_flux_error_g', sa.Float(), nullable=True, comment='Error in g-band total flux (nJy)'))
    op.add_column('target', sa.Column('total_flux_error_r', sa.Float(), nullable=True, comment='Error in r-band total flux (nJy)'))
    op.add_column('target', sa.Column('total_flux_error_i', sa.Float(), nullable=True, comment='Error in i-band total flux (nJy)'))
    op.add_column('target', sa.Column('total_flux_error_z', sa.Float(), nullable=True, comment='Error in z-band total flux (nJy)'))
    op.add_column('target', sa.Column('total_flux_error_y', sa.Float(), nullable=True, comment='Error in y-band total flux (nJy)'))
    op.add_column('target', sa.Column('total_flux_error_j', sa.Float(), nullable=True, comment='Error in J band total flux (nJy)'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('target', 'total_flux_error_j')
    op.drop_column('target', 'total_flux_error_y')
    op.drop_column('target', 'total_flux_error_z')
    op.drop_column('target', 'total_flux_error_i')
    op.drop_column('target', 'total_flux_error_r')
    op.drop_column('target', 'total_flux_error_g')
    op.drop_column('target', 'total_flux_j')
    op.drop_column('target', 'total_flux_y')
    op.drop_column('target', 'total_flux_z')
    op.drop_column('target', 'total_flux_i')
    op.drop_column('target', 'total_flux_r')
    op.drop_column('target', 'total_flux_g')
    # ### end Alembic commands ###
