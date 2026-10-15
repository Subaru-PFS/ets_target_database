#!/usr/bin/env python3
"""
Model defaults reach the database through the COPY insert path.

Since TargetDB moved onto pfs.utils.database.db.DB, inserts go through
PostgreSQL's COPY, which knows nothing about the SQLAlchemy models'
client-side `default=` values. These tests insert through the CLI with the
defaulted columns left out entirely and with blank cells, then read back what
was stored.

Every row created here, including the probe input catalog, is deleted again:
the fixtures in conftest.py are session-scoped and other modules assert exact
row counts on them. For the same reason this module depends on master_data
only, not target_data, which would load the example targets early.
"""

import pandas as pd
import pytest
from sqlalchemy import text

from .conftest import run_cli

PROBE_PROPOSAL = "ZZZ-DEFAULTS-1"
PROBE_OB_PREFIX = "zzz_defaults_"
PROBE_CATALOG = "zzz_defaults_catalog"
# Explicit and outside the Identity range, so the sequence is not advanced.
PROBE_CATALOG_ID = 99990

EXPECTED_TARGET_DEFAULTS = {
    "epoch": "J2000.0",
    "parallax": 1e-7,
    "pmra": 0.0,
    "pmdec": 0.0,
    "target_type_id": 1,
    "priority": 1.0,
    "single_exptime": 900.0,
    "is_medium_resolution": False,
    "qa_relative_throughput": 1.0,
    "qa_relative_noise": 1.0,
}


def fetch_row(engine, sql, **params):
    with engine.connect() as conn:
        return dict(conn.execute(text(sql), params).mappings().one())


@pytest.fixture(scope="module")
def inserted_with_defaults(master_data, engine, db_config, tmp_path_factory):
    work = tmp_path_factory.mktemp("column-defaults")

    catalog_csv = work / "input_catalog.csv"
    pd.DataFrame(
        {
            "input_catalog_id": [PROBE_CATALOG_ID],
            "input_catalog_name": [PROBE_CATALOG],
            "upload_id": ["zzzdefaults00001"],
        }
    ).to_csv(catalog_csv, index=False)

    # Every defaulted proposal column left out.
    proposal_csv = work / "proposal.csv"
    pd.DataFrame(
        {
            "proposal_id": [PROBE_PROPOSAL],
            "group_id": ["o99999"],
            "pi_last_name": ["Probe"],
            "rank": [5.0],
            "grade": ["A"],
            "proposal_category_name": ["openuse"],
            "partner_name": ["subaru"],
        }
    ).to_csv(proposal_csv, index=False)

    common = {
        "proposal_id": PROBE_PROPOSAL,
        "input_catalog_name": PROBE_CATALOG,
        "target_type_name": "SCIENCE",
        "ra": 150.0,
        "dec": 2.0,
        "effective_exptime": 3600.0,
    }

    # Every defaulted target column left out, single_exptime (NOT NULL) included.
    absent_csv = work / "targets_absent.csv"
    pd.DataFrame(
        [{**common, "ob_code": f"{PROBE_OB_PREFIX}absent", "obj_id": 1}]
    ).to_csv(absent_csv, index=False)

    # Defaulted columns present: one row filled in, one left blank.
    blank_csv = work / "targets_blank.csv"
    pd.DataFrame(
        [
            {
                **common,
                "ob_code": f"{PROBE_OB_PREFIX}given",
                "obj_id": 2,
                "single_exptime": 1800,
                "epoch": "J2016.0",
                "parallax": 0.5,
                "pmra": 1.2,
                "pmdec": -3.4,
                "priority": 5.0,
                "is_medium_resolution": True,
            },
            {
                **common,
                "ob_code": f"{PROBE_OB_PREFIX}blank",
                "obj_id": 3,
                "single_exptime": None,
                "epoch": None,
                "parallax": None,
                "pmra": None,
                "pmdec": None,
                "priority": None,
                "is_medium_resolution": None,
            },
        ]
    ).to_csv(blank_csv, index=False)

    try:
        for table, path in [
            ("input_catalog", catalog_csv),
            ("proposal", proposal_csv),
            ("target", absent_csv),
            ("target", blank_csv),
        ]:
            run_cli("insert", path, "-c", db_config, "-t", table, "--commit")
        yield
    finally:
        with engine.connect() as conn:
            conn.execute(
                text("DELETE FROM target WHERE proposal_id = :p"), {"p": PROBE_PROPOSAL}
            )
            conn.execute(
                text("DELETE FROM proposal WHERE proposal_id = :p"),
                {"p": PROBE_PROPOSAL},
            )
            conn.execute(
                text("DELETE FROM input_catalog WHERE input_catalog_id = :c"),
                {"c": PROBE_CATALOG_ID},
            )
            conn.commit()


def test_proposal_absent_columns_get_defaults(engine, inserted_with_defaults):
    row = fetch_row(
        engine,
        "SELECT pi_first_name, pi_middle_name, allocated_time_total, "
        "allocated_time_lr, allocated_time_mr, is_too "
        "FROM proposal WHERE proposal_id = :p",
        p=PROBE_PROPOSAL,
    )

    assert row["allocated_time_total"] == 0.0
    assert row["allocated_time_lr"] == 0.0
    assert row["allocated_time_mr"] == 0.0
    assert row["is_too"] is False
    # COPY stores a "" default as NULL; either is fine for these columns.
    assert row["pi_first_name"] in ("", None)
    assert row["pi_middle_name"] in ("", None)


@pytest.mark.parametrize("ob_suffix", ["absent", "blank"])
def test_target_defaults_are_stored(engine, inserted_with_defaults, ob_suffix):
    columns = ", ".join(EXPECTED_TARGET_DEFAULTS)
    row = fetch_row(
        engine,
        f"SELECT {columns} FROM target WHERE ob_code = :o",
        o=f"{PROBE_OB_PREFIX}{ob_suffix}",
    )

    assert row == EXPECTED_TARGET_DEFAULTS


def test_target_given_values_are_kept(engine, inserted_with_defaults):
    row = fetch_row(
        engine,
        "SELECT single_exptime, epoch, parallax, pmra, pmdec, priority, "
        "is_medium_resolution FROM target WHERE ob_code = :o",
        o=f"{PROBE_OB_PREFIX}given",
    )

    assert row == {
        "single_exptime": 1800.0,
        "epoch": "J2016.0",
        "parallax": 0.5,
        "pmra": 1.2,
        "pmdec": -3.4,
        "priority": 5.0,
        "is_medium_resolution": True,
    }
