"""remove redundant unique constraint from primary keys

Revision ID: ce8ac566901b
Revises: 89865530fdf1
Create Date: 2025-11-07 15:06:45.280873

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "ce8ac566901b"
down_revision = "89865530fdf1"
branch_labels = None
depends_on = None


def upgrade():
    # Remove redundant unique constraints on primary key columns
    # These constraints are unnecessary because primary keys already guarantee uniqueness
    # and have their own indexes.
    #
    # Note: Some of these unique constraints may be referenced by foreign keys.
    # PostgreSQL foreign keys can reference either unique constraints or primary keys.
    # When we drop a unique constraint that's referenced by a foreign key with CASCADE,
    # the dependent foreign keys are automatically dropped.
    # IMPORTANT: CASCADE does NOT automatically recreate these foreign keys.
    # They must be manually recreated (see migration ae27ee4ad568).

    # Drop constraints that are NOT referenced by foreign keys
    op.drop_constraint(op.f("sky_sky_id_key"), "sky", type_="unique")
    op.drop_constraint(op.f("fluxstd_fluxstd_id_key"), "fluxstd", type_="unique")
    op.drop_constraint(op.f("target_target_id_key"), "target", type_="unique")

    # These constraints ARE referenced by foreign keys, so we use raw SQL with CASCADE
    # CASCADE will drop the dependent foreign keys (they are recreated in migration ae27ee4ad568)
    op.execute("ALTER TABLE pfs_arm DROP CONSTRAINT IF EXISTS pfs_arm_name_key CASCADE")
    op.execute(
        "ALTER TABLE proposal DROP CONSTRAINT IF EXISTS proposal_proposal_id_key CASCADE"
    )
    op.execute(
        "ALTER TABLE proposal_category DROP CONSTRAINT IF EXISTS proposal_category_proposal_category_id_key CASCADE"
    )
    op.execute(
        "ALTER TABLE input_catalog DROP CONSTRAINT IF EXISTS input_catalog_input_catalog_id_key CASCADE"
    )
    op.execute(
        "ALTER TABLE partner DROP CONSTRAINT IF EXISTS partner_partner_id_key CASCADE"
    )
    op.execute(
        "ALTER TABLE target_type DROP CONSTRAINT IF EXISTS target_type_target_type_id_key CASCADE"
    )
    op.execute(
        "ALTER TABLE filter_name DROP CONSTRAINT IF EXISTS filter_name_filter_name_key CASCADE"
    )

    # Recreate one of the foreign keys that was dropped by CASCADE
    # Note: This is incomplete - 17 foreign keys were dropped but only 1 is recreated here.
    # The remaining 16 foreign keys are recreated in migration ae27ee4ad568.
    op.create_foreign_key(
        "target_qa_reference_arm_fkey",
        "target",
        "pfs_arm",
        ["qa_reference_arm"],
        ["name"],
    )


def downgrade():
    # Recreate the redundant unique constraints
    # First drop the foreign key that we recreated in upgrade()
    op.drop_constraint("target_qa_reference_arm_fkey", "target", type_="foreignkey")

    # Recreate unique constraints
    op.create_unique_constraint(
        op.f("filter_name_filter_name_key"),
        "filter_name",
        ["filter_name"],
        postgresql_nulls_not_distinct=False,
    )
    op.create_unique_constraint(
        op.f("target_type_target_type_id_key"),
        "target_type",
        ["target_type_id"],
        postgresql_nulls_not_distinct=False,
    )
    op.create_unique_constraint(
        op.f("partner_partner_id_key"),
        "partner",
        ["partner_id"],
        postgresql_nulls_not_distinct=False,
    )
    op.create_unique_constraint(
        op.f("input_catalog_input_catalog_id_key"),
        "input_catalog",
        ["input_catalog_id"],
        postgresql_nulls_not_distinct=False,
    )
    op.create_unique_constraint(
        op.f("proposal_category_proposal_category_id_key"),
        "proposal_category",
        ["proposal_category_id"],
        postgresql_nulls_not_distinct=False,
    )
    op.create_unique_constraint(
        op.f("pfs_arm_name_key"),
        "pfs_arm",
        ["name"],
        postgresql_nulls_not_distinct=False,
    )
    op.create_unique_constraint(
        op.f("proposal_proposal_id_key"),
        "proposal",
        ["proposal_id"],
        postgresql_nulls_not_distinct=False,
    )
    op.create_unique_constraint(
        op.f("target_target_id_key"),
        "target",
        ["target_id"],
        postgresql_nulls_not_distinct=False,
    )
    op.create_unique_constraint(
        op.f("fluxstd_fluxstd_id_key"),
        "fluxstd",
        ["fluxstd_id"],
        postgresql_nulls_not_distinct=False,
    )
    op.create_unique_constraint(
        op.f("sky_sky_id_key"), "sky", ["sky_id"], postgresql_nulls_not_distinct=False
    )

    # Recreate the foreign key that will now reference the unique constraint
    op.create_foreign_key(
        "target_qa_reference_arm_fkey",
        "target",
        "pfs_arm",
        ["qa_reference_arm"],
        ["name"],
    )
