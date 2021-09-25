#!/usr/bin/env python

import argparse
import sys

from .. import create_schema


def get_arguments():
    parser = argparse.ArgumentParser(description="Create the schema in targetDB.")
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

    args = parser.parse_args()

    return args


def main():

    args = get_arguments()

    print(args)

    create_schema(args.dbinfo, drop_all=args.drop_all)


if __name__ == "__main__":
    main()
