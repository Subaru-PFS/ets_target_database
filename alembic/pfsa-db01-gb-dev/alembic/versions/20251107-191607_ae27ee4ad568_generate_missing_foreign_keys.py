"""generate missing foreign keys

Revision ID: ae27ee4ad568
Revises: ce8ac566901b
Create Date: 2025-11-07 19:16:07.094831

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "ae27ee4ad568"
down_revision = "ce8ac566901b"
branch_labels = None
depends_on = None


def upgrade():
    # Recreate foreign keys that were dropped by CASCADE in migration ce8ac566901b
    # These foreign keys reference primary keys instead of the redundant unique constraints

    # Foreign keys to input_catalog.input_catalog_id
    op.create_foreign_key(
        "cluster_input_catalog_id_fkey",
        "cluster",
        "input_catalog",
        ["input_catalog_id"],
        ["input_catalog_id"],
    )
    op.create_foreign_key(
        "fluxstd_input_catalog_id_fkey",
        "fluxstd",
        "input_catalog",
        ["input_catalog_id"],
        ["input_catalog_id"],
    )
    op.create_foreign_key(
        "sky_input_catalog_id_fkey",
        "sky",
        "input_catalog",
        ["input_catalog_id"],
        ["input_catalog_id"],
    )
    op.create_foreign_key(
        "target_input_catalog_id_fkey",
        "target",
        "input_catalog",
        ["input_catalog_id"],
        ["input_catalog_id"],
    )
    op.create_foreign_key(
        "user_pointing_input_catalog_id_fkey",
        "user_pointing",
        "input_catalog",
        ["input_catalog_id"],
        ["input_catalog_id"],
    )

    # Foreign keys from fluxstd to filter_name.filter_name
    op.create_foreign_key(
        "fluxstd_filter_g_fkey", "fluxstd", "filter_name", ["filter_g"], ["filter_name"]
    )
    op.create_foreign_key(
        "fluxstd_filter_r_fkey", "fluxstd", "filter_name", ["filter_r"], ["filter_name"]
    )
    op.create_foreign_key(
        "fluxstd_filter_i_fkey", "fluxstd", "filter_name", ["filter_i"], ["filter_name"]
    )
    op.create_foreign_key(
        "fluxstd_filter_z_fkey", "fluxstd", "filter_name", ["filter_z"], ["filter_name"]
    )
    op.create_foreign_key(
        "fluxstd_filter_y_fkey", "fluxstd", "filter_name", ["filter_y"], ["filter_name"]
    )
    op.create_foreign_key(
        "fluxstd_filter_j_fkey", "fluxstd", "filter_name", ["filter_j"], ["filter_name"]
    )

    # Foreign keys from target to filter_name.filter_name
    op.create_foreign_key(
        "target_filter_g_fkey", "target", "filter_name", ["filter_g"], ["filter_name"]
    )
    op.create_foreign_key(
        "target_filter_r_fkey", "target", "filter_name", ["filter_r"], ["filter_name"]
    )
    op.create_foreign_key(
        "target_filter_i_fkey", "target", "filter_name", ["filter_i"], ["filter_name"]
    )
    op.create_foreign_key(
        "target_filter_z_fkey", "target", "filter_name", ["filter_z"], ["filter_name"]
    )
    op.create_foreign_key(
        "target_filter_y_fkey", "target", "filter_name", ["filter_y"], ["filter_name"]
    )
    op.create_foreign_key(
        "target_filter_j_fkey", "target", "filter_name", ["filter_j"], ["filter_name"]
    )


def downgrade():
    # Drop the foreign keys created in upgrade()
    # Note: This downgrade would recreate the situation where foreign keys are missing
    # This should only be used if you need to rollback to the state after ce8ac566901b

    # Drop foreign keys from target to filter_name
    op.drop_constraint("target_filter_j_fkey", "target", type_="foreignkey")
    op.drop_constraint("target_filter_y_fkey", "target", type_="foreignkey")
    op.drop_constraint("target_filter_z_fkey", "target", type_="foreignkey")
    op.drop_constraint("target_filter_i_fkey", "target", type_="foreignkey")
    op.drop_constraint("target_filter_r_fkey", "target", type_="foreignkey")
    op.drop_constraint("target_filter_g_fkey", "target", type_="foreignkey")

    # Drop foreign keys from fluxstd to filter_name
    op.drop_constraint("fluxstd_filter_j_fkey", "fluxstd", type_="foreignkey")
    op.drop_constraint("fluxstd_filter_y_fkey", "fluxstd", type_="foreignkey")
    op.drop_constraint("fluxstd_filter_z_fkey", "fluxstd", type_="foreignkey")
    op.drop_constraint("fluxstd_filter_i_fkey", "fluxstd", type_="foreignkey")
    op.drop_constraint("fluxstd_filter_r_fkey", "fluxstd", type_="foreignkey")
    op.drop_constraint("fluxstd_filter_g_fkey", "fluxstd", type_="foreignkey")

    # Drop foreign keys to input_catalog
    op.drop_constraint(
        "user_pointing_input_catalog_id_fkey", "user_pointing", type_="foreignkey"
    )
    op.drop_constraint("target_input_catalog_id_fkey", "target", type_="foreignkey")
    op.drop_constraint("sky_input_catalog_id_fkey", "sky", type_="foreignkey")
    op.drop_constraint("fluxstd_input_catalog_id_fkey", "fluxstd", type_="foreignkey")
    op.drop_constraint("cluster_input_catalog_id_fkey", "cluster", type_="foreignkey")
