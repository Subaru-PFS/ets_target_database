#!/usr/bin/env python3
"""Verify insert-pointings only creates user_pointing rows for catalogs
flagged with is_user_pointing=True, and that the row count and catalog
linkage are correct."""

import pandas as pd
from sqlalchemy import text

from .conftest import TARGETS_DATA_DIR, count_rows, ecsv_row_count

INPUT_CATALOGS_CSV = TARGETS_DATA_DIR / "example_input_catalogs.csv"


def test_user_pointing_only_for_flagged_catalogs(engine, pointing_data, target_data):
    catalogs_df = pd.read_csv(INPUT_CATALOGS_CSV)
    flagged = catalogs_df[catalogs_df["is_user_pointing"]]
    not_flagged = catalogs_df[~catalogs_df["is_user_pointing"]]
    assert len(flagged) > 0, "test fixture data must include a user-pointing catalog"

    local_dir = target_data["local_dir"]

    with engine.connect() as conn:
        for _, row in flagged.iterrows():
            upload_dir = next(local_dir.glob(f"????????-??????-{row['upload_id']}"))
            expected = ecsv_row_count(upload_dir / f"ppc_{row['upload_id']}.ecsv")

            actual = conn.execute(
                text(
                    "SELECT count(*) FROM user_pointing up "
                    "JOIN input_catalog c ON up.input_catalog_id = c.input_catalog_id "
                    "WHERE c.upload_id = :upload_id"
                ),
                {"upload_id": row["upload_id"]},
            ).scalar_one()
            assert actual == expected

        for _, row in not_flagged.iterrows():
            actual = conn.execute(
                text(
                    "SELECT count(*) FROM user_pointing up "
                    "JOIN input_catalog c ON up.input_catalog_id = c.input_catalog_id "
                    "WHERE c.upload_id = :upload_id"
                ),
                {"upload_id": row["upload_id"]},
            ).scalar_one()
            assert actual == 0


def test_user_pointing_total_matches_flagged_catalogs(engine, pointing_data, target_data):
    catalogs_df = pd.read_csv(INPUT_CATALOGS_CSV)
    flagged = catalogs_df[catalogs_df["is_user_pointing"]]

    local_dir = target_data["local_dir"]
    total_expected = 0
    for _, row in flagged.iterrows():
        upload_dir = next(local_dir.glob(f"????????-??????-{row['upload_id']}"))
        total_expected += ecsv_row_count(upload_dir / f"ppc_{row['upload_id']}.ecsv")

    assert count_rows(engine, "user_pointing") == total_expected
