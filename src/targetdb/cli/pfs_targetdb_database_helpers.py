#!/usr/bin/env python

import argparse
import os
import sys
import time
from datetime import datetime, timezone

import pandas as pd
from astropy.table import Table
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists, drop_database

from targetdb.targetdb import TargetDB

from .cli_utils import load_config, load_input_data


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
        print(
            "WARNING: you are going to delete the database, {:s}.".format(args.dbinfo)
        )
        proceed = query_yes_no("Proceed? ", default="no")
        if proceed:
            print("Dropping database: {:s}".format(args.dbinfo))
            drop_database(engine.url)
    else:
        print("Database does not exist: {:s}".format(args.dbinfo))


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


def join_backref_values(df, db=None, table=None, key=None, check_key=None):
    res = db.fetch_all(table)
    df_joined = df.merge(
        res,
        how="left",
        left_on=key,
        right_on=key,
    )
    if df_joined[check_key].isna().any():
        logger.error(f"There is at least one non-existing {check_key:s}.")
        raise ValueError(f"There is at least one non-existing {check_key:s}.")
    return df_joined


def add_backref_values(df, db=None, table=None):
    df_tmp = df.copy()
    backref_tables, backref_keys, backref_check_keys = [], [], []

    if table == "target":
        if "target_type_id" in df_tmp.columns:
            logger.info(
                "target_type_id is found in the DataFrame. Skip back reference detection."
            )
        elif "target_type_name" not in df_tmp.columns:
            logger.error("target_type_name is not found in the DataFrame.")
            raise KeyError("target_type_name is not found in the DataFrame.")
        else:
            if "upload_id" in df_tmp.columns:
                logger.info(
                    "upload_id is found in the DataFrame. Use it for back reference for input_catalog"
                )
                backref_tables = ["proposal", "input_catalog", "target_type"]
                backref_keys = ["proposal_id", "upload_id", "target_type_name"]
                backref_check_keys = ["proposal_id", "upload_id", "target_type_id"]
            else:
                logger.info(
                    "upload_id is not found in the DataFrame. Use input_catalog_name instead"
                )
                backref_tables = ["proposal", "input_catalog", "target_type"]
                backref_keys = ["proposal_id", "input_catalog_name", "target_type_name"]
                backref_check_keys = [
                    "proposal_id",
                    "input_catalog_id",
                    "target_type_id",
                ]
    elif table == "fluxstd":
        if "input_catalog_id" in df_tmp.columns:
            logger.info(
                "input_catalog_id is found in the DataFrame. Skip back reference detection."
            )
        elif "input_catalog_name" not in df_tmp.columns:
            logger.error("input_catalog_name is not found in the DataFrame.")
            raise KeyError("input_catalog_name is not found in the DataFrame.")
        else:
            backref_tables = ["input_catalog"]
            backref_keys = ["input_catalog_name"]
            backref_check_keys = ["input_catalog_id"]
    elif table == "sky":
        if "input_catalog_id" in df_tmp.columns:
            logger.info(
                "input_catalog_id is found in the DataFrame. Skip back reference detection."
            )
        elif "input_catalog_name" not in df_tmp.columns:
            logger.error("input_catalog_name is not found in the DataFrame.")
            raise KeyError("input_catalog_name is not found in the DataFrame.")
        else:
            backref_tables = ["input_catalog"]
            backref_keys = ["input_catalog_name"]
            backref_check_keys = ["input_catalog_id"]
    elif table == "proposal":
        if "proposal_category_id" in df_tmp.columns:
            logger.info(
                "proposal_category_id is found in the DataFrame. Skip back reference detection."
            )
        elif "proposal_category_name" not in df_tmp.columns:
            logger.error("proposal_category_name is not found in the DataFrame.")
            raise KeyError("proposal_category_name is not found in the DataFrame.")
        else:
            backref_tables = ["proposal_category"]
            backref_keys = ["proposal_category_name"]
            backref_check_keys = ["proposal_category_id"]

    # Join referenced values
    for i in range(len(backref_tables)):
        df_tmp = join_backref_values(
            df_tmp,
            db=db,
            table=backref_tables[i],
            key=backref_keys[i],
            check_key=backref_check_keys[i],
        )

    return df_tmp


def add_database_rows(insert=False, update=False):
    if not insert and not update:
        logger.warning("Neither insert nor update is selected. Exiting...")
        return

    args, config, df = get_arguments_with_config(
        desc=(
            "Insert data to targetDB from an input file"
            if insert
            else "Update data in targetDB from an input file"
        )
    )

    logger.info("Connecting to targetDB")
    db = TargetDB(**config["targetdb"]["db"])
    db.connect()

    if args.table in ["proposal", "fluxstd", "target", "sky"]:
        t_begin = time.time()
        df = add_backref_values(df, db=db, table=args.table)
        t_end = time.time()
        logger.info(f"Added back reference values in {t_end - t_begin:.2f} s")

    utcnow = datetime.now(timezone.utc)
    if insert:
        df["created_at"] = utcnow
    df["updated_at"] = utcnow

    if args.verbose:
        logger.debug(f"Working on the following DataFrame: \n{df}")

    try:
        t_begin = time.time()
        if args.commit:
            logger.info("Committing the changes to targetDB")
            if insert:
                db.insert(args.table, df, dry_run=False)
            elif update:
                db.update(args.table, df, dry_run=False)
        else:
            logger.info("No changes will be committed to targetDB (i.e., dry run)")
            if insert:
                db.insert(args.table, df, dry_run=True)
            elif update:
                db.update(args.table, df, dry_run=True)
        t_end = time.time()
        logger.info(
            f"Insert data to the {args.table} table successful for {df.index.size} rows in {args.input_file} ({t_end - t_begin:.2f} s)"
            if insert
            else f"Update data in the {args.table} table successful for {df.index.size} rows in {args.input_file} ({t_end - t_begin:.2f} s)"
        )
    except Exception as e:
        logger.error(f"Operation failed: {e}: {args.input_file}")
        raise

    if args.fetch:
        logger.info("Fetching all table entries")
        res = db.fetch_all(args.table)
        logger.info(f"Fetched entries in the {args.table} table: \n{res}")

    logger.info("Closing targetDB")
    db.close()


def main_insert():
    add_database_rows(insert=True)


def main_update():
    add_database_rows(update=True)


if __name__ == "__main__":
    pass
