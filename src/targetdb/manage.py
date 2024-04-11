#!/usr/bin/env python3

from sqlalchemy import create_engine

from .models import Base


def create_schema(url_object, drop_all=False):
    """
    Create a database schema from the SQLAlchemy models.

    Parameters
    ----------
    url_object : sqlalchemy.engine.url.URL
        The URL object representing the database connection.
    drop_all : bool, optional
        If True, drop all tables in the database before creating new ones.
        Default is False.

    Raises
    ------
    sqlalchemy.exc.SQLAlchemyError
        If any SQLAlchemy related errors occur while connecting to the database or manipulating the schema.

    Examples
    --------
    >>> from sqlalchemy.engine.url import URL
    >>> url_object = URL.create("postgresql", username="username", password="password", host="localhost", port=5432, database="test_db")
    >>> create_schema(url_object, drop_all=True)
    """

    engine = create_engine(url_object)

    if drop_all:
        Base.metadata.drop_all(engine)

    Base.metadata.create_all(engine)
