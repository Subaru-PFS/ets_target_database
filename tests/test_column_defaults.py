#!/usr/bin/env python
"""
Unit tests for applying the models' client-side `default=` values on insert.

`DB.insert_dataframe()` writes through PostgreSQL's COPY, which never sees the
SQLAlchemy models, so their `default=` values have to be applied to the
DataFrame explicitly. None of these tests need a database; what COPY actually
stores is covered by `tests/integration/test_column_defaults.py`.
"""

import numpy as np
import pandas as pd
import pytest

from targetdb import TargetDB
from targetdb.targetdb import scalar_column_defaults
from targetdb.utils import add_database_rows, fill_null_with_defaults


def test_scalar_column_defaults_lists_model_defaults():
    defaults = scalar_column_defaults("target")
    assert defaults["epoch"] == "J2000.0"
    assert defaults["single_exptime"] == 900
    assert defaults["is_cluster"] is False
    assert "ra" not in defaults
    # server_default is applied by the database, not a client-side default.
    assert "created_at" not in defaults


def test_scalar_column_defaults_is_empty_without_defaults():
    assert scalar_column_defaults("cluster") == {}


def test_fill_absent_columns_adds_missing_defaults():
    df = pd.DataFrame({"proposal_id": ["S99A-X1"], "allocated_time_total": [np.nan]})

    out = TargetDB._fill_absent_columns_with_defaults("proposal", df)

    assert out["is_too"].tolist() == [False]
    assert out["allocated_time_lr"].tolist() == [0.0]
    assert out["pi_first_name"].tolist() == [""]
    # Present columns are left alone, nulls included.
    assert np.isnan(out["allocated_time_total"].iloc[0])
    # The caller's DataFrame is not modified.
    assert list(df.columns) == ["proposal_id", "allocated_time_total"]


def test_fill_absent_columns_returns_input_when_nothing_is_absent():
    df = pd.DataFrame({"cluster_id": [1]})
    assert TargetDB._fill_absent_columns_with_defaults("cluster", df) is df


def test_insert_hands_defaults_to_insert_dataframe(monkeypatch):
    captured = {}

    def fake_insert_dataframe(self, table, df, **kwargs):
        captured["table"] = table
        captured["df"] = df
        return len(df)

    monkeypatch.setattr(TargetDB, "insert_dataframe", fake_insert_dataframe)
    db = TargetDB(host="localhost", port=5432, dbname="x", user="u", password="p")
    df = pd.DataFrame(
        {
            "ob_code": ["a"],
            "obj_id": [1],
            "ra": [0.0],
            "dec": [0.0],
            "input_catalog_id": [10000],
            "effective_exptime": [900.0],
            "target_type_name": ["SCIENCE"],
        }
    )

    db.insert("target", df)

    out = captured["df"]
    assert captured["table"] == "target"
    assert "target_type_name" not in out.columns
    assert out["single_exptime"].tolist() == [900]
    assert out["epoch"].tolist() == ["J2000.0"]


def test_fill_null_replaces_nan_none_na_and_empty_string():
    df = pd.DataFrame(
        {
            "epoch": ["J2016.0", "", None],
            "pmra": [1.5, np.nan, np.nan],
            # A CSV column with blanks, read with keep_default_na=False.
            "priority": ["2", "", "3"],
            "is_cluster": pd.array([True, pd.NA, False], dtype="boolean"),
            "single_exptime": pd.array([1800, pd.NA, 900], dtype="Int64"),
        }
    )

    out = fill_null_with_defaults(df, "target")

    assert out["epoch"].tolist() == ["J2016.0", "J2000.0", "J2000.0"]
    assert out["pmra"].tolist() == [1.5, 0.0, 0.0]
    assert out["priority"].tolist() == ["2", 1.0, "3"]
    assert out["is_cluster"].tolist() == [True, False, False]
    assert out["single_exptime"].tolist() == [1800, 900, 900]


def test_fill_null_keeps_real_falsy_values():
    df = pd.DataFrame(
        {
            "pmra": [0.0, -2.0],
            "is_medium_resolution": [False, True],
            "priority": [0.0, 5.0],
        }
    )

    out = fill_null_with_defaults(df, "target")

    pd.testing.assert_frame_equal(out, df)


def test_fill_null_skips_empty_string_defaults():
    df = pd.DataFrame(
        {
            "input_catalog_name": ["a", "b"],
            "upload_id": ["", None],
            "input_catalog_description": ["", "x"],
            "active": [None, False],
        }
    )

    out = fill_null_with_defaults(df, "input_catalog")

    assert out["upload_id"].tolist() == ["", None]
    assert out["input_catalog_description"].tolist() == ["", "x"]
    assert out["active"].tolist() == [True, False]


def test_fill_null_handles_pandas_string_dtype():
    df = pd.DataFrame({"epoch": pd.array(["J2016.0", pd.NA, ""], dtype="string")})

    out = fill_null_with_defaults(df, "target")

    assert out["epoch"].tolist() == ["J2016.0", "J2000.0", "J2000.0"]


def test_fill_null_does_not_add_absent_columns():
    df = pd.DataFrame({"ob_code": ["a"]})
    assert list(fill_null_with_defaults(df, "target").columns) == ["ob_code"]


def test_fill_null_does_not_modify_input():
    df = pd.DataFrame({"pmra": [np.nan]})
    fill_null_with_defaults(df, "target")
    assert np.isnan(df["pmra"].iloc[0])


CONFIG = {
    "targetdb": {
        "db": {
            "host": "localhost",
            "port": 5432,
            "dbname": "x",
            "user": "u",
            "password": "p",
            "dialect": "postgresql",
        }
    }
}


@pytest.fixture
def captured_writes(monkeypatch):
    """Record what add_database_rows() hands to TargetDB, without a database."""
    calls = []
    monkeypatch.setattr("targetdb.utils.add_backref_values", lambda df, **kw: df)
    monkeypatch.setattr(
        TargetDB,
        "insert",
        lambda self, table, df, dry_run=False: calls.append(("insert", table, df)),
    )
    monkeypatch.setattr(
        TargetDB,
        "update",
        lambda self, table, df, dry_run=False: calls.append(("update", table, df)),
    )
    return calls


def test_add_database_rows_fills_nulls_on_insert(captured_writes):
    df = pd.DataFrame({"obj_id": [1, 2], "epoch": ["J2016.0", ""]})

    add_database_rows(config=CONFIG, df=df, table="fluxstd", insert=True)

    ((kind, _, written),) = captured_writes
    assert kind == "insert"
    assert written["epoch"].tolist() == ["J2016.0", "J2000.0"]


def test_add_database_rows_leaves_nulls_on_update(captured_writes):
    df = pd.DataFrame({"fluxstd_id": [1, 2], "epoch": ["J2016.0", ""]})

    add_database_rows(config=CONFIG, df=df, table="fluxstd", update=True)

    ((kind, _, written),) = captured_writes
    assert kind == "update"
    assert written["epoch"].tolist() == ["J2016.0", ""]
