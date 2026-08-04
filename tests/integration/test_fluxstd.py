#!/usr/bin/env python3
"""Verify prep-fluxstd output and the resulting fluxstd table contents."""

import pandas as pd
from sqlalchemy import text

from .conftest import FLUXSTD_INPUT_DIR, count_rows

INPUT_FEATHER = FLUXSTD_INPUT_DIR / "ra354.8_354.9_dec-40.0_90.0.feather"


def test_prep_fluxstd_generates_output_files(fluxstd_data):
    assert fluxstd_data["files"], "expected at least one generated feather file"
    for f in fluxstd_data["files"]:
        assert f.exists()


def test_fluxstd_row_count_matches_input(engine, fluxstd_data):
    expected = len(pd.read_feather(INPUT_FEATHER))
    assert count_rows(engine, "fluxstd") == expected


def test_fluxstd_rows_tagged_with_catalog_and_version(engine, fluxstd_data):
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT DISTINCT input_catalog_id, version FROM fluxstd")
        ).fetchall()
    assert rows == [(3006, "3.3")]


def test_fluxstd_rename_cols_applied(fluxstd_data):
    df = pd.read_feather(fluxstd_data["files"][0])
    assert "is_fstar_gaia" in df.columns
    assert "fstar_gaia" not in df.columns
