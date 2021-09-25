#!/usr/bin/env python

import argparse
import sys

from .. import generate_schema_markdown


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Create tables in targetDB in Markdown format."
    )
    parser.add_argument(
        "--schema_md",
        type=str,
        default=sys.stdout,
        help="Output markdown file to write tables in the database (Default: sys.stdout)",
    )

    args = parser.parse_args()

    return args


def main():

    args = get_arguments()

    print(args)

    generate_schema_markdown(schema_md=args.schema_md)


if __name__ == "__main__":
    main()
