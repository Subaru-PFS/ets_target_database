#!/usr/bin/env python3
"""
Session-scoped fixture pipeline that reproduces, locally, the sequence of
`pfs-targetdb-cli` commands run by .github/workflows/test_database.yml:

    postgres_service -> db_config -> database -> q3c_installed -> schema
        -> master_data -> fluxstd_data
        -> master_data -> target_data -> pointing_data

Each fixture requests the one(s) it depends on, so a test only needs to
request the fixture for the stage it cares about (and pytest builds
everything upstream automatically). All of it is torn down once per test
session (or left running with `--keep-db`).

Unlike the CI workflow, output files (prep-fluxstd output, transferred
target lists) are written under a pytest-managed temporary directory
instead of into the repository, so running the suite never leaves the
working tree dirty.
"""

import subprocess
from pathlib import Path

import pandas as pd
import pytest
from astropy.table import Table
from sqlalchemy import create_engine, text
from typer.testing import CliRunner

from targetdb.cli.cli_main import app
from targetdb.utils import get_url_object, load_config

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCKER_DIR = REPO_ROOT / "tests" / "docker"
COMPOSE_FILE = DOCKER_DIR / "docker-compose.test.yml"

EXAMPLES_DATA = REPO_ROOT / "examples" / "data"
TARGETS_DATA_DIR = EXAMPLES_DATA / "targets"
FLUXSTD_INPUT_DIR = EXAMPLES_DATA / "fluxstd" / "Fstar_v3.3" / "feather-original"

# Master tables inserted in the same order as the "Insert example data" CI step.
MASTER_TABLE_FILES = [
    ("target_type", "target_types.csv"),
    ("filter_name", "filter_names.csv"),
    ("partner", "partner.csv"),
    ("pfs_arm", "pfs_arm.csv"),
    ("proposal_category", "proposal_category.csv"),
    ("proposal", "proposals.csv"),
    ("input_catalog", "input_catalogs.csv"),
]

PG_PORT = 15433

_cli_runner = CliRunner()


def run_cli(*args):
    """
    Invoke the ``pfs-targetdb-cli`` Typer app in-process and assert success.

    Running in-process (rather than via subprocess) means failures surface
    as normal Python tracebacks/output in the pytest report instead of an
    opaque non-zero exit code.
    """
    result = _cli_runner.invoke(app, [str(a) for a in args], catch_exceptions=False)
    assert result.exit_code == 0, (
        f"CLI command {args!r} failed with exit code {result.exit_code}\n"
        f"Output:\n{result.output}"
    )
    return result


def count_rows(engine, table):
    with engine.connect() as conn:
        return conn.execute(text(f"SELECT count(*) FROM {table}")).scalar_one()


def csv_row_count(path):
    return len(pd.read_csv(path))


def ecsv_row_count(path):
    return len(Table.read(path, format="ascii.ecsv"))


