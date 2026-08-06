#!/usr/bin/env python3
"""
Check that the alembic `env.py` scripts build their URL from TARGETDB_CONF.

Only `alembic/local_test/` is exercised, and only against the throwaway
container -- never a deployment target. `alembic current` is enough: it opens a
connection using the URL `env.py` assembled, which is exactly the part that
changed. No upgrade is attempted.

These tests assert on the connection, not on alembic's exit status.
`local_test`'s revision history is broken independently of any of this:
`80f8276e2ee7` names a `down_revision` (`ecfad41204d1`) that is not in the
repository, so alembic raises `KeyError` once it walks the revision map --
after the database connection has already been made.

The no-TARGETDB_CONF fallback to `alembic.ini` is covered by
`tests/test_targetdb.py::TestGetAlembicUrl`, which needs no server.
"""

import os
import subprocess
import sys

import pytest

from targetdb.utils import load_config

from .conftest import REPO_ROOT

ALEMBIC_DIR = REPO_ROOT / "alembic" / "local_test"


def run_alembic(*args, env=None):
    return subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=ALEMBIC_DIR,
        env={**os.environ, **(env or {})},
        capture_output=True,
        text=True,
    )


@pytest.fixture
def alembic_ini_exists():
    if not (ALEMBIC_DIR / "alembic.ini").exists():
        pytest.skip(f"no alembic.ini in {ALEMBIC_DIR}")


def test_current_connects_via_targetdb_conf(db_config, schema, alembic_ini_exists):
    """env.py must reach the container using only the URL built from the TOML.

    "Context impl PostgresqlImpl" is logged from context.configure(), which
    run_migrations_online() only reaches once connectable.connect() has
    succeeded -- so it is proof the connection was made.
    """
    result = run_alembic("current", env={"TARGETDB_CONF": str(db_config)})
    combined = result.stdout + result.stderr

    assert "Context impl PostgresqlImpl" in combined, combined
    for failure in [
        "password authentication failed",
        "could not connect",
        "OperationalError",
    ]:
        assert failure not in combined, combined


def test_percent_in_password_is_not_interpolated(
    db_config, schema, work_dir, alembic_ini_exists
):
    """A "%" in the password must reach libpq untouched.

    ConfigParser reads "%" as an interpolation marker, which is why env.py
    builds the engine directly instead of going through
    config.set_main_option(). The wrong password means the connection is
    refused -- the point is *how*: an authentication failure proves the URL was
    assembled and handed over intact, whereas an interpolation error would mean
    it never got that far.
    """
    config = load_config(str(db_config))["targetdb"]["db"]
    conf_path = work_dir / "percent_password.toml"
    conf_path.write_text(
        f"""\
[targetdb.db]
dialect = "{config["dialect"]}"
user = "{config["user"]}"
password = "pa%%ss"
host = "{config["host"]}"
port = {config["port"]}
dbname = "{config["dbname"]}"
"""
    )

    result = run_alembic("current", env={"TARGETDB_CONF": str(conf_path)})
    combined = result.stdout + result.stderr

    assert result.returncode != 0
    assert "password authentication failed" in combined, combined
    assert "Interpolation" not in combined, combined
