"""drop cluster table and target.is_cluster

Revision ID: c290658f6031
Revises: 31f82c75c58d
Create Date: 2026-10-15 02:55:55.748622+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c290658f6031'
down_revision = '31f82c75c58d'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('cluster')
    op.drop_column('target', 'is_cluster')


def downgrade():
    # Recreate both as they were at 31f82c75c58d. The data is not restored.
    op.add_column('target', sa.Column('is_cluster', sa.Boolean(), nullable=True, comment='True if it is a cluster of multiple targets.'))
    op.create_table(
        'cluster',
        sa.Column('cluster_id', sa.BigInteger(), autoincrement=False, nullable=False, comment='Unique identifier of clusters found at duplication checking'),
        sa.Column('target_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('n_targets', sa.Integer(), nullable=True, comment='Number of targets in the cluster'),
        sa.Column('ra_cluster', sa.Float(), nullable=True, comment='Mean RA of targets in the cluster (ICRS, degree)'),
        sa.Column('dec_cluster', sa.Float(), nullable=True, comment='Mean Dec of targets in the cluster (ICRS, degree)'),
        sa.Column('d_ra', sa.Float(), nullable=True, comment='RA(target) - RA(cluster) (degree)'),
        sa.Column('d_dec', sa.Float(), nullable=True, comment='Dec(target) - Dec(cluster) (degree)'),
        sa.Column('input_catalog_id', sa.Integer(), nullable=True, comment='Input catalog ID from the input_catalog table'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"), nullable=True, comment='UTC'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, comment='UTC'),
        sa.ForeignKeyConstraint(['input_catalog_id'], ['input_catalog.input_catalog_id'], name='cluster_input_catalog_id_fkey'),
        sa.ForeignKeyConstraint(['target_id'], ['target.target_id'], name='cluster_target_id_fkey'),
        sa.PrimaryKeyConstraint('cluster_id', 'target_id', name='cluster_pkey'),
        sa.UniqueConstraint('cluster_id', 'target_id', name='cluster_cluster_id_target_id_key'),
    )
