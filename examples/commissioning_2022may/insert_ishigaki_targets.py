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


def load_data(infile, proposal_id=None):
    tb = Table.read(infile, format="ascii.ecsv")

    df = tb.to_pandas()
    print(df)

    if proposal_id is not None:
        return df, proposal_id
    else:
        return df, tb.meta["proposal_id"]


def format_data(df, proposal_id):

    # filter_bands = ["g", "r", "i", "z", "y", "j"]

    dfout = df.copy(deep=True)

    dfout.rename(
        columns={"input_catalogs": "input_catalog_name"},
        inplace=True,
    )
    dfout["proposal_id"] = proposal_id
    dfout["target_type_name"] = "SCIENCE"

    dfout.loc[
        (dfout["input_catalog_name"] == "GaiaEDR3"), "input_catalog_name"
    ] = "gaia_edr3"
    dfout.loc[
        (dfout["input_catalog_name"] == "M15_ENG"), "input_catalog_name"
    ] = "eng_m15"

    dfout.loc[dfout["pmra"].isna(), "pmra"] = 0.0
    dfout.loc[dfout["pmdec"].isna(), "pmdec"] = 0.0
    dfout.loc[dfout["parallax"].isna(), "parallax"] = 1.0e-7

    # lists_filtername = {"g": [], "r": [], "i": [], "z": [], "y": [], "j": []}

    # for i in range(df.index.size):

    #     filter_name = df["filter_name"][i]

    #     if "APASS" in filter_name:
    #         filter_system = "sdss"
    #     elif "PS1" in filter_name:
    #         filter_system = "ps1"
    #     else:
    #         logger.error(f"Filter system is not registered. Check the code.")
    #         exit()

    #     for band in filter_bands:
    #         try:
    #             if np.isfinite(dfout[f"psf_mag_{band}"][i]) and np.isfinite(
    #                 dfout[f"psf_flux_{band}"][i]
    #             ):
    #                 lists_filtername[band].append(f"{band}_{filter_system}")
    #             else:
    #                 logger.warn(
    #                     f"NaN is found in the {band} flux and magnitude for the object {df['obj_id'][i]}. None is put there."
    #                 )
    #                 lists_filtername[band].append(None)
    #         except KeyError as e:
    #             logger.warn(
    #                 f"No {band} information is found in the data and the columns are set as NULL in the database."
    #             )
    #             lists_filtername[band].append(None)

    # for band in filter_bands:
    #     dfout[f"filter_{band}"] = lists_filtername[band]

    print(dfout)

    return dfout


def main(conf, infile, dry_run=False):

    logger.info(f"Loading input data into dataframe")
    df, proposal_id = load_data(infile, proposal_id="S22A-EN16")
    df = format_data(df, proposal_id)

    # set up a dataframe for new input catalogs
    df_input_catalog = pd.DataFrame(
        {
            "input_catalog_id": [90001],
            "input_catalog_name": ["eng_m15"],
            "input_catalog_description": [
                "Messier 15 stars for the engineering observation"
            ],
        }
    )
    logger.info(f"Load config file {conf}.")
    config = toml.load(conf)

    logger.info(f"Connect to the database.")
    db = targetdb.TargetDB(**dict(config["targetdb"]))
    db.connect()

    db = insert_simple(db, table="input_catalog", df=df_input_catalog, fetch_table=True)
    # db.update("input_catalog", df_input_catalog)
    # exit()

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
        logger.debug("Dry run. Do nothing.")
        pass
    else:
        logger.info(f"Insert data into the database.")
        db = insert_simple(db, table="target", df=df, fetch_table=False)

    logger.info(f"Close the database.")
    db.close()


def fix_nan(conf, infile, dry_run=False):

    # logger.info(f"Loading input data into dataframe")
    # df, proposal_id = load_data(infile, proposal_id="S22A-EN16")
    # df = format_data(df, proposal_id)

    logger.info(f"Load config file {conf}.")
    config = toml.load(conf)

    logger.info(f"Connect to the database.")
    db = targetdb.TargetDB(**dict(config["targetdb"]))
    db.connect()

    logger.info(f"Fetch objects.")
    df_current = db.fetch_query(
        f"""SELECT target_id, pmra, pmdec, parallax, updated_at
            FROM target
            WHERE (pmra = 'NaN')
            OR (pmdec = 'NaN')
            OR (parallax= 'NaN')
            ORDER BY target_id;"""
    )

    print(df_current)

    df_update = df_current[
        ["target_id", "pmra", "pmdec", "parallax", "updated_at"]
    ].copy(deep=True)

    df_update.loc[df_update["pmra"].isna(), "pmra"] = 0.0
    df_update.loc[df_update["pmdec"].isna(), "pmdec"] = 0.0
    df_update.loc[df_update["parallax"].isna(), "parallax"] = 0.0

    utcnow = datetime.datetime.utcnow()
    df_update["updated_at"] = utcnow

    if dry_run:
        logger.debug("Dry run. Do nothing.")
        pass
    else:
        logger.info(
            f"Update the table with default values of pm/parallax parameters with the timestamp of {utcnow}"
        )
        db.update("target", df_update)

    df_check = db.fetch_query(
        f"""SELECT target_id, pmra, pmdec, parallax, updated_at
            FROM target
            WHERE (pmra = 'NaN')
            OR (pmdec = 'NaN')
            OR (parallax= 'NaN')
            ORDER BY target_id;"""
    )
    if df_check.empty:
        logger.info("No row with NaN values in parallax and proper motions.")
    else:
        logger.warning("Some rows contains NaN values in parallax and proper motions.")
        logger.warning(f"{df_check}")

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
        default="../../../external_data/commissioning_2022may/galactic_archaeology/ga_targets.ecsv",
        help="Input file from Ishigaki-san",
    )

    parser.add_argument(
        "--dry_run",
        action="store_true",
        # default="../../../external_data/commissioning_2022may/galactic_archaeology/",
        help="Dry-run (no update of the database)",
    )

    args = parser.parse_args()

    main(args.conf, args.infile, args.dry_run)

    # fix_nan(args.conf, args.infile, args.dry_run)
