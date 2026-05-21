"""add filter_u and change accordingly

Revision ID: 5df293bb75f2
Revises: a251bdccb11f
Create Date: 2026-05-20 18:18:28.628076

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5df293bb75f2'
down_revision = 'a251bdccb11f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('fluxstd', sa.Column('psf_mag_u', sa.Float(), nullable=True, comment='u-band PSF magnitude (AB mag)'))
    op.add_column('fluxstd', sa.Column('psf_mag_error_u', sa.Float(), nullable=True, comment='Error in u-band PSF magnitude (AB mag)'))
    op.add_column('fluxstd', sa.Column('psf_flux_u', sa.Float(), nullable=True, comment='u-band PSF flux (nJy)'))
    op.add_column('fluxstd', sa.Column('psf_flux_error_u', sa.Float(), nullable=True, comment='Error in u-band PSF flux (nJy)'))
    op.add_column('fluxstd', sa.Column('filter_u', sa.String(), nullable=True, comment='u-band filter (u_sdss, u_cfht, etc.)'))
    op.create_foreign_key('fluxstd_filter_u_fkey', 'fluxstd', 'filter_name', ['filter_u'], ['filter_name'])
    op.add_column('target', sa.Column('fiber_mag_u', sa.Float(), nullable=True, comment='u-band magnitude within a fiber (AB mag)'))
    op.add_column('target', sa.Column('psf_mag_u', sa.Float(), nullable=True, comment='u-band PSF magnitude (AB mag)'))
    op.add_column('target', sa.Column('psf_mag_error_u', sa.Float(), nullable=True, comment='Error in u-band PSF magnitude (AB mag)'))
    op.add_column('target', sa.Column('psf_flux_u', sa.Float(), nullable=True, comment='u-band PSF flux (nJy)'))
    op.add_column('target', sa.Column('psf_flux_error_u', sa.Float(), nullable=True, comment='Error in u-band PSF flux (nJy)'))
    op.add_column('target', sa.Column('total_flux_u', sa.Float(), nullable=True, comment='u-band total flux (nJy)'))
    op.add_column('target', sa.Column('total_flux_error_u', sa.Float(), nullable=True, comment='Error in u-band total flux (nJy)'))
    op.add_column('target', sa.Column('filter_u', sa.String(), nullable=True, comment='u-band filter (u_sdss, u_cfht, etc.)'))
    op.create_foreign_key('target_filter_u_fkey', 'target', 'filter_name', ['filter_u'], ['filter_name'])


def downgrade():
    op.drop_constraint('target_filter_u_fkey', 'target', type_='foreignkey')
    op.drop_column('target', 'filter_u')
    op.drop_column('target', 'total_flux_error_u')
    op.drop_column('target', 'total_flux_u')
    op.drop_column('target', 'psf_flux_error_u')
    op.drop_column('target', 'psf_flux_u')
    op.drop_column('target', 'psf_mag_error_u')
    op.drop_column('target', 'psf_mag_u')
    op.drop_column('target', 'fiber_mag_u')
    op.drop_constraint('fluxstd_filter_u_fkey', 'fluxstd', type_='foreignkey')
    op.drop_column('fluxstd', 'filter_u')
    op.drop_column('fluxstd', 'psf_flux_error_u')
    op.drop_column('fluxstd', 'psf_flux_u')
    op.drop_column('fluxstd', 'psf_mag_error_u')
    op.drop_column('fluxstd', 'psf_mag_u')
