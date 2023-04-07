#!/usr/bin/env python

import argparse
import configparser
import datetime
import os

# import pprint
import sys

# import astropy.units as u
# import numpy as np
import pandas as pd
import toml

# from astropy.coordinates import SkyCoord
# from astropy.coordinates import search_around_sky
from astropy.table import Table
from logzero import logger

# from targetdb import models
from targetdb import targetdb


def get_arguments():
    parser = argparse.ArgumentParser(description="Test targetDB API")

    parser.add_argument(
        "conf",
        type=str,
        help="Config file for targetDB (required)",
    )

    # Option to reset tables
    parser.add_argument(
        "--reset",
        # action="store_true",
        nargs="*",
        metavar="all, target, fluxstd, sky",
        help="Reset one or more tables in targetdb before playing with it. Possible values are 'all', 'target', 'fluxstd', 'sky' ",
    )

    # Add skip flags to populate tables
    parser.add_argument(
        "--skip_proposal_category",
        action="store_true",
        help="Skip inserting test data into the proposal_category table (default: False)",
    )
    parser.add_argument(
        "--skip_proposal",
        action="store_true",
        help="Skip inserting test data into the proposal table (default: False)",
    )
    parser.add_argument(
        "--skip_input_catalog",
        action="store_true",
        help="Skip inserting test data into the input_catalog table (default: False)",
    )
    parser.add_argument(
        "--skip_target_type",
        action="store_true",
        help="Skip inserting test data into the target_type table (default: False)",
    )
    parser.add_argument(
        "--skip_target",
        action="store_true",
        help="Skip inserting test data into the target table (default: False)",
    )
    parser.add_argument(
        "--skip_fluxstd",
        action="store_true",
        help="Skip inserting test data into the fluxstd table (default: False)",
    )
    parser.add_argument(
        "--skip_sky",
        action="store_true",
        help="Skip inserting test data into the sky table (default: False)",
    )

    # Specify input data when populating tables
    parser.add_argument(
        "--proposal_category",
        default=None,
        type=str,
        help="Input CSV file for proposal categories (default: None)",
    )
    parser.add_argument(
        "--proposal",
        default=None,
        type=str,
        help="Input CSV file for proposals (default: None)",
    )
    parser.add_argument(
        "--input_catalog",
        default=None,
        type=str,
        help="Input CSV file for input catalogs (default: None)",
    )
    parser.add_argument(
        "--target_type",
        default=None,
        type=str,
        help="Input CSV file for target types (default: None)",
    )
    parser.add_argument(
        "--target",
        default=None,
        type=str,
        help="Sample file for targets (default: None)",
    )
    parser.add_argument(
        "--fluxstd",
        default=None,
        type=str,
        help="Sample file for fluxstds (default: None)",
    )
    parser.add_argument(
        "--sky",
        default=None,
        type=str,
        help="Sample file for sky (default: None)",
    )

    args = parser.parse_args()

    return args


def connect_db(conf=None):

    # config = configparser.ConfigParser()
    # config.read(conf)
    config = toml.load(conf)
    db = targetdb.TargetDB(**dict(config["targetdb"]))
    db.connect()

    return db


def update_simple(db, table=None, csv=None, df=None, fetch_table=False):
    if csv is not None and df is None:
        df_input = pd.read_csv(csv)
    elif csv is None and df is not None:
        df_input = df
    else:
        print("csv and df cannot be None at the same time. Exit.")
        exit()

    n_input = len(df_input.index)
    df_ret = None
    try:
        print("trying to update data into {:s}...".format(table))

        utcnow = datetime.datetime.utcnow()
        # df_input["created_at"] = [utcnow] * n_input
        df_input["updated_at"] = [utcnow] * n_input

        df_ret = db.update(table, df_input)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        # print("no unique value in the input data is found. skip.")
        exit()

    if fetch_table:
        res = db.fetch_all(table)
        print(res)

    # if return_defaults:
    #     return db, df_ret
    # else:
    return db


def insert_simple(
    db, table=None, csv=None, df=None, return_defaults=False, fetch_table=False
):

    if csv is not None and df is None:
        df_input = pd.read_csv(csv)
    elif csv is None and df is not None:
        df_input = df
    else:
        print("csv and df cannot be None at the same time. Exit.")
        exit()

    n_input = len(df_input.index)
    df_ret = None

    try:
        print("trying to insert data into {:s}...".format(table))

        utcnow = datetime.datetime.utcnow()
        df_input["created_at"] = [utcnow] * n_input
        df_input["updated_at"] = [utcnow] * n_input

        df_ret = db.insert(table, df_input, return_defaults=return_defaults)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        # print("no unique value in the input data is found. skip.")
        # exit()

    if fetch_table:
        res = db.fetch_all(table)
        print(res)

    if return_defaults:
        return db, df_ret
    else:
        return db


def join_backref_values(df, db=None, table=None, key=None, check_key=None):

    res = db.fetch_all(table)
    df_joined = df.merge(
        res,
        how="left",
        left_on=key,
        right_on=key,
    )
    # print(df_joined)
    if df_joined[check_key].isna().any():
        print("There is at least one non-existing {:s}.".format(check_key))
        exit()
    return df_joined


def insert_proposal(db, csv=None, fetch_table=False):
    # df_proposal = pd.read_csv("../data/proposal.csv")
    df_proposal = pd.read_csv(csv)
    n_proposal = len(df_proposal.index)

    df_joined = join_backref_values(
        df_proposal,
        db=db,
        table="proposal_category",
        key="proposal_category_name",
        check_key="proposal_category_id",
    )

    db = insert_simple(db, table="proposal", df=df_joined, fetch_table=fetch_table)

    return db


