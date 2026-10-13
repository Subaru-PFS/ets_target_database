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

from targetdb import TargetDB
from targetdb.targetdb import scalar_column_defaults


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
