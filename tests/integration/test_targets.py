#!/usr/bin/env python3
"""
Verify transfer-targets + insert-targets: local data is fetched for every
catalog, and the resulting `target` rows match the transferred ECSV files
and reference valid input_catalog/proposal/target_type rows.
"""

import pandas as pd
import pytest
from sqlalchemy import text

from .conftest import TARGETS_DATA_DIR, count_rows, ecsv_row_count

INPUT_CATALOGS_CSV = TARGETS_DATA_DIR / "example_input_catalogs.csv"


@pytest.fixture(scope="module")
def catalogs_df():
    return pd.read_csv(INPUT_CATALOGS_CSV)


def test_transfer_targets_downloads_all_catalogs(target_data, catalogs_df):
    local_dir = target_data["local_dir"]
    for upload_id in catalogs_df["upload_id"]:
        matches = list(local_dir.glob(f"????????-??????-{upload_id}"))
        assert len(matches) == 1, (
            f"expected exactly one transferred data dir for upload_id={upload_id}, "
            f"got {matches}"
        )


def test_input_catalogs_registered_with_upload_id(engine, target_data, catalogs_df):
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT input_catalog_name, upload_id FROM input_catalog "
                "WHERE upload_id IS NOT NULL"
            )
        ).fetchall()
    registered = dict(rows)

    for _, row in catalogs_df.iterrows():
        assert registered.get(row["input_catalog_name"]) == row["upload_id"]


def test_target_row_count_matches_ecsv_inputs(engine, target_data):
    local_dir = target_data["local_dir"]
    total_expected = 0
    for upload_dir in sorted(local_dir.glob("????????-??????-*")):
        upload_id = upload_dir.name.split("-", 2)[2]
        total_expected += ecsv_row_count(upload_dir / f"target_{upload_id}.ecsv")

    assert count_rows(engine, "target") == total_expected


def test_targets_reference_valid_foreign_keys(engine, target_data):
    with engine.connect() as conn:
        orphan_catalog = conn.execute(
            text(
                "SELECT count(*) FROM target t "
                "LEFT JOIN input_catalog c ON t.input_catalog_id = c.input_catalog_id "
                "WHERE c.input_catalog_id IS NULL"
            )
        ).scalar_one()
        orphan_proposal = conn.execute(
            text(
                "SELECT count(*) FROM target t "
                "LEFT JOIN proposal p ON t.proposal_id = p.proposal_id "
                "WHERE t.proposal_id IS NOT NULL AND p.proposal_id IS NULL"
            )
        ).scalar_one()
        orphan_target_type = conn.execute(
            text(
                "SELECT count(*) FROM target t "
                "LEFT JOIN target_type tt ON t.target_type_id = tt.target_type_id "
                "WHERE t.target_type_id IS NOT NULL AND tt.target_type_id IS NULL"
            )
        ).scalar_one()

    assert orphan_catalog == 0
    assert orphan_proposal == 0
    assert orphan_target_type == 0
