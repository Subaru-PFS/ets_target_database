"""add filter_v and change accordingly

Revision ID: 31f82c75c58d
Revises: 5df293bb75f2
Create Date: 2026-05-21 09:09:10.662583

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31f82c75c58d'
down_revision = '5df293bb75f2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('fluxstd', sa.Column('psf_mag_v', sa.Float(), nullable=True, comment='v-band PSF magnitude (AB mag)'))
    op.add_column('fluxstd', sa.Column('psf_mag_error_v', sa.Float(), nullable=True, comment='Error in v-band PSF magnitude (AB mag)'))
    op.add_column('fluxstd', sa.Column('psf_flux_v', sa.Float(), nullable=True, comment='v-band PSF flux (nJy)'))
    op.add_column('fluxstd', sa.Column('psf_flux_error_v', sa.Float(), nullable=True, comment='Error in v-band PSF flux (nJy)'))
    op.add_column('fluxstd', sa.Column('filter_v', sa.String(), nullable=True, comment='v-band filter (v_skymapper, v_splus, etc.)'))
    op.alter_column('fluxstd', 'filter_u',
               existing_type=sa.VARCHAR(),
               comment='u-band filter (u_sdss, u_cfht, u_skymapper, etc.)',
               existing_comment='u-band filter (u_sdss, u_cfht, etc.)',
               existing_nullable=True)
    op.create_foreign_key('fluxstd_filter_v_fkey', 'fluxstd', 'filter_name', ['filter_v'], ['filter_name'])
    op.add_column('target', sa.Column('fiber_mag_v', sa.Float(), nullable=True, comment='v-band magnitude within a fiber (AB mag)'))
    op.add_column('target', sa.Column('psf_mag_v', sa.Float(), nullable=True, comment='v-band PSF magnitude (AB mag)'))
    op.add_column('target', sa.Column('psf_mag_error_v', sa.Float(), nullable=True, comment='Error in v-band PSF magnitude (AB mag)'))
    op.add_column('target', sa.Column('psf_flux_v', sa.Float(), nullable=True, comment='v-band PSF flux (nJy)'))
    op.add_column('target', sa.Column('psf_flux_error_v', sa.Float(), nullable=True, comment='Error in v-band PSF flux (nJy)'))
    op.add_column('target', sa.Column('total_flux_v', sa.Float(), nullable=True, comment='v-band total flux (nJy)'))
    op.add_column('target', sa.Column('total_flux_error_v', sa.Float(), nullable=True, comment='Error in v-band total flux (nJy)'))
    op.add_column('target', sa.Column('filter_v', sa.String(), nullable=True, comment='v-band filter (v_skymapper, v_splus, etc.)'))
    op.alter_column('target', 'filter_u',
               existing_type=sa.VARCHAR(),
               comment='u-band filter (u_sdss, u_cfht, u_skymapper, etc.)',
               existing_comment='u-band filter (u_sdss, u_cfht, etc.)',
               existing_nullable=True)
    op.create_foreign_key('target_filter_v_fkey', 'target', 'filter_name', ['filter_v'], ['filter_name'])


def downgrade():
    op.drop_constraint('target_filter_v_fkey', 'target', type_='foreignkey')
    op.alter_column('target', 'filter_u',
               existing_type=sa.VARCHAR(),
               comment='u-band filter (u_sdss, u_cfht, etc.)',
               existing_comment='u-band filter (u_sdss, u_cfht, u_skymapper, etc.)',
               existing_nullable=True)
    op.drop_column('target', 'filter_v')
    op.drop_column('target', 'total_flux_error_v')
    op.drop_column('target', 'total_flux_v')
    op.drop_column('target', 'psf_flux_error_v')
    op.drop_column('target', 'psf_flux_v')
    op.drop_column('target', 'psf_mag_error_v')
    op.drop_column('target', 'psf_mag_v')
    op.drop_column('target', 'fiber_mag_v')
    op.drop_constraint('fluxstd_filter_v_fkey', 'fluxstd', type_='foreignkey')
    op.alter_column('fluxstd', 'filter_u',
               existing_type=sa.VARCHAR(),
               comment='u-band filter (u_sdss, u_cfht, etc.)',
               existing_comment='u-band filter (u_sdss, u_cfht, u_skymapper, etc.)',
               existing_nullable=True)
    op.drop_column('fluxstd', 'filter_v')
    op.drop_column('fluxstd', 'psf_flux_error_v')
    op.drop_column('fluxstd', 'psf_flux_v')
    op.drop_column('fluxstd', 'psf_mag_error_v')
    op.drop_column('fluxstd', 'psf_mag_v')