def insert_target(db, infile=None, fetch_table=False, proposal_id=None):

    _, ext = os.path.splitext(infile)

    logger.info("Loading data from {:s}".format(infile))

    if ext == ".csv":
        df = pd.read_csv(infile)
    elif ext == ".feather":
        df = pd.read_feather(infile)
    elif ext == ".fits":
        tb = Table.read(infile)
        df = tb.to_pandas()
        # FITS binary table's string is in bytecode. It has to be converted to utf-8.
        df["input_catalog"] = df["input_catalog"].apply(lambda x: x.decode())
        df["epoch"] = df["epoch"].apply(lambda x: x.decode())
    elif ext == ".ecsv":
        tb = Table.read(infile, format="ascii.ecsv")
        df = tb.to_pandas()
    else:
        logger.error("Filetype {:s} is not supported. Abort.".format(ext))

    df.rename(
        columns={"object_id": "obj_id", "input_catalog": "input_catalog_name"},
        inplace=True,
    )

    # copy dataframe (may not be needed)
    df_target_tmp = df.copy()

    if proposal_id is not None:
        df_target_tmp["proposal_id"] = [proposal_id] * len(df_target_tmp.index)

    df_target_tmp["target_type_name"] = ["SCIENCE"] * len(df_target_tmp.index)

    backref_tables = ["proposal", "input_catalog", "target_type"]
    backref_keys = ["proposal_id", "input_catalog_name", "target_type_name"]
    backref_check_keys = ["proposal_id", "input_catalog_id", "target_type_id"]

    for i in range(len(backref_tables)):
        df_target_tmp = join_backref_values(
            df_target_tmp,
            db=db,
            table=backref_tables[i],
            key=backref_keys[i],
            check_key=backref_check_keys[i],
        )

    db = insert_simple(db, table="target", df=df_target_tmp, fetch_table=fetch_table)

    return db


def insert_fluxstd(db, infile=None, fetch_table=False):

    _, ext = os.path.splitext(infile)

    logger.info("Loading data from {:s}".format(infile))

    if ext == ".csv":
        df = pd.read_csv(infile)
    elif ext == ".feather":
        df = pd.read_feather(infile)
    else:
        logger.error("Filetype {:s} is not supported. Abort.".format(ext))

    # copy dataframe (may not be needed)
    df_fluxstd_tmp = df.copy()

    backref_tables = ["input_catalog", "target_type"]
    backref_keys = ["input_catalog_name", "target_type_name"]
    backref_check_keys = ["input_catalog_id", "target_type_id"]

    for i in range(len(backref_tables)):
        df_fluxstd_tmp = join_backref_values(
            df_fluxstd_tmp,
            db=db,
            table=backref_tables[i],
            key=backref_keys[i],
            check_key=backref_check_keys[i],
        )

    db = insert_simple(db, table="fluxstd", df=df_fluxstd_tmp, fetch_table=fetch_table)

    return db


def insert_sky(db, infile=None, fetch_table=False):

    _, ext = os.path.splitext(infile)

    logger.info("Loading data from {:s}".format(infile))

    if ext == ".csv":
        df = pd.read_csv(infile)
    elif ext == ".feather":
        df = pd.read_feather(infile)
    else:
        logger.error("Filetype {:s} is not supported. Abort.".format(ext))

    # copy dataframe (may not be needed)
    df_tmp = df.copy()

    backref_tables = ["input_catalog", "target_type"]
    backref_keys = ["input_catalog_name", "target_type_name"]
    backref_check_keys = ["input_catalog_id", "target_type_id"]

    for i in range(len(backref_tables)):
        df_tmp = join_backref_values(
            df_tmp,
            db=db,
            table=backref_tables[i],
            key=backref_keys[i],
            check_key=backref_check_keys[i],
        )

    db = insert_simple(db, table="sky", df=df_tmp, fetch_table=fetch_table)

    return db


def main():

    args = get_arguments()

    logger.info(args)

    db = connect_db(args.conf)

    if args.reset:
        logger.info("Reset database tables.")
        for reset_scope in args.reset:
            if reset_scope == "all":
                db.reset_all()
            if reset_scope == "target":
                db.reset_target()
            if reset_scope == "fluxstd":
                db.reset_fluxstd()
            if reset_scope == "sky":
                db.reset_sky()

    if not args.skip_proposal_category:
        logger.info("Inserting sample data into the proposal_category table")
        db = insert_simple(
            db,
            table="proposal_category",
            csv=args.proposal_category,
            fetch_table=True,
        )

    if not args.skip_proposal:
        logger.info("Inserting sample data into the proposal table")
        db = insert_proposal(
            db,
            csv=args.proposal,
            fetch_table=True,
        )

    if not args.skip_input_catalog:
        logger.info("Inserting sample data into the input_catalog table")
        db = insert_simple(
            db,
            table="input_catalog",
            csv=args.input_catalog,
            fetch_table=True,
        )

    if not args.skip_target_type:
        logger.info("Inserting sample data into the target_type table")
        db = insert_simple(
            db,
            table="target_type",
            csv=args.target_type,
            fetch_table=True,
        )

    if not args.skip_target:
        logger.info("Inserting sample data into the target table")
        db = insert_target(
            db, infile=args.target, fetch_table=False, proposal_id="S23A-EN16"
        )

    if not args.skip_fluxstd:
        logger.info("Inserting sample data into the fluxstd table")
        db = insert_fluxstd(db, infile=args.fluxstd, fetch_table=False)

    if not args.skip_sky:
        logger.info("Inserting sample data into the sky table")
        db = insert_sky(db, infile=args.sky, fetch_table=False)

    db.close()


if __name__ == "__main__":
    main()
