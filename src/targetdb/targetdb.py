#!/usr/bin/env python

import io

import pandas as pd
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from loguru import logger

from . import models


class TargetDB(object):
    # url = "postgresql://pfs@db-ics:5432/opdb"

    def __init__(
        self,
        host="localhost",
        port: int = 5432,
        dbname=None,
        user=None,
        password=None,
        dialect="postgresql",
    ):
        for param in [dbname, user, password]:
            if param is None:
                logger.error(f"{param} is not provided")
                raise ValueError(f"{param} is not provided")

        self.dbinfo = f"{dialect}://{user}:{password}@{host}:{port}/{dbname}"

    def connect(self):
        self.engine = create_engine(self.dbinfo)
        SessionClass = sessionmaker(self.engine)
        self.session = SessionClass()
        # print('connection to {0} started'.format(self.dbinfo))

    def close(self):
        self.session.close()
        # print('connection to {0} closed'.format(self.dbinfo))

    def reset_all(self, full=True):
        #
        # Order of the resetting tables is important
        #
        self.session.query(models.cluster).delete()
        self.session.query(models.target).delete()
        self.session.query(models.fluxstd).delete()
        self.session.query(models.sky).delete()
        self.session.query(models.proposal).delete()
        self.session.query(models.input_catalog).delete()
        self.session.query(models.target_type).delete()
        self.session.query(models.proposal_category).delete()
        self.session.execute("ALTER SEQUENCE target_target_id_seq RESTART WITH 1")
        self.session.execute("ALTER SEQUENCE fluxstd_fluxstd_id_seq RESTART WITH 1")
        self.session.execute("ALTER SEQUENCE sky_sky_id_seq RESTART WITH 1")

        self.session.commit()

    def reset_target(self):
        self.session.query(models.target).delete()
        self.session.execute("ALTER SEQUENCE target_target_id_seq RESTART WITH 1")

    def reset_fluxstd(self):
        self.session.query(models.fluxstd).delete()
        self.session.execute("ALTER SEQUENCE fluxstd_fluxstd_id_seq RESTART WITH 1")

    def reset_sky(self):
        self.session.query(models.sky).delete()
        self.session.execute("ALTER SEQUENCE sky_sky_id_seq RESTART WITH 1")

    def rollback(self):
        self.session.rollback()

    # functionality to insert/update information into the database

    def insert_mappings(
        self, tablename, mappings, return_defaults=False, dry_run=False
    ):
        """
        Description
        -----------
            Insert information into a table
        Parameters
        ----------
            tablename : `string`
            mappings : `dictionnary list`
        Returns
        -------
            None
        """
        model = getattr(models, tablename)
        try:
            # print(mappings)
            self.session.bulk_insert_mappings(
                model, mappings, return_defaults=return_defaults
            )
            if dry_run:
                self.session.rollback()
                return None
            else:
                self.session.commit()

            if return_defaults:
                df_ret = pd.DataFrame.from_records(mappings)
                return df_ret
            else:
                return None
            # print(mappings)
        except Exception as e:
            self.session.rollback()
            raise e

    def insert(self, tablename, dataframe, return_defaults=False, dry_run=False):
        """
        Description
        -----------
            Insert information into a table
        Parameters
        ----------
            tablename : `string`
            dataframe : `pandas.DataFrame`
        Returns
        -------
            None
        Note
        ----
            Column labels of `dataframe` should be exactly the same as those of the table
        """
        mappings_dict = dataframe.to_dict(orient="records")
        df_ret = self.insert_mappings(
            tablename, mappings_dict, return_defaults=return_defaults, dry_run=dry_run
        )
        if return_defaults:
            return df_ret
        else:
            return None

    def insert_by_copy(self, tablename, data, colnames, dry_run=False):
        """
        Description
        -----------
            Insert information into a table using COPY FROM method
        Parameters
        ----------
            tablename : `string`
            data : `a text stream`
            colnames: `list` of `string`
        Returns
        -------
            None
        Note
        ----
        """
        conn = self.engine.raw_connection()
        cur = conn.cursor()
        cur.copy_from(data, tablename, ",", columns=colnames)
        if dry_run:
            conn.rollback()
        else:
            conn.commit()
        cur.close()
        conn.close()

    def update(self, tablename, dataframe, dry_run=False):
        """
        Description
        -----------
            Update information of a table
        Parameters
        ----------
            tablename : `string`
            dataframe : `pandas.DataFrame`
        Returns
        -------
            None
        Note
        ----
            Column labels of `dataframe` should be exactly the same as those of the table
        """
        model = getattr(models, tablename)
        try:
            self.session.bulk_update_mappings(
                model, dataframe.to_dict(orient="records")
            )
            if dry_run:
                self.session.rollback()
            else:
                self.session.commit()
        except:
            self.session.rollback()
            raise

    """
        ##################################################
        functionality to get information from the database
        ##################################################
    """

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
        """
        model = getattr(models, tablename)
        try:
            # Use session.execute() with select() to avoid immutabledict issues with pd.read_sql()
            stmt = select(model)
            result = self.session.execute(stmt)
            # Get column names from the model's mapper
            columns = [c.key for c in model.__mapper__.columns]
            data = result.fetchall()
            # Extract values from Row objects (each row is a tuple with one element - the model instance)
            rows = [[getattr(row[0], col) for col in columns] for row in data]
            df = pd.DataFrame(rows, columns=columns)
        except:
            self.session.rollback()
            raise

        return df

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
        model = getattr(models, tablename)
        try:
            # Use session.execute() with select() to avoid immutabledict issues with pd.read_sql()
            stmt = select(model)
            for k, v in kwargs.items():
                stmt = stmt.filter(getattr(model, k) == v)
            result = self.session.execute(stmt)
            # Get column names from the model's mapper
            columns = [c.key for c in model.__mapper__.columns]
            data = result.fetchall()
            # Extract values from Row objects (each row is a tuple with one element - the model instance)
            rows = [[getattr(row[0], col) for col in columns] for row in data]
            df = pd.DataFrame(rows, columns=columns)
        except:
            self.session.rollback()
            raise

        return df

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
        """
        try:
            # Use session.execute() with text() to avoid immutabledict issues with pd.read_sql()
            result = self.session.execute(text(query))
            columns = result.keys()
            data = result.fetchall()
            df = pd.DataFrame(data, columns=columns)
        except:
            self.session.rollback()
            raise

        return df

    def fetch_by_copy(self, tablename, colnames):
        """
        Description
        -----------
            Get selected records from a table by using COPY TO method
        Parameters
        ----------
            tablename : `string`
            colnames  : `list` of `string`
        Returns
        -------
            data      : `io.StringIO` (comma-separated)
        Note
        ----
        """
        data = io.StringIO()
        conn = self.engine.raw_connection()
        cur = conn.cursor()
        cur.copy_to(data, tablename, sep=",", null="\\N", columns=colnames)
        cur.close()
        conn.close()
        data.seek(0)
        return data

    def execute_query(self, query, dry_run=False):
        """
        Description
        -----------
            Execute a SQL query
        Parameters
        ----------
            query : `string`
        Returns
        -------
            None
        Note
        ----
        """
        try:
            self.session.execute(text(query))
            if dry_run:
                self.session.rollback()
            else:
                self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
