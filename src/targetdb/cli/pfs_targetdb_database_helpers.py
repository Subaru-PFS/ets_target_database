#!/usr/bin/env python

import argparse
import sys
import time

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists, drop_database

from ..utils import add_database_rows, get_url_object, load_config, load_input_data


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


def get_arguments(desc=None):
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "-c",
        "--config",
        default=None,
        required=True,
        help="Database config file (.toml)",
    )

    args = parser.parse_args()

    logger.info(f"Loading config file: {args.config}")
    config = load_config(args.config)

    return args, config


def main_create_database():
    _, config = get_arguments(desc="Create a database on PostgreSQL.")
    url_object = get_url_object(config)
    engine = create_engine(url_object)

    if not database_exists(engine.url):
        logger.info(f"Creating database: {url_object.render_as_string()}")
        create_database(engine.url)
    else:
        logger.info(f"Database already exists: {url_object.render_as_string()}")


def main_drop_database():
    _, config = get_arguments(desc="Drop a database on PostgreSQL.")

    url_object = get_url_object(config)

    engine = create_engine(url_object)

    if database_exists(engine.url):
        print(
            f"WARNING: you are going to delete the database, {url_object.render_as_string()}"
        )
        proceed = query_yes_no("Proceed? ", default="no")
        if proceed:
            logger.info(f"Dropping database: {url_object.render_as_string()}")
            drop_database(engine.url)
    else:
        logger.info("Database does not exist: {url_object.render_as_string()}")


def get_arguments_with_config(desc=None):
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "input_file",
        help="Input file to be inserted to targetDB (CSV, ECSV, or Feather formats)",
    )
    parser.add_argument(
        "-c",
        "--config",
        default=None,
        required=True,
        help="Database config file (.toml)",
    )
    parser.add_argument("-t", "--table", required=True, help="Table name in targetDB")
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Commit the changes to the database (default: False)",
    )
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="Fetch all table entries and print (default: False)",
    )
    parser.add_argument(
        "--from-uploader",
        action="store_true",
        help="Target list from the PFS Target Uploader",
    )
    parser.add_argument(
        "--upload_id", type=str, default=None, help="Upload ID issued by the uploader"
    )
    parser.add_argument(
        "--proposal_id", type=str, default=None, help="Proposal ID (e.g., S24B-QT001)"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")

    args = parser.parse_args()

    logger.info(f"Loading config file: {args.config}")
    config = load_config(args.config)

    logger.info(f"Loading input data from {args.input_file} into a DataFrame")
    t_begin = time.time()
    df = load_input_data(args.input_file)
    t_end = time.time()
    logger.info(f"Loaded input data in {t_end - t_begin:.2f} seconds")

    return args, config, df


def main_insert():
    args, config, df = get_arguments_with_config(
        desc=("Insert data to targetDB from an input file")
    )

    add_database_rows(
        input_file=args.input_file,
        table=args.table,
        commit=args.commit,
        fetch=args.fetch,
        verbose=args.verbose,
        config=config,
        df=df,
        from_uploader=args.from_uploader,
        proposal_id=args.proposal_id,
        upload_id=args.upload_id,
        insert=True,
    )


def main_update():
    args, config, df = get_arguments_with_config(
        desc=("Update data in targetDB from an input file")
    )

    add_database_rows(
        input_file=args.input_file,
        table=args.table,
        commit=args.commit,
        fetch=args.fetch,
        verbose=args.verbose,
        config=config,
        df=df,
        from_uploader=args.from_uploader,
        proposal_id=args.proposal_id,
        upload_id=args.upload_id,
        update=True,
    )


if __name__ == "__main__":
    pass
