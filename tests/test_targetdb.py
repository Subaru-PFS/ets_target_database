#!/usr/bin/env python3
"""
Unit tests for `TargetDB` and the URL helpers it shares with `targetdb.utils`.

None of these need a database: URL construction is a pure function of the
configuration, and `connect()` only materializes a lazily-created engine.
The behaviour that does need a live server is covered by
`tests/integration/test_targetdb_api.py` and `tests/integration/test_dry_run.py`.
"""

import pytest

from targetdb import TargetDB
from targetdb.utils import get_alembic_url, get_url_object, normalize_drivername

# Methods dropped when TargetDB became a subclass of pfs.utils.database.db.DB.
# reset_* stopped working under SQLAlchemy 2.x and *_by_copy used psycopg2-only
# APIs; none of the three PFS repositories called any of them.
REMOVED_METHODS = [
    "reset_all",
    "reset_target",
    "reset_fluxstd",
    "reset_sky",
    "insert_by_copy",
    "fetch_by_copy",
    "insert_mappings",
    "rollback",
]


def make_config(**overrides):
    db = {
        "dialect": "postgresql",
        "user": "admin",
        "password": "secret",
        "host": "db.example.org",
        "port": 5433,
        "dbname": "targetdb",
    }
    db.update(overrides)
    for key in [k for k, v in db.items() if v is None]:
        del db[key]
    return {"targetdb": {"db": db}}


class TestNormalizeDrivername:
    @pytest.mark.parametrize("dialect", ["postgresql", "postgres"])
    def test_bare_postgres_names_map_to_psycopg3(self, dialect):
        assert normalize_drivername(dialect) == "postgresql+psycopg"

    @pytest.mark.parametrize(
        "dialect", ["postgresql+psycopg", "postgresql+psycopg2", "mysql+pymysql"]
    )
    def test_explicit_driver_is_passed_through(self, dialect):
        assert normalize_drivername(dialect) == dialect


class TestUrl:
    def test_url_contains_password_and_psycopg3_driver(self):
        db = TargetDB(**make_config()["targetdb"]["db"])
        assert (
            db.url == "postgresql+psycopg://admin:secret@db.example.org:5433/targetdb"
        )

    def test_url_omits_password_when_not_configured(self):
        """Without a password the URL matches DB.url's native shape, so libpq
        resolves the credential itself via PGPASSWORD / ~/.pgpass."""
        db = TargetDB(**make_config(password=None)["targetdb"]["db"])
        assert db.url == "postgresql+psycopg://admin@db.example.org:5433/targetdb"
        assert "secret" not in db.url

    def test_password_special_characters_are_escaped(self):
        db = TargetDB(**make_config(password="p%w@rd")["targetdb"]["db"])
        assert db.url == (
            "postgresql+psycopg://admin:p%25w%40rd@db.example.org:5433/targetdb"
        )

    def test_explicit_dialect_is_honoured(self):
        db = TargetDB(**make_config(dialect="postgresql+psycopg")["targetdb"]["db"])
        assert db.url.startswith("postgresql+psycopg://")


class TestGetUrlObject:
    def test_applies_the_same_driver_normalization(self):
        url = get_url_object(make_config())
        assert url.drivername == "postgresql+psycopg"

    def test_password_is_optional(self):
        url = get_url_object(make_config(password=None))
        assert url.password is None
        assert url.render_as_string(hide_password=False) == (
            "postgresql+psycopg://admin@db.example.org:5433/targetdb"
        )

    def test_matches_targetdb_url(self):
        config = make_config()
        url = get_url_object(config).render_as_string(hide_password=False)
        assert url == TargetDB(**config["targetdb"]["db"]).url


class TestRequiredParameters:
    @pytest.mark.parametrize("missing", ["dbname", "user"])
    def test_missing_parameter_raises_with_its_name(self, missing):
        with pytest.raises(ValueError, match=f"{missing} is not provided"):
            TargetDB(**make_config(**{missing: None})["targetdb"]["db"])

    def test_missing_password_does_not_raise(self):
        TargetDB(**make_config(password=None)["targetdb"]["db"])


class TestApiSurface:
    def test_connect_returns_none(self):
        """DB.connect() hands back a pooled Connection, but every caller here
        and downstream discards the return value, which would leak one
        checked-out connection per call. The override must return nothing."""
        db = TargetDB(**make_config()["targetdb"]["db"])
        assert db.connect() is None

    @pytest.mark.parametrize("name", REMOVED_METHODS)
    def test_removed_methods_are_gone(self, name):
        db = TargetDB(**make_config()["targetdb"]["db"])
        assert not hasattr(db, name)

    @pytest.mark.parametrize(
        "name", ["connect", "close", "fetch_query", "fetch_all", "fetch_by_id"]
    )
    def test_downstream_methods_are_kept(self, name):
        db = TargetDB(**make_config()["targetdb"]["db"])
        assert callable(getattr(db, name))


class TestGetAlembicUrl:
    def _write_config(self, tmp_path, password="secret"):
        conf = tmp_path / "dbconf.toml"
        conf.write_text(
            f"""\
[targetdb.db]
dialect = "postgresql"
user = "admin"
password = "{password}"
host = "db.example.org"
port = 5433
dbname = "targetdb"
"""
        )
        return conf

    def test_reads_the_file_named_by_targetdb_conf(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TARGETDB_CONF", str(self._write_config(tmp_path)))
        assert get_alembic_url() == (
            "postgresql+psycopg://admin:secret@db.example.org:5433/targetdb"
        )

    def test_returns_none_without_targetdb_conf(self, monkeypatch):
        """None is the signal for env.py to fall back to alembic.ini."""
        monkeypatch.delenv("TARGETDB_CONF", raising=False)
        assert get_alembic_url() is None

    def test_explicit_argument_wins_over_the_environment(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TARGETDB_CONF", "/nonexistent/does-not-exist.toml")
        conf = self._write_config(tmp_path)
        assert "db.example.org" in get_alembic_url(conf_file=conf)

    def test_percent_in_password_survives(self, tmp_path, monkeypatch):
        """ConfigParser would treat "%" as an interpolation marker, which is why
        env.py builds the engine directly instead of calling
        config.set_main_option()."""
        monkeypatch.setenv(
            "TARGETDB_CONF", str(self._write_config(tmp_path, password="pa%%ss"))
        )
        assert get_alembic_url().endswith("@db.example.org:5433/targetdb")
        assert "pa%25%25ss" in get_alembic_url()