def _run_compose(*args):
    cmd = ["docker", "compose", "-f", str(COMPOSE_FILE), *args]
    result = subprocess.run(cmd, cwd=DOCKER_DIR, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


@pytest.fixture(scope="session")
def postgres_service(request):
    """Bring up the PostgreSQL+Q3C container for the whole test session."""
    _run_compose("up", "-d", "--build", "--wait", "--wait-timeout", "120")
    try:
        yield {"host": "localhost", "port": PG_PORT}
    finally:
        if request.config.getoption("--keep-db"):
            print(
                f"\n--keep-db: leaving the test PostgreSQL container running "
                f"on port {PG_PORT}. Stop it manually with:\n"
                f"  docker compose -f {COMPOSE_FILE} down -v"
            )
        else:
            _run_compose("down", "-v", "--remove-orphans")


@pytest.fixture(scope="session")
def work_dir(tmp_path_factory):
    """Scratch directory for generated config/data files, unique per session."""
    return tmp_path_factory.mktemp("targetdb-integration")


@pytest.fixture(scope="session")
def db_config(postgres_service, work_dir):
    """Write a test dbconf.toml pointing at the container and return its path."""
    config_path = work_dir / "test_db_config.toml"
    config_path.write_text(
        f"""\
[targetdb.db]
dialect = "postgresql"
user = "postgres"
password = "postgres"
host = "{postgres_service["host"]}"
port = {postgres_service["port"]}
dbname = "test_targetdb"

[uploader]
host = "localhost"
data_dir = "{EXAMPLES_DATA / "uploader"}"
"""
    )
    return config_path


@pytest.fixture(scope="session")
def engine(database, db_config):
    config = load_config(str(db_config))
    eng = create_engine(get_url_object(config))
    yield eng
    eng.dispose()


@pytest.fixture(scope="session")
def database(db_config):
    run_cli("create-db", "-c", db_config)


@pytest.fixture(scope="session")
def q3c_installed(database, db_config):
    run_cli("install-q3c", "-c", db_config)


@pytest.fixture(scope="session")
def schema(q3c_installed, db_config):
    run_cli("create-schema", "-c", db_config)


@pytest.fixture(scope="session")
def master_data(schema, db_config):
    """Insert the master/reference tables shared by every downstream stage."""
    for table, filename in MASTER_TABLE_FILES:
        run_cli(
            "insert", EXAMPLES_DATA / filename, "-c", db_config, "-t", table, "--commit"
        )
    # input_catalog entry required by the flux standard star catalog.
    run_cli(
        "insert",
        EXAMPLES_DATA / "input_catalog_fluxstd.csv",
        "-c",
        db_config,
        "-t",
        "input_catalog",
        "--commit",
    )


@pytest.fixture(scope="session")
def fluxstd_data(master_data, db_config, work_dir):
    """Run prep-fluxstd and insert the resulting rows into the fluxstd table."""
    output_dir = work_dir / "fluxstd_feather"
    run_cli(
        "prep-fluxstd",
        FLUXSTD_INPUT_DIR,
        output_dir,
        "--version",
        "3.3",
        "--input_catalog_id",
        "3006",
        "--rename-cols",
        '{"fstar_gaia": "is_fstar_gaia"}',
        "--format",
        "feather",
    )
    generated_files = sorted(output_dir.glob("*.feather"))
    assert generated_files, f"prep-fluxstd produced no feather files in {output_dir}"

    for f in generated_files:
        run_cli("insert", f, "-c", db_config, "-t", "fluxstd", "--commit")

    return {"output_dir": output_dir, "files": generated_files}


@pytest.fixture(scope="session")
def target_data(master_data, db_config, work_dir):
    """Insert proposals/catalogs for the target examples, then transfer and insert targets."""
    run_cli(
        "insert",
        TARGETS_DATA_DIR / "example_proposals.csv",
        "-c",
        db_config,
        "-t",
        "proposal",
        "--commit",
    )
    run_cli(
        "insert",
        TARGETS_DATA_DIR / "example_input_catalogs.csv",
        "-c",
        db_config,
        "-t",
        "input_catalog",
        "--commit",
        "--fetch",
    )

    local_dir = work_dir / "targets"
    run_cli(
        "transfer-targets",
        TARGETS_DATA_DIR / "example_input_catalogs.csv",
        "-c",
        db_config,
        "--local-dir",
        local_dir,
        "--force",
    )
    run_cli(
        "insert-targets",
        TARGETS_DATA_DIR / "example_input_catalogs.csv",
        "-c",
        db_config,
        "--data-dir",
        local_dir,
        "--commit",
    )

    return {"local_dir": local_dir}


@pytest.fixture(scope="session")
def pointing_data(target_data, db_config):
    run_cli(
        "insert-pointings",
        TARGETS_DATA_DIR / "example_input_catalogs.csv",
        "-c",
        db_config,
        "--data-dir",
        target_data["local_dir"],
        "--commit",
    )
