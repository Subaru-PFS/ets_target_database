"""set default to created_at

Revision ID: 8f188c3cb652
Revises: f8bacfde2cef
Create Date: 2024-05-02 11:29:46.318970

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "8f188c3cb652"
down_revision = "f8bacfde2cef"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "cluster",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
        existing_comment="UTC",
        existing_nullable=True,
    )
    op.alter_column(
        "filter_name",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
        existing_comment="The date and time in UTC when the record was created",
        existing_nullable=True,
    )
    op.alter_column(
        "fluxstd",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
        existing_comment="The date and time in UTC when the record was created",
        existing_nullable=True,
    )
    op.alter_column(
        "input_catalog",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
        existing_comment="The date and time in UTC when the record was created",
        existing_nullable=True,
    )
    op.alter_column(
        "proposal",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
        existing_comment="The date and time in UTC when the record was created",
        existing_nullable=True,
    )
    op.alter_column(
        "proposal_category",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
        existing_comment="The date and time in UTC when the record was created",
        existing_nullable=True,
    )
    op.alter_column(
        "sky",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
        existing_comment="The date and time in UTC when the record was created",
        existing_nullable=True,
    )
    op.alter_column(
        "target",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
        existing_comment="The date and time in UTC when the record was created",
        existing_nullable=True,
    )
    op.alter_column(
        "target_type",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
        existing_comment="The date and time in UTC when the record was created",
        existing_nullable=True,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "target_type",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        server_default=None,
        existing_comment="The date and time in UTC when the record was created",
        existing_nullable=True,
    )
    op.alter_column(
        "target",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        server_default=None,
        existing_comment="The date and time in UTC when the record was created",
        existing_nullable=True,
    )
    op.alter_column(
        "sky",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        server_default=None,
        existing_comment="The date and time in UTC when the record was created",
        existing_nullable=True,
    )
    op.alter_column(
        "proposal_category",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        server_default=None,
        existing_comment="The date and time in UTC when the record was created",
        existing_nullable=True,
    )
    op.alter_column(
        "proposal",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        server_default=None,
        existing_comment="The date and time in UTC when the record was created",
        existing_nullable=True,
    )
    op.alter_column(
        "input_catalog",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        server_default=None,
        existing_comment="The date and time in UTC when the record was created",
        existing_nullable=True,
    )
    op.alter_column(
        "fluxstd",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        server_default=None,
        existing_comment="The date and time in UTC when the record was created",
        existing_nullable=True,
    )
    op.alter_column(
        "filter_name",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        server_default=None,
        existing_comment="The date and time in UTC when the record was created",
        existing_nullable=True,
    )
    op.alter_column(
        "cluster",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        server_default=None,
        existing_comment="UTC",
        existing_nullable=True,
    )
    # ### end Alembic commands ###
