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


def update_ob_code(db, df_input, table=None, fetch_table=False):
    n_input = len(df_input.index)
    # df_ret = None
    try:
        print("trying to update data into {:s}...".format(table))
        utcnow = datetime.datetime.utcnow()
        # df_input["created_at"] = [utcnow] * n_input
        df_input["updated_at"] = [utcnow] * n_input
        print(df_input)
        db.update(table, df_input)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        # print("no unique value in the input data is found. skip.")
        exit()

    if fetch_table:
        res = db.fetch_all(table)
        print(res)

    return db


def fill_ob_code(df):
    # ob_codes = df['obj_id'].

    print(df["obj_id"][pd.isna(df["obj_id"])].size)
    print(df.dtypes)

    df["obj_id"].fillna(-1, inplace=True)
    print(df["obj_id"][pd.isna(df["obj_id"])].size)
    print(df.dtypes)

    ob_codes = (
        df["obj_id"].astype(np.int64).astype(str)
        + "_"
        + df["target_id"].astype(np.int64).astype(str)
    )

    # res_str = np.full(ob_codes.index.size, "r_", dtype=str)
    res_str = np.array(["r_"] * ob_codes.index.size, dtype=str)
    res_str[df["is_medium_resolution"]] = "m_"

    print(res_str)

    df["ob_code"] = np.char.add(res_str, ob_codes.to_numpy(dtype=str))

    print(df["ob_code"])

    return df[["target_id", "ob_code"]]


def main(conf: str, dry_run: bool = False):

    logger.info(f"Load config file {conf}.")
    config = toml.load(conf)

    logger.info(f"Connect to the database.")
    db = targetdb.TargetDB(**dict(config["targetdb"]["db"]))
    db.connect()

    df_all = db.fetch_all("target")
    # df_all = db.fetch_query("SELECT * FROM target LIMIT 1;")

    # print(df_all["ob_code"])
    # exit()

    df_for_update = fill_ob_code(df_all)

    print(df_for_update)

    if not dry_run:
        logger.info("Updating target table for OB code")
        db = update_ob_code(db, df_for_update, table="target")
    else:
        logger.info("Dry run. Do nothing.")

    db.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "conf",
        type=str,
        help="Config file for the script to run. Must be a .toml file (mandatory)",
    )

    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Dry-run (no update of the database)",
    )

    args = parser.parse_args()

    print(args)
    # exit()

    main(args.conf, dry_run=args.dry_run)
