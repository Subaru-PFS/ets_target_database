#!/usr/bin/env python

import argparse
import sys

from . import create_schema

# from targetdb import generate_schema_markdown


def get_arguments():
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
    # parser.add_argument(
    #     "--schema_md",
    #     type=str,
    #     default=sys.stdout,
    #     help="Output markdown file to write tables in the database (Default: sys.stdout)",
    # )

    args = parser.parse_args()

    return args


# def main(dbinfo, schema_md=None, drop_all=False):
def main():

    args = get_arguments()

    print(args)

    create_schema(args.dbinfo, drop_all=args.drop_all)

    # generate_schema_markdown(schema_md=schema_md)


if __name__ == "__main__":

    # dbinfo = "postgresql://admin:admin@localhost:15432/targetdb_test"
    # # drop_all = True
    # drop_all = False

    # schema_md = "schema_targetdb_tables.md"

    main()

    # main(dbinfo, schema_md=schema_md, drop_all=drop_all)
