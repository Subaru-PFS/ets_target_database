"""add user_pointing table

Revision ID: b68482e38606
Revises: f07c300ae87f
Create Date: 2024-10-24 12:03:38.150098

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "b68482e38606"
down_revision = "f07c300ae87f"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user_pointing",
        sa.Column(
            "user_pointing_id",
            sa.BigInteger(),
            nullable=False,
            comment="Unique identifier for each user-defined pointing (autoincremented primary key)",
        ),
        sa.Column(
            "ppc_code",
            sa.String(),
            nullable=False,
            comment="String identifier of the pointing set either by the uploader or user",
        ),
        sa.Column(
            "ppc_ra",
            sa.Float(),
            nullable=False,
            comment="RA of the pointing center (ICRS, degree)",
        ),
        sa.Column(
            "ppc_dec",
            sa.Float(),
            nullable=False,
            comment="Dec of the pointing center (ICRS, degree)",
        ),
        sa.Column(
            "ppc_pa",
            sa.Float(),
            nullable=False,
            comment="Position angle of the pointing center (degree)",
        ),
        sa.Column(
            "ppc_resolution",
            sa.Enum("L", "M", name="resolutionmode"),
            nullable=False,
            comment="Resolution mode of the pointing ('L' or 'M')",
        ),
        sa.Column(
            "ppc_priority",
            sa.Float(),
            nullable=False,
            comment="Priority of the pointing calculated by the uploader",
        ),
        sa.Column(
            "input_catalog_id",
            sa.Integer(),
            nullable=False,
            comment="Input catalog ID from the input_catalog table",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=True,
            comment="The date and time in UTC when the record was created",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
            comment="The date and time in UTC when the record was last updated",
        ),
        sa.ForeignKeyConstraint(
            ["input_catalog_id"],
            ["input_catalog.input_catalog_id"],
        ),
        sa.PrimaryKeyConstraint("user_pointing_id"),
    )
    op.add_column(
        "input_catalog",
        sa.Column(
            "is_user_pointing",
            sa.Boolean(),
            nullable=True,
            comment="True if user-defined pointings are provided",
        ),
    )
    # op.drop_index('target_q3c_ang2ipix_idx1', table_name='target')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.create_index('target_q3c_ang2ipix_idx1', 'target', [sa.text('q3c_ang2ipix(ra, "dec")')], unique=False)
    op.drop_column("input_catalog", "is_user_pointing")
    op.drop_table("user_pointing")
    # ### end Alembic commands ###
