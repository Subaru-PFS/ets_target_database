#!/usr/bin/env python

import argparse
import configparser
import datetime
import sys

import astropy.units as u
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord
from astropy.coordinates import search_around_sky
from logzero import logger
from targetdb import models
from targetdb import targetdb


def get_arguments():
    parser = argparse.ArgumentParser(description="Test targetDB API")
    parser.add_argument(
        "conf",
        type=str,
        # default="targetdb_config.ini",
        help="Config file for targetDB",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset all tables in targetdb before playing with it. (Default: False)",
    )
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

    args = parser.parse_args()

    return args


def connect_db(conf=None):

    config = configparser.ConfigParser()
    config.read(conf)

    # print(dict(config["dbinfo"]))

    db = targetdb.TargetDB(**dict(config["dbinfo"]))

    db.connect()

    return db


def insert_simple(db, table=None, csv=None, df=None, return_defaults=False):

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


def insert_proposal(db):
    df_proposal = pd.read_csv("../data/proposal.csv")
    n_proposal = len(df_proposal.index)

    df_joined = join_backref_values(
        df_proposal,
        db=db,
        table="proposal_category",
        key="proposal_category_name",
        check_key="proposal_category_id",
    )

    db = insert_simple(db, table="proposal", df=df_joined)

    return db


def main():

    args = get_arguments()

    db = connect_db(args.conf)

    if args.reset:
        logger.info("Reset database tables.")
        db.reset()

    if not args.skip_proposal_category:
        logger.info("Inserting sample data into the proposal_category table")
        db = insert_simple(
            db, table="proposal_category", csv="../data/proposal_category.csv"
        )

    if not args.skip_proposal:
        logger.info("Inserting sample data into the proposal table")
        db = insert_proposal(db)

    if not args.skip_input_catalog:
        logger.info("Inserting sample data into the input_catalog table")
        db = insert_simple(db, table="input_catalog", csv="../data/input_catalog.csv")

    if not args.skip_target_type:
        logger.info("Inserting sample data into the target_type table")
        db = insert_simple(db, table="target_type", csv="../data/target_type.csv")

    db.close()


if __name__ == "__main__":
    # conf = "targetdb_config.ini"
    # reset = True
    # reset = False
    main()
