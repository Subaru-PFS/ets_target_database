#!/usr/bin/env python3
"""Verify the master/reference tables inserted from examples/data/*.csv."""

import pytest
from sqlalchemy import text

from .conftest import EXAMPLES_DATA, MASTER_TABLE_FILES, count_rows, csv_row_count

# input_catalog receives an extra insert (input_catalog_fluxstd.csv) on top of
# input_catalogs.csv, so it is checked separately below rather than via the
# generic 1:1 CSV-to-table comparison.
SIMPLE_MASTER_TABLES = [
    (table, filename)
    for table, filename in MASTER_TABLE_FILES
    if table != "input_catalog"
]


@pytest.mark.parametrize("table, filename", SIMPLE_MASTER_TABLES)
def test_master_table_row_count(engine, master_data, table, filename):
    expected = csv_row_count(EXAMPLES_DATA / filename)
    assert count_rows(engine, table) == expected


def test_input_catalog_row_count(engine, master_data):
    expected = csv_row_count(EXAMPLES_DATA / "input_catalogs.csv") + csv_row_count(
        EXAMPLES_DATA / "input_catalog_fluxstd.csv"
    )
    assert count_rows(engine, "input_catalog") == expected


def test_fluxstd_input_catalog_registered(engine, master_data):
    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT input_catalog_name FROM input_catalog "
                "WHERE input_catalog_id = 3006"
            )
        ).fetchone()
    assert row is not None
    assert row[0] == "Fstar_v3.3"
