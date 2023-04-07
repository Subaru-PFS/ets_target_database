#!/usr/bin/env python3

import argparse
import datetime

import numpy as np
import pandas as pd
import toml
from astropy.table import Table
from logzero import logger
from targetdb_api_utils import insert_simple
from targetdb_api_utils import join_backref_values
from targetdb_api_utils import update_simple

from targetdb import targetdb


def load_data(infile):
    tb = Table.read(infile, format="ascii.ecsv")
    # proposal_id = tb.meta["proposal_id"]
    df = tb.to_pandas()
    print(df)
    return df


def format_data(df, proposal_id):

    dfout = df.copy(deep=True)

    dfout.rename(
        columns={"input_catalogs": "input_catalog_name"},
        inplace=True,
    )

    df_tmp = dfout.loc[
        (dfout["input_catalog_name"] != "Gaia")
        & (dfout["input_catalog_name"] != "NGC1904_ENG")
        & (dfout["input_catalog_name"] != "NGC2419_ENG")
        & (dfout["input_catalog_name"] != "NGC5272_ENG")
        & (dfout["input_catalog_name"] != "NGC5904_ENG")
    ]

    if not df_tmp.empty:
        logger.error("Unexpected input_catalog_name found. Exiting.")
        exit()

    catalog_name_mapper = {
        "Gaia": "gaia_dr3",
        "NGC1904_ENG": "eng_ngc1904",
        "NGC2419_ENG": "eng_ngc2419",
        "NGC5272_ENG": "eng_ngc5272",
        "NGC5904_ENG": "eng_ngc5904",
    }
    for k, v in catalog_name_mapper.items():
        dfout.loc[dfout["input_catalog_name"] == k, "input_catalog_name"] = v

    df_tmp = dfout.loc[
        dfout["epoch"] != "J2000",
    ]

    if not df_tmp.empty:
        logger.error("Unexpected epoch other than J2000 found. Exiting.")
        exit()

    dfout.loc[dfout["epoch"] == "J2000", "epoch"] = "J2000.0"

    dfout["proposal_id"] = proposal_id
    dfout["target_type_name"] = "SCIENCE"

    # if df["filter"][0] == "V":
    #    dfout["filter_g"] = ["v_johnson" for _ in range(df.index.size)]
    # elif df["filter"][0] == "GaiaG":
    #    dfout["filter_g"] = ["g_gaia" for _ in range(df.index.size)]
    dfout["filter_g"] = ["g_gaia" for _ in range(df.index.size)]
    dfout["psf_mag_g"] = df["magnitude"].astype(np.float64)

    print(dfout)

    return dfout


def fill_ob_code(df):
    # ob_codes = df['obj_id'].
    df["obj_id"].fillna(-1, inplace=True)

    ob_codes = (
        df["obj_id"].astype(np.int64).astype(str)
        + "_"
        + "ishigaki_ga_2023feb"
    )

    df["ob_code"] = np.char.add("r_", ob_codes.to_numpy(dtype=str))

    print(df["ob_code"])

    return df


def main(conf, infile, proposal_id=None, dry_run=False):

    logger.info(f"Loading input data into dataframe")
    df = load_data(infile)

    df = format_data(df, proposal_id)

    logger.info(f"Load config file {conf}.")
    config = toml.load(conf)

    logger.info(f"Connect to the database.")
    db = targetdb.TargetDB(**dict(config["targetdb"]["db"]))
    db.connect()

    backref_tables = ["proposal", "input_catalog", "target_type"]
    backref_keys = ["proposal_id", "input_catalog_name", "target_type_name"]
    backref_check_keys = ["proposal_id", "input_catalog_id", "target_type_id"]

    for i in range(len(backref_tables)):
        df = join_backref_values(
            df,
            db=db,
            table=backref_tables[i],
            key=backref_keys[i],
            check_key=backref_check_keys[i],
        )

    # logger.info(f"{df}")
    logger.debug(df[["proposal_id", "input_catalog_name", "target_type_name"]])

    df = fill_ob_code(df)
    # print(df['filter_g'])

    if not dry_run:
        logger.info(f"Insert data into the database.")
        db = insert_simple(
            db,
            table="target",
            df=df,
            fetch_table=False,
        )
    else:
        logger.info(f"{dry_run=}")
        logger.info("Dry run. Do nothing.")

    logger.info(f"Close the database.")
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
        default=None,
        help="Input file from Ishigaki-san",
    )

    parser.add_argument(
        "--proposal_id",
        type=str,
        default="S23A-EN16",
        help="proposal id (default: S23A-EN16)",
    )

    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Dry-run (no update of the database)",
    )

    args = parser.parse_args()

    print(args)
    # exit()

    main(
        args.conf,
        args.infile,
        dry_run=args.dry_run,
        proposal_id=args.proposal_id,
    )
