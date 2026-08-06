#!/usr/bin/env python

from contextlib import contextmanager

import pandas as pd
from loguru import logger
from pfs.utils.database.db import DB
from sqlalchemy import URL, and_, bindparam, select

from . import models


class TargetDB(DB):
    """PFS targetDB accessor built on top of ``pfs.utils.database.db.DB``.

    ``DB`` supplies the engine cache, ``pool_pre_ping``, ``COPY``-based bulk
    inserts and the ``query_*`` family. Only what ``DB`` does not provide is
    implemented here:

    * a password and an explicit dialect in the URL (``DB`` always omits the
      password and hardcodes ``postgresql+psycopg``),
    * ``update()``,
    * the ``dry_run=`` keyword that backs the CLI's ``--commit`` default,
    * ``close()``.

    The public methods kept for backwards compatibility (``connect``,
    ``close``, ``fetch_query``, ``fetch_all``, ``fetch_by_id``) are all used by
    downstream packages (``ets_pointing``, ``pfs_obsproc_planning_tools``).

    Connection parameters default to ``DEFAULT_HOST``/``DEFAULT_USER``/
    ``DEFAULT_DBNAME``/``DEFAULT_PORT`` below, the same convention
    ``pfs.utils.database.db`` uses for ``OpDB`` and ``QaDB``: ``DB.__init__``
    resolves any argument left as ``None`` from ``type(self).DEFAULT_*``, so
    declaring these class attributes is also what makes the inherited
    ``set_default_connection()`` classmethod usable on ``TargetDB``. The
    default user, ``obsproc``, is read-only in production -- every write path
    in this package (the CLI, ``utils.add_database_rows``, etc.) passes an
    explicit ``user`` from a config file instead of relying on these
    defaults, so a bare ``TargetDB()`` can read but never write.
    """

    DEFAULT_HOST = "pfsa-db"
    DEFAULT_USER = "obsproc"
    DEFAULT_DBNAME = "targetdb"
    DEFAULT_PORT = 5433
    # Not part of DB: DB.url hardcodes postgresql+psycopg, TargetDB.url does
    # not, so TargetDB needs its own default for the dialect argument below.
    DEFAULT_DIALECT = "postgresql"

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        dbname: str | None = None,
        user: str | None = None,
        password: str | None = None,
        dialect: str | None = None,
    ):
        # Set before super().__init__(): the url property below reads both, and
        # anything the base class does must already see them.
        # `password` is deliberately optional and has no DEFAULT_PASSWORD:
        # when it is None it is left out of the URL and libpq resolves it
        # (PGPASSWORD, then ~/.pgpass), which is exactly the arrangement DB
        # itself documents.
        self._password = password
        # Imported lazily to avoid a circular import (utils imports TargetDB).
        from .utils import normalize_drivername

        self._drivername = normalize_drivername(
            dialect if dialect is not None else type(self).DEFAULT_DIALECT
        )
        self._dry_run = False

        super().__init__(host=host, user=user, dbname=dbname, port=port)

        # The CLI and every other write path splat a full [targetdb.db] table,
        # so this never fires there. It fires exactly when a parameter was
        # omitted and a class default therefore decided which database (and,
        # for `user`, which privilege level) this instance talks to.
        defaulted = [
            name
            for name, value in [
                ("host", host),
                ("port", port),
                ("dbname", dbname),
                ("user", user),
            ]
            if value is None
        ]
        if defaulted:
            logger.info(
                f"Using TargetDB class defaults for {', '.join(defaulted)}: "
                f"{self.user}@{self.host}:{self.port}/{self.dbname}"
            )

    @property
    def url(self) -> str:
        """Connection URL, including the password when one was configured.

        Overrides ``DB.url``, which always omits the password and hardcodes the
        ``postgresql+psycopg`` driver.

        Note
        ----
        ``DB.engine`` caches engines in a process-global dict keyed by this
        string, so a configured password is held in that key for the lifetime
        of the process. Never log this value directly -- use
        ``URL.create(...).render_as_string()`` (which masks it) instead.
        """
        return URL.create(
            drivername=self._drivername,
            username=self.user,
            password=self._password,
            host=self.host,
            port=self.port,
            database=self.dbname,
        ).render_as_string(hide_password=False)

    def connect(self) -> None:
        """Materialize the engine. Deliberately returns nothing.

        ``DB.connect()`` returns a pooled ``Connection``; callers here (and in
        the downstream packages) discard the return value, which would leak one
        checked-out connection per call. ``DB.connection()`` is the only
        internal user of ``DB.connect()`` and is overridden below, so narrowing
        this to "make sure the engine exists" is safe.
        """
        _ = self.engine

    def close(self) -> None:
        """Dispose the engine, closing every pooled connection.

        ``DB`` has no ``close()``. Without this, connections linger until the
        engine is garbage-collected and ``drop-db`` fails with "database is
        being accessed by other users". ``Engine.dispose()`` replaces the pool
        rather than invalidating the engine, so the instance cached in
        ``pfs.utils.database.db._DB_ENGINES`` stays usable afterwards.
        """
        self.engine.dispose()

    def __enter__(self):
        """Support usage as a context manager: ``with TargetDB(...) as db:``."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure close() is called even if an exception occurs inside the block."""
        self.close()
        return False  # re-raise any exception

    @contextmanager
    def _dry_run_scope(self, dry_run):
        """Temporarily flip the dry-run flag consulted by ``connection()``."""
        previous = self._dry_run
        self._dry_run = dry_run
        try:
            yield
        finally:
            self._dry_run = previous

    @contextmanager
    def connection(self):
        """Pooled connection that commits, or rolls back under dry-run.

        Overrides ``DB.connection()``, which always commits. Every ``DB`` method
        that touches the database goes through here, so honouring ``_dry_run``
        at this one point makes ``insert``/``update``/``execute_query`` all obey
        the CLI's ``--commit`` contract -- including the ``COPY`` fast path,
        whose raw cursor runs inside this same transaction.

        The transaction is opened eagerly rather than left to SQLAlchemy's
        implicit begin: ``pandas.DataFrame.to_sql`` starts *and commits* a
        transaction of its own when handed a connection that is not already in
        one, which would make the rollback below a no-op.
        """
        with self.engine.connect() as conn:
            conn.begin()
            yield conn
            if self._dry_run:
                conn.rollback()
            else:
                conn.commit()

    # ##################################################
    # functionality to insert/update information
    # ##################################################

    @staticmethod
    def _drop_unknown_columns(tablename, dataframe):
        """Drop DataFrame columns the table does not have.

        `add_backref_values()` resolves foreign keys by merging whole reference
        tables into the DataFrame, which leaves descriptive columns behind
        (`partner_name` and `proposal_category_name` when inserting proposals,
        for instance). The ORM `bulk_insert_mappings()` path this class used to
        take ignored keys that were not mapped to a column; `COPY` and Core
        `update()` do not, so the same leniency is applied explicitly here.
        """
        known = set(getattr(models, tablename).__table__.columns.keys())
        extra = [column for column in dataframe.columns if column not in known]
        if not extra:
            return dataframe
        logger.debug(f"Ignoring columns absent from the {tablename} table: {extra}")
        return dataframe.drop(columns=extra)

    def insert(self, tablename, dataframe, dry_run=False):
        """
        Description
        -----------
            Insert information into a table
        Parameters
        ----------
            tablename : `string`
            dataframe : `pandas.DataFrame`
            dry_run   : `bool`  roll back instead of committing
        Returns
        -------
            n_inserted : `int` or `None`
        Note
        ----
            Column labels of `dataframe` should be exactly the same as those of
            the table. Delegates to `DB.insert_dataframe()`, which uses
            PostgreSQL's `COPY`.
        """
        with self._dry_run_scope(dry_run):
            return self.insert_dataframe(
                tablename, self._drop_unknown_columns(tablename, dataframe)
            )

    def update(self, tablename, dataframe, dry_run=False):
        """
        Description
        -----------
            Update information of a table
        Parameters
        ----------
            tablename : `string`
            dataframe : `pandas.DataFrame`
            dry_run   : `bool`  roll back instead of committing
        Returns
        -------
            None
        Note
        ----
            Column labels of `dataframe` should be exactly the same as those of
            the table, and must include the primary key column(s), which are
            matched on rather than written. `DB` has no equivalent, so this is a
            single Core UPDATE statement executed once per row by executemany.
        """
        table = getattr(models, tablename).__table__
        dataframe = self._drop_unknown_columns(tablename, dataframe)
        records = dataframe.to_dict(orient="records")
        if not records:
            logger.warning(f"No rows to update in the {tablename} table.")
            return

        pk_names = [c.name for c in table.primary_key.columns]
        missing = [name for name in pk_names if name not in dataframe.columns]
        if missing:
            raise ValueError(
                f"Primary key column(s) {missing} missing from the DataFrame "
                f"for the {tablename} table."
            )

        value_names = [name for name in dataframe.columns if name not in pk_names]
        if not value_names:
            raise ValueError(
                f"The DataFrame for the {tablename} table contains only primary "
                "key columns; there is nothing to update."
            )

        # The primary key values are bound under a "_pk_" prefix so that they do
        # not collide with the SET parameters of the same name.
        for record in records:
            for name in pk_names:
                record[f"_pk_{name}"] = record.pop(name)

        stmt = (
            table.update()
            .where(
                and_(
                    *[
                        c == bindparam(f"_pk_{c.name}")
                        for c in table.primary_key.columns
                    ]
                )
            )
            .values({name: bindparam(name) for name in value_names})
        )

        with self._dry_run_scope(dry_run), self.connection() as conn:
            conn.execute(stmt, records)

    """
        ##################################################
        functionality to get information from the database
        ##################################################
    """

    def _fetch(self, stmt):
        """Run a Core SELECT and return the result as a DataFrame."""
        with self.connection() as conn:
            return pd.read_sql(stmt, con=conn)

    def fetch_all(self, tablename):
        """
        Description
        -----------
            Get all records from a table
        Parameters
        ----------
            tablename : `string`
        Returns
        -------
            df : `pandas.DataFrame`
        Note
        ----
            Uses a Core `select()` on the model's `Table` rather than
            `DB.query_dataframe()`, which would require interpolating the table
            name into a SQL string.
        """
        return self._fetch(select(getattr(models, tablename).__table__))

    def fetch_by_id(self, tablename, **kwargs):
        """
        Description
        -----------
            Get records from a table where the keyword identifier is matched
        Parameters
        ----------
            tablename : `string`
            **kwargs  :          (e.g., pfs_visit_id=12345)
        Returns
        -------
            df : `pandas.DataFrame`
        Note
        ----
        """
        table = getattr(models, tablename).__table__
        stmt = select(table)
        for k, v in kwargs.items():
            stmt = stmt.where(table.c[k] == v)
        return self._fetch(stmt)

    def fetch_query(self, query):
        """
        Description
        -----------
            Get all records from SQL query
        Parameters
        ----------
            query : `string`
        Returns
        -------
            df : `pandas.DataFrame`
        Note
        ----
            Delegates to `DB.query_dataframe()`.
        """
        return self.query_dataframe(query)

    def execute_query(self, query, dry_run=False):
        """
        Description
        -----------
            Execute a SQL query
        Parameters
        ----------
            query   : `string`
            dry_run : `bool`  roll back instead of committing
        Returns
        -------
            None
        Note
        ----
            Delegates to `DB.commit()`.
        """
        with self._dry_run_scope(dry_run):
            self.commit(query)
