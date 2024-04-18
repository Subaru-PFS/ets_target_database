#!/usr/bin/env python

import argparse
import sys

from ..utils import generate_schema_markdown


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Create tables in targetDB in Markdown format."
    )
    parser.add_argument(
        "--output-file",
        type=str,
        # default=sys.stdout,
        default=None,
        help="Output markdown file to write tables in the database (Default: sys.stdout)",
    )

    args = parser.parse_args()

    return args


def main():

    args = get_arguments()

    print(args)

    generate_schema_markdown(output_file=args.output_file)


if __name__ == "__main__":
    main()
