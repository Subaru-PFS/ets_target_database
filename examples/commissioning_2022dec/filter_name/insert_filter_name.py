#!/usr/bin/env python3

import argparse
import datetime
import sys

import numpy as np
import pandas as pd
import toml
from logzero import logger

from targetdb import targetdb

# from ..targetdb_api_utils import simple_update


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


# def update_ob_code(db, df_input, table=None, fetch_table=False):
#     n_input = len(df_input.index)
#     # df_ret = None
#     try:
#         print("trying to update data into {:s}...".format(table))
#         utcnow = datetime.datetime.utcnow()
#         # df_input["created_at"] = [utcnow] * n_input
#         df_input["updated_at"] = [utcnow] * n_input
#         print(df_input)
#         db.update(table, df_input)
#     except:
#         print("Unexpected error:", sys.exc_info()[0])
#         # print("no unique value in the input data is found. skip.")
#         exit()

#     if fetch_table:
#         res = db.fetch_all(table)
#         print(res)

#     return db


def main(conf: str, infile: str, dry_run: bool = False):

    logger.info(f"Load config file {conf}.")
    config = toml.load(conf)

    logger.info(f"Connect to the database.")
    db = targetdb.TargetDB(**dict(config["targetdb"]["db"]))
    db.connect()

    logger.info("Inserting data.")
    db = insert_simple(
        db,
        table="filter_name",
        csv=infile,
        return_defaults=False,
        fetch_table=True,
    )

    db.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "conf",
        type=str,
        help="Config file for the script to run. Must be a .toml file (mandatory)",
    )
    parser.add_argument(
        "--infile",
        type=str,
        help="Input csv",
    )

    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Dry-run (no update of the database)",
    )

    args = parser.parse_args()

    print(args)
    # exit()

    main(args.conf, args.infile, dry_run=args.dry_run)
