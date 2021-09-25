#!/usr/bin/env python

import argparse

from sqlalchemy import create_engine
from sqlalchemy_utils import create_database
from sqlalchemy_utils import database_exists
from sqlalchemy_utils import drop_database


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Create targetDB itself on PostgreSQL."
    )
    parser.add_argument(
        "dbinfo",
        type=str,
        help="Database URL (postgresql://user:password@hostname:port/dbname)",
    )

    args = parser.parse_args()

    return args


def main_create_database():
    args = get_arguments()

    print(args)

    engine = create_engine(args.dbinfo)

    if not database_exists(engine.url):
        print("Creating database: {:s}".format(args.dbinfo))
        create_database(engine.url)
    else:
        print("Database already exists: {:s}".format(args.dbinfo))


def main_drop_database():
    args = get_arguments()

    print(args)

    engine = create_engine(args.dbinfo)

    if database_exists(engine.url):
        print("Dropping database: {:s}".format(args.dbinfo))
        drop_database(engine.url)
    else:
        print("Database does not exist: {:s}".format(args.dbinfo))


if __name__ == "__main__":
    main_create_database()
