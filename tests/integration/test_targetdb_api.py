#!/usr/bin/env python3
"""
Exercise the `TargetDB` public API the way downstream packages call it.

`ets_pointing` and `pfs_obsproc_planning_tools` use `connect()` / `close()` /
`fetch_query()` / `fetch_all()` / `fetch_by_id()` and discard what `connect()`
returns. Reproducing that shape here keeps the contract under test inside this
repository, without needing either package installed.
"""

import pandas as pd
import pytest
from sqlalchemy import create_engine, text

from targetdb import TargetDB, models
from targetdb.utils import get_url_object, load_config


@pytest.fixture
def db(db_config, master_data):
    config = load_config(str(db_config))
    database = TargetDB(**config["targetdb"]["db"])
    yield database
    database.close()


def test_downstream_call_sequence(db):
    """The exact shape used in the downstream dbutils.py modules."""
    db.connect()  # return value deliberately discarded
    df = db.fetch_query("SELECT * FROM proposal")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    db.close()


def test_connect_does_not_leak_a_connection(db):
    """DB.connect() checks a connection out of the pool and hands it over; the
    override must not, since every caller throws the return value away."""
    db.connect()
    assert db.engine.pool.checkedout() == 0


def test_query_methods_return_connections_to_the_pool(db):
    db.connect()
    db.fetch_query("SELECT 1")
    db.fetch_all("proposal")
    db.fetch_by_id("proposal", proposal_id="S21B-EN01")
    assert db.engine.pool.checkedout() == 0


def test_close_releases_server_side_connections(db, db_config):
    """Without this, `drop-db` fails with "database is being accessed by other
    users"."""
    db.connect()
    db.fetch_query("SELECT 1")

    config = load_config(str(db_config))
    dbname = config["targetdb"]["db"]["dbname"]
    # A separate engine, so counting does not observe its own connection as one
    # of TargetDB's.
    observer = create_engine(get_url_object(config))
    try:
        with observer.connect() as conn:
            before = conn.execute(
                text(
                    "SELECT count(*) FROM pg_stat_activity "
                    "WHERE datname = :d AND pid <> pg_backend_pid()"
                ),
                {"d": dbname},
            ).scalar_one()
        assert before >= 1

        db.close()

        with observer.connect() as conn:
            after = conn.execute(
                text(
                    "SELECT count(*) FROM pg_stat_activity "
                    "WHERE datname = :d AND pid <> pg_backend_pid()"
                ),
                {"d": dbname},
            ).scalar_one()
        assert after == before - 1
    finally:
        observer.dispose()


def test_engine_is_reusable_after_close(db):
    """Engine.dispose() replaces the pool rather than invalidating the engine,
    so the instance cached in pfs.utils.database.db._DB_ENGINES stays usable."""
    db.connect()
    db.close()
    assert not db.fetch_all("proposal").empty


def test_fetch_all_column_names_and_order_match_the_model(db):
    """join_backref_values() merges these results into user DataFrames, so a
    renamed or reordered column would break things silently."""
    df = db.fetch_all("proposal")
    expected = list(models.proposal.__table__.columns.keys())
    assert list(df.columns) == expected


@pytest.mark.parametrize("table", ["proposal", "input_catalog", "target_type"])
def test_fetch_all_matches_a_direct_count(db, engine, table):
    from .conftest import count_rows

    assert len(db.fetch_all(table)) == count_rows(engine, table)


def test_fetch_by_id_filters_on_every_keyword(db):
    df = db.fetch_by_id("proposal", proposal_id="S21B-EN01")
    assert len(df) == 1
    assert df["proposal_id"].iloc[0] == "S21B-EN01"

    assert db.fetch_by_id("proposal", proposal_id="does-not-exist").empty

    # Two keywords must be ANDed, not the last one winning.
    assert db.fetch_by_id(
        "proposal", proposal_id="S21B-EN01", pi_last_name="Nobody"
    ).empty


def test_fetch_by_id_columns_match_fetch_all(db):
    assert list(db.fetch_by_id("proposal", proposal_id="S21B-EN01").columns) == list(
        db.fetch_all("proposal").columns
    )


def test_context_manager_closes_the_engine(db_config, master_data):
    config = load_config(str(db_config))
    with TargetDB(**config["targetdb"]["db"]) as database:
        assert not database.fetch_all("proposal").empty
    assert database.engine.pool.checkedout() == 0
