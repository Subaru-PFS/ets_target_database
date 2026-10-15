# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

See @README.md for project overview and @docs/getting_started.md for setup and usage details.

## Commands

```bash
# Install (development)
pip install -e .        # or: uv sync

# Run tests
pytest tests/
pytest tests/test_models.py::test_relations_consistency  # single test

# Lint / format
ruff check src/
black src/

# Docs (requires pip install -e ".[doc]" or uv sync --extra doc)
mkdocs serve
mkdocs build
```

## CLI

All CLI commands require a TOML config file (`-c dbconf.toml`). The config shape is:

```toml
[targetdb.db]
host = "localhost"
port = 5432
dbname = "targetdb"
user = "admin"
password = "admin"   # optional; omitted from the URL when absent, so libpq uses ~/.pgpass
dialect = "postgresql"
```

CLI flags default to `--commit False` (dry-run). Pass `--commit` explicitly to write to the database.

## Non-obvious architecture

- **PostgreSQL + Q3C extension required.** The Q3C extension must be installed before creating the schema (`pfs-targetdb-cli install-q3c`). It provides spatial indexing via `q3c_ang2ipix(ra, dec)` — every positional table (`target`, `fluxstd`, `sky`) has a `*_q3c_ang2ipix_idx` index.
- **Model import order in `src/targetdb/models/__init__.py` is load-order-sensitive** due to SQLAlchemy FK relationships. New models must be imported after their FK dependencies and added to `__all__`.
- **`input_catalog_id` is range-constrained.** The PostgreSQL `Identity` sequence starts at `10000`, max `89999`. Values up to `99999` are reserved for special use.
- **`version` column in `fluxstd` and `sky` is a string**, not a number (e.g., `"3.3"`).
- **All timestamps use UTC** via a custom `utcnow()` SQLAlchemy `FunctionElement` defined in `models/__init__.py`.
- **CLI delegates entirely to `utils.py`.** `cli/cli_main.py` is only argument parsing; all business logic lives in `utils.py`.
- **`TargetDB` is a subclass of `pfs.utils.database.db.DB`** (from the `pfs-utils` package, installed from GitHub). `DB` supplies the engine cache, `pool_pre_ping`, `COPY`-based bulk inserts and the `query_*` API. `targetdb.py` only overrides what `DB` lacks: a password/dialect in the URL, `update()`, `close()`, and the `dry_run=` keyword. Two overrides are load-bearing and easy to break:
  - `connect()` returns `None` on purpose. `DB.connect()` hands back a pooled `Connection`, and every caller here and downstream discards it, which would leak one checked-out connection per call.
  - `connection()` opens its transaction eagerly (`conn.begin()`) and rolls back when `_dry_run` is set. The eager begin matters because `pandas.to_sql` starts _and commits_ a transaction of its own when handed a connection that is not already in one, which would defeat the rollback. Every dry-run path funnels through here. `tests/integration/test_dry_run.py` guards this.
- **`TargetDB`'s connection defaults live in `DEFAULT_HOST`/`DEFAULT_USER`/`DEFAULT_DBNAME`/`DEFAULT_PORT` class attributes**, the same convention `OpDB`/`QaDB` use in `pfs.utils.database.db`. `DB.__init__` resolves any argument left `None` from `type(self).DEFAULT_*`, so every parameter in `TargetDB.__init__` must default to `None`, never to a literal — a non-`None` default in the signature shadows the class attribute and silently breaks the inherited `set_default_connection()` classmethod. `DEFAULT_USER` is `obsproc`, a read-only account, on purpose: these defaults only apply to a bare `TargetDB()`, since every write path (the CLI, `utils.add_database_rows`, …) splats a full `[targetdb.db]` table with an explicit `user`, so a least-privilege default costs nothing and makes an accidental write to production through a bare `TargetDB()` impossible.
- **psycopg3 only.** `dialect = "postgresql"` in a config file is rewritten to `postgresql+psycopg` by `normalize_drivername()` in `utils.py`, the single choke point that every code path (`get_url_object`, `TargetDB.__init__`) passes through. psycopg2 is not a dependency.
- **Inserts drop DataFrame columns the target table does not have** (`TargetDB._drop_unknown_columns`). `add_backref_values()` resolves foreign keys by merging whole reference tables in, leaving columns like `partner_name` behind; the old ORM path ignored unmapped keys and `COPY` does not.
- **Model `default=` values are applied by hand on insert.** They are client-side defaults and `COPY` never sees the models. `TargetDB.insert()` adds absent columns with their scalar default (what the old ORM path did); the CLI insert path also replaces NaN/None/`""` in columns whose default is not `""` (`utils.fill_null_with_defaults()`). Updates never fill. A `""` default is still stored as NULL, because pfs-utils' `COPY` writes `""` as NULL. The non-`""` defaults are also server defaults, declared through `models.with_default()` so the two cannot drift (`tests/test_models.py` checks this). They only cover columns an INSERT leaves out — a blank cell arrives as an explicit NULL — so the Python-side filling stays. A new defaulted column needs `with_default()` and an Alembic revision that sets its server default.
- **Alembic has separate directories with independent histories** under `alembic/` (`local_test/`, `pfsa-db01-gb/`). Each has its own `alembic.ini`; run migrations from within the subdirectory. Dev and production share the `pfsa-db01-gb/` history: new revisions go there and are applied to dev, then production, by switching `TARGETDB_CONF`. `env.py` builds the URL from the TOML file named by the `TARGETDB_CONF` environment variable, falling back to `sqlalchemy.url` in `alembic.ini` when it is unset — so credentials live in one place: `TARGETDB_CONF=dbconf.toml alembic upgrade head`. Do not use `config.set_main_option()` for the URL: ConfigParser reads `%` as an interpolation marker and would mangle passwords containing it. See `alembic/README.md` for the workflow and known gotchas (q3c expression indexes and server defaults are invisible to autogenerate; `ALTER`s on the large tables need `lock_timeout`; `local_test/`'s revision chain is broken).
