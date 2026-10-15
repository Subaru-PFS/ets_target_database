"""set server defaults matching the model defaults

Revision ID: 03091e870c70
Revises: c290658f6031
Create Date: 2026-10-15 04:30:32.493866+00:00

SET DEFAULT only changes the catalog: no table is rewritten and existing rows
keep their values, so this is instant even on target, fluxstd and sky. Each
ALTER still needs an ACCESS EXCLUSIVE lock, though, and while it waits behind
a long-running query every new query on that table queues behind it. The
lock_timeout makes the migration fail fast instead; it rolls back as a whole
and can simply be run again.

Columns whose model default is "" are left without a server default on
purpose: COPY stores "" as NULL, so a '' default would only make an omitted
column differ from a blank one.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03091e870c70'
down_revision = 'c290658f6031'
branch_labels = None
depends_on = None


# The DEFAULT expressions, as SQL, matching models.with_default() at this revision.
SERVER_DEFAULTS = {
    'input_catalog': {
        'active': 'true',
        'is_classical': 'false',
        'is_user_pointing': 'false',
    },
    'proposal': {
        'allocated_time_total': '0.0',
        'allocated_time_lr': '0.0',
        'allocated_time_mr': '0.0',
        'is_too': 'false',
    },
    'target': {
        'epoch': "'J2000.0'",
        'parallax': '1e-07',
        'pmra': '0.0',
        'pmdec': '0.0',
        'target_type_id': '1',
        'priority': '1.0',
        'single_exptime': '900',
        'is_medium_resolution': 'false',
        'qa_relative_throughput': '1.0',
        'qa_relative_noise': '1.0',
    },
    'fluxstd': {
        'epoch': "'J2000.0'",
        'parallax': '1e-07',
        'pmra': '0.0',
        'pmdec': '0.0',
        'target_type_id': '3',
        'is_fstar_gaia': 'false',
        'is_gc_neighbor': 'false',
        'is_dense_region': 'false',
    },
    'sky': {
        'epoch': "'J2000.0'",
        'target_type_id': '2',
    },
}


def upgrade():
    op.execute("SET LOCAL lock_timeout = '10s'")
    for table, columns in SERVER_DEFAULTS.items():
        for column, default in columns.items():
            op.alter_column(table, column, server_default=sa.text(default))


def downgrade():
    op.execute("SET LOCAL lock_timeout = '10s'")
    for table, columns in SERVER_DEFAULTS.items():
        for column in columns:
            op.alter_column(table, column, server_default=None)
