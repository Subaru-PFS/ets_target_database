#!/usr/bin/env python3

import argparse
import datetime

import numpy as np
import pandas as pd
import toml
from astropy.table import Table
from logzero import logger
from targetdb import targetdb

from targetdb_api_utils import insert_simple
from targetdb_api_utils import join_backref_values


def load_data(infile):
    tb = Table.read(infile, format="ascii.ecsv")
    proposal_id = tb.meta["proposal_id"]
    df = tb.to_pandas()
    print(df)
    return df, proposal_id


def format_data(df, proposal_id):

    filter_bands = ["g", "r", "i", "z", "y", "j"]

    dfout = df.copy(deep=True)

    dfout.rename(
        columns={"input_catalog": "input_catalog_name"},
        inplace=True,
    )
    dfout["proposal_id"] = proposal_id
    dfout["target_type_name"] = "SCIENCE"

    lists_filtername = {"g": [], "r": [], "i": [], "z": [], "y": [], "j": []}

    for i in range(df.index.size):

        filter_name = df["filter_name"][i]

        if "APASS" in filter_name:
            filter_system = "sdss"
        elif "PS1" in filter_name:
            filter_system = "ps1"
        else:
            logger.error(f"Filter system is not registered. Check the code.")
            exit()

        for band in filter_bands:
            try:
                if np.isfinite(dfout[f"psf_mag_{band}"][i]) and np.isfinite(
                    dfout[f"psf_flux_{band}"][i]
                ):
                    lists_filtername[band].append(f"{band}_{filter_system}")
                else:
                    logger.warn(
                        f"NaN is found in the {band} flux and magnitude for the object {df['obj_id'][i]}. None is put there."
                    )
                    lists_filtername[band].append(None)
            except KeyError as e:
                logger.warn(
                    f"No {band} information is found in the data and the columns are set as NULL in the database."
                )
                lists_filtername[band].append(None)

    for band in filter_bands:
        dfout[f"filter_{band}"] = lists_filtername[band]

    print(dfout)

    return dfout


def main(conf, infile, dry_run=False):

    logger.info(f"Loading input data into dataframe")
    df, proposal_id = load_data(infile)

    df = format_data(df, proposal_id)

    logger.info(f"Load config file {conf}.")
    config = toml.load(conf)

    logger.info(f"Connect to the database.")
    db = targetdb.TargetDB(**dict(config["targetdb"]))
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

    logger.debug(df[["proposal_id", "input_catalog_name", "target_type_name"]])

    if dry_run:
        logger.info("Dry run. Do nothing.")
        pass
    else:
        logger.info(f"Insert data into the database.")
        db = insert_simple(db, table="target", df=df, fetch_table=False)

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
        default="../../../../external_data/commissioning_2022sep/stars_yamashita/targets_S22B-EN16.ecsv",
        help="Input file from Yamashita-san",
    )

    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Dry-run (no update of the database)",
    )

    args = parser.parse_args()

    main(args.conf, args.infile, args.dry_run)
