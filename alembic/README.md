# Alembic migrations for targetdb

Schema changes to `targetdb` are applied with
[Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html). The models in
`src/targetdb/models/` are the source of truth; the revision scripts here record
how each deployed database was brought to match them.

## Layout

Each deployment target has its own directory, with its own `alembic.ini` and its
own independent revision history. **Run alembic from inside the directory for
the database you are migrating** — the histories are not interchangeable.

| Directory           | Database                                        |
| ------------------- | ----------------------------------------------- |
| `local_test/`       | A local database used for trying migrations out |
| `pfsa-db01-gb/`     | Production                                      |
| `pfsa-db01-gb-dev/` | Development                                     |

The revision scripts under `*/alembic/versions/` are historical records. They
are deliberately excluded from `ruff` and `black` (see `pyproject.toml`) and
should not be reformatted or "cleaned up" — only the `env.py` scripts are
linted. Once a revision has been applied to a deployed database, edit it only
to fix something that is actually broken.

## Configuring the connection

Set `TARGETDB_CONF` to a targetdb TOML configuration file — the same one the
CLI takes with `-c` — and `env.py` builds the connection URL from it:

```bash
cd alembic/pfsa-db01-gb
TARGETDB_CONF=~/database_configs/config_targetdb.toml alembic upgrade head
```

This keeps the credentials in one place rather than duplicating them into every
`alembic.ini`, and the psycopg3 driver is selected automatically. If
`TARGETDB_CONF` is unset, `env.py` falls back to the `sqlalchemy.url` entry in
`alembic.ini`, which is a credentials-free placeholder.

Passwords may be left out of the TOML entirely, in which case libpq resolves
them from `PGPASSWORD` or `~/.pgpass`. See `docs/getting_started.md`.

## Workflow

1. **Change the models** under `src/targetdb/models/`.

2. **Generate a revision.** Autogenerate compares the models against the live
   database, so this needs a database that is currently at `head`:

   ```bash
   TARGETDB_CONF=<config.toml> alembic revision --autogenerate -m "Add columns"
   ```

3. **Read the generated file** in `versions/` before running it. Autogenerate is
   a starting point, not an answer — see the gotchas below for what it gets
   wrong on this schema.

4. **Apply it.**

   ```bash
   TARGETDB_CONF=<config.toml> alembic upgrade head
   ```

   Check where you are at any time with `alembic current`, and what exists with
   `alembic history`.

Try a migration against `local_test/` (or a throwaway container — see
`tests/docker/`) before running it on a deployed database.

## Gotchas

### A unique constraint cannot be added while duplicates exist

`CREATE UNIQUE INDEX` fails outright if the table already violates the
constraint, and the migration aborts partway:

```text
UniqueViolation: could not create unique index "uq_sky_obj_id_input_catalog_id_version"
DETAIL:  Key (obj_id, input_catalog_id, version)=(44332, 1002, 20220915) is duplicated.
```

Count the offending rows first, and decide what to do with them before writing
the migration:

```sql
-- How many groups are duplicated, and by how much?
SELECT ct, count(*) AS n_groups
FROM (
    SELECT obj_id, input_catalog_id, version, count(*) AS ct
    FROM sky
    GROUP BY obj_id, input_catalog_id, version
    HAVING count(*) > 1
) sub
GROUP BY 1 ORDER BY 1;

-- Which rows are they?
SELECT obj_id, ra, dec, input_catalog_id, version, count(*)
FROM sky
GROUP BY obj_id, ra, dec, input_catalog_id, version
HAVING count(*) > 1;
```

Substitute the table and the intended constraint columns. `sky` has run to
billions of rows per `version`, so on it and `fluxstd` expect these queries to
take a while, and restrict them by `version` where you can.

### Autogenerate does not see the q3c indexes

The positional tables are indexed on the expression `q3c_ang2ipix(ra, dec)`, and
SQLAlchemy cannot reflect expression-based indexes:

```text
SAWarning: Skipped unsupported reflection of expression-based index sky_q3c_ang2ipix_idx
```

The warning is harmless, but it means autogenerate will neither create nor
notice a change to those indexes. Write that DDL by hand.

Identity/serial sequences are likewise reported as skipped
(`Detected sequence named 'fluxstd_fluxstd_id_seq' ... assuming SERIAL and
omitting`); this is normal and needs nothing.

### `%` in a password

`env.py` builds the engine directly rather than going through
`config.set_main_option()`, because ConfigParser reads `%` as an interpolation
marker and would corrupt a password containing one. Keep it that way.

### `local_test/` has a broken revision chain

`80f8276e2ee7` names a `down_revision` (`ecfad41204d1`) that is not present in
the repository, so any command that walks the full revision map — `alembic
current` and `alembic history` included — raises `KeyError`. This predates the
move to `TARGETDB_CONF`; connecting to the database itself works.
