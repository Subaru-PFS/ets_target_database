#!/usr/bin/env python3
"""Verify the initial database setup: q3c extension and table creation."""

from sqlalchemy import text

from targetdb import models


def test_q3c_extension_installed(engine, q3c_installed):
    with engine.connect() as conn:
        extnames = {row[0] for row in conn.execute(text("SELECT extname FROM pg_extension"))}
    assert "q3c" in extnames


def test_all_model_tables_created(engine, schema):
    with engine.connect() as conn:
        existing_tables = {
            row[0]
            for row in conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public'"
                )
            )
        }

    expected_tables = set(models.Base.metadata.tables.keys())
    missing = expected_tables - existing_tables
    assert not missing, f"Tables missing after create-schema: {sorted(missing)}"
