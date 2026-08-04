#!/usr/bin/env python3

import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

import pytest

INTEGRATION_TESTS_DIR = Path(__file__).parent / "integration"


def pytest_addoption(parser):
    parser.addoption(
        "--keep-db",
        action="store_true",
        default=False,
        help=(
            "Do not tear down the PostgreSQL test container after the "
            "integration test session. Useful for inspecting the database "
            "after a failure, e.g. with "
            "`psql -h localhost -p 15433 -U postgres -d test_targetdb`."
        ),
    )


@lru_cache(maxsize=1)
def docker_available_reason():
    """
    Check whether a usable Docker daemon is available.

    Returns
    -------
    reason : str or None
        None if Docker is available and responsive, otherwise a short
        string explaining why it is not, suitable for a pytest skip reason.
    """
    if shutil.which("docker") is None:
        return "docker executable not found on PATH"

    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return f"docker info failed to run: {e}"

    if result.returncode != 0:
        return "docker daemon is not reachable (`docker info` failed)"

    return None


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: tests requiring a PostgreSQL container via Docker",
    )


def pytest_collection_modifyitems(config, items):
    reason = docker_available_reason()

    for item in items:
        try:
            item.path.relative_to(INTEGRATION_TESTS_DIR)
        except ValueError:
            continue

        item.add_marker(pytest.mark.integration)

        if reason is not None:
            item.add_marker(pytest.mark.skip(reason=f"Docker unavailable: {reason}"))
