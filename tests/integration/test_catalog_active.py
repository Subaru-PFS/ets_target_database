#!/usr/bin/env python3
"""Verify update-catalog-active only changes the targeted input_catalog row."""

from sqlalchemy import text

from .conftest import run_cli

TARGET_CATALOG_ID = 1004


def _read_active_flags(engine):
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT input_catalog_id, active FROM input_catalog"))
        return dict(rows.all())


def test_update_catalog_active_only_affects_target_row(engine, master_data, db_config):
    before = _read_active_flags(engine)
    assert TARGET_CATALOG_ID in before, (
        f"expected input_catalog_id={TARGET_CATALOG_ID} from examples/data/input_catalogs.csv"
    )

    run_cli(
        "update-catalog-active",
        TARGET_CATALOG_ID,
        "true",
        "-c",
        db_config,
        "--verbose",
        "--commit",
    )

    after = _read_active_flags(engine)

    assert after[TARGET_CATALOG_ID] is True

    unaffected_before = {k: v for k, v in before.items() if k != TARGET_CATALOG_ID}
    unaffected_after = {k: v for k, v in after.items() if k != TARGET_CATALOG_ID}
    assert unaffected_after == unaffected_before
