#!/usr/bin/env python3
"""
Prove the `--commit` contract against a real PostgreSQL server.

The CLI defaults to `--commit False`, so every write path has to roll back
unless the flag is passed. Since `TargetDB` moved onto
`pfs.utils.database.db.DB` that guarantee rests on two things only a live
server can demonstrate:

* `TargetDB.connection()` opens its transaction eagerly, because
  `pandas.DataFrame.to_sql` starts *and commits* one of its own when handed a
  connection that is not already in a transaction, and
* the `COPY` fast path (`_psql_insert_copy`) writes through a raw psycopg
  cursor, so it has to be enrolled in that same transaction to be undone.

Every test here restores the database before it returns: the fixtures in
conftest.py are session-scoped and other modules assert exact row counts on
them.
"""

import pandas as pd
import pytest
from sqlalchemy import text

from targetdb import TargetDB
from targetdb.utils import load_config

from .conftest import EXAMPLES_DATA, count_rows, run_cli

PROPOSAL_CSV = EXAMPLES_DATA / "proposals.csv"
# Prefix used by the rows these tests create, so cleanup can find them.
PROBE_PREFIX = "ZZZ-DRYRUN"
TARGET_CATALOG_ID = 1004


@pytest.fixture
def probe_proposals(master_data, engine, tmp_path):
    """A CSV of proposals that do not exist yet, removed again afterwards.

    Re-inserting the example rows would fail on the primary key inside COPY
    itself, which says nothing about whether the transaction was committed.
    """
    df = pd.read_csv(PROPOSAL_CSV).head(2).copy()
    df["proposal_id"] = [f"{PROBE_PREFIX}-{i}" for i in range(len(df))]
    df["group_id"] = [f"o99{i:03d}" for i in range(len(df))]
    csv_path = tmp_path / "probe_proposals.csv"
    df.to_csv(csv_path, index=False)

    yield csv_path, len(df)

    with engine.connect() as conn:
        conn.execute(
            text("DELETE FROM proposal WHERE proposal_id LIKE :p"),
            {"p": f"{PROBE_PREFIX}%"},
        )
        conn.commit()


def read_active_flag(engine, input_catalog_id):
    with engine.connect() as conn:
        return conn.execute(
            text("SELECT active FROM input_catalog WHERE input_catalog_id = :i"),
            {"i": input_catalog_id},
        ).scalar_one()


def test_insert_without_commit_writes_nothing(engine, db_config, probe_proposals):
    """The raw-cursor COPY write must be rolled back with the transaction."""
    csv_path, _ = probe_proposals
    before = count_rows(engine, "proposal")

    run_cli("insert", csv_path, "-c", db_config, "-t", "proposal")

    assert count_rows(engine, "proposal") == before


def test_insert_with_commit_writes_rows(engine, db_config, probe_proposals):
    csv_path, n_rows = probe_proposals
    before = count_rows(engine, "proposal")

    run_cli("insert", csv_path, "-c", db_config, "-t", "proposal", "--commit")

    assert count_rows(engine, "proposal") == before + n_rows


def test_update_without_commit_changes_nothing(engine, master_data, db_config):
    before = read_active_flag(engine, TARGET_CATALOG_ID)

    run_cli(
        "update-catalog-active", TARGET_CATALOG_ID, str(not before), "-c", db_config
    )

    assert read_active_flag(engine, TARGET_CATALOG_ID) == before


def test_update_with_commit_changes_the_value(engine, master_data, db_config):
    before = read_active_flag(engine, TARGET_CATALOG_ID)
    flipped = not before

    run_cli(
        "update-catalog-active",
        TARGET_CATALOG_ID,
        str(flipped),
        "-c",
        db_config,
        "--commit",
    )
    assert read_active_flag(engine, TARGET_CATALOG_ID) == flipped

    # Restore, so this module leaves the session fixtures as it found them.
    run_cli(
        "update-catalog-active",
        TARGET_CATALOG_ID,
        str(before),
        "-c",
        db_config,
        "--commit",
    )
    assert read_active_flag(engine, TARGET_CATALOG_ID) == before


def test_execute_query_honours_dry_run(engine, master_data, db_config):
    """execute_query() delegates to DB.commit(), which goes through
    connection() -- the single place the dry-run decision is made."""
    config = load_config(str(db_config))

    with engine.connect() as conn:
        before = conn.execute(
            text(
                "SELECT count(*) FROM proposal_category WHERE proposal_category_name = 'dry-run probe'"
            )
        ).scalar_one()
    assert before == 0

    with TargetDB(**config["targetdb"]["db"]) as db:
        db.execute_query(
            "UPDATE proposal_category SET proposal_category_name = 'dry-run probe'",
            dry_run=True,
        )

    with engine.connect() as conn:
        after = conn.execute(
            text(
                "SELECT count(*) FROM proposal_category WHERE proposal_category_name = 'dry-run probe'"
            )
        ).scalar_one()
    assert after == 0
