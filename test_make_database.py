#!/usr/bin/env python

import argparse
import sys

from targetdb import create_schema
from targetdb import generate_schema_markdown


def main(dbinfo, schema_md=None, drop_all=False):

    create_schema(dbinfo, drop_all=drop_all)

    generate_schema_markdown(schema_md=schema_md)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Create targetDB on PostgreSQL.")
    parser.add_argument(
        "dbinfo",
        type=str,
        help="Database URL (postgresql://user:password@hostname:port/dbname)",
    )
    parser.add_argument(
        "--drop_all",
        action="store_true",
        help="Drop all tables before creating schema. (Default: False)",
    )
    parser.add_argument(
        "--schema_md",
        type=str,
        default=sys.stdout,
        help="Output markdown file to write tables in the database (Default: sys.stdout)",
    )

    args = parser.parse_args()

    print(args)

    dbinfo = args.dbinfo
    drop_all = args.drop_all
    schema_md = args.schema_md

    # dbinfo = "postgresql://admin:admin@localhost:15432/targetdb_test"
    # # drop_all = True
    # drop_all = False

    # schema_md = "schema_targetdb_tables.md"

    main(dbinfo, schema_md=schema_md, drop_all=drop_all)
