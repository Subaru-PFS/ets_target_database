#!/usr/bin/env python

import io

import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import update
from sqlalchemy.orm import sessionmaker

from . import models


class TargetDB(object):
    # url = "postgresql://pfs@db-ics:5432/opdb"

    def __init__(
        self,
        hostname="localhost",
        port="5432",
        dbname="testdb",
        username="admin",
        passwd="ask someone",
        dialect="postgresql",
    ):
        self.dbinfo = "{0}://{1}:{2}@{3}:{4}/{5}".format(
            dialect, username, passwd, hostname, port, dbname
        )

    def connect(self):
        self.engine = create_engine(self.dbinfo)
        SessionClass = sessionmaker(self.engine)
        self.session = SessionClass()
        # print('connection to {0} started'.format(self.dbinfo))

    def close(self):
        self.session.close()
        # print('connection to {0} closed'.format(self.dbinfo))

    def reset(self, full=True):
        self.session.query(models.input_catalog).delete()
        self.session.query(models.object_type).delete()
        self.session.query(models.proposal).delete()
        self.session.query(models.proposal_category).delete()
        self.session.query(models.target).delete()
        self.session.query(models.unique_object).delete()

        self.session.commit()

    def rollback(self):
        self.session.rollback()

    """
        ############################################################
        functionality to insert/update information into the database
        ############################################################
    """

    def insert_mappings(self, tablename, mappings):
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
            self.session.bulk_insert_mappings(model, mappings)
            self.session.commit()
        except:
            self.session.rollback()
            raise

    def insert(self, tablename, dataframe):
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
        self.insert_mappings(tablename, dataframe.to_dict(orient="records"))

    def insert_by_copy(self, tablename, data, colnames):
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
        conn.commit()
        cur.close()
        conn.close()

    def update(self, tablename, dataframe):
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
            df = pd.read_sql(self.session.query(model).statement, self.session.bind)
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
        query = self.session.query(model)
        for k, v in kwargs.items():
            query = query.filter(getattr(model, k) == v)
        try:
            df = pd.read_sql(query.statement, self.session.bind)
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
            df = pd.read_sql(query, self.session.bind)
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