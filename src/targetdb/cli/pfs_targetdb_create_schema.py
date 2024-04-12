#!/usr/bin/env python

import argparse

from loguru import logger

from ..manage import create_schema
from ..utils import get_url_object, load_config


def get_arguments(desc=None):

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "-c",
        "--config",
        default=None,
        required=True,
        help="Database config file (.toml)",
    )
    parser.add_argument(
        "--drop_all",
        action="store_true",
        help="Drop all tables before creating schema. (Default: False)",
    )

    args = parser.parse_args()

    logger.info(f"Loading config file: {args.config}")
    config = load_config(args.config)

    return args, config


def main_create_schema():

    args, config = get_arguments(
        desc="Create tables of the target dabatabase in a database."
    )

    url_object = get_url_object(config)

    create_schema(url_object, drop_all=args.drop_all)


if __name__ == "__main__":
    pass
