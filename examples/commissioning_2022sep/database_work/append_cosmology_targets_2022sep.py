#!/usr/bin/env python3

import argparse
import datetime

import numpy as np
import pandas as pd
import toml
from astropy import units as u
from astropy.table import Table
from logzero import logger
from targetdb import targetdb

from targetdb_api_utils import insert_simple
from targetdb_api_utils import join_backref_values


def load_data(infile, proposal_id, input_catalog, epoch_str="J2000.0"):

    # tb = Table.read(infile)
    df = pd.read_csv(
        infile,
        dtype={
            "object_id": np.int64,
            "ra": float,
            "dec": float,
            "specz_redshift": float,
            "g_cmodel_mag": float,
        },
    )
    df.rename(
        columns={"object_id": "obj_id", "g_cmodel_mag": "psf_mag_g"},
        inplace=True,
    )

    df["input_catalog_name"] = np.full(
        df.index.size, input_catalog, dtype=np.dtype("U256")
    )
    df["epoch"] = np.full(df.index.size, epoch_str, dtype=np.dtype("U256"))
    df["priority"] = np.full(df.index.size, 1.0, dtype=float)
    df["effective_exptime"] = np.full(df.index.size, 900.0, dtype=float)

    df["psf_flux_g"] = (df["psf_mag_g"].to_numpy() * u.ABmag).to("nJy").value

    # copy dataframe (not necessary)
    df_target_tmp = df.copy(deep=True)

    if proposal_id is not None:
        df_target_tmp["proposal_id"] = [proposal_id] * len(df_target_tmp.index)

    df_target_tmp["target_type_name"] = ["SCIENCE"] * len(df_target_tmp.index)

    logger.info(
        f"""
                {df_target_tmp}
                """
    )

    return df_target_tmp, proposal_id


def main(conf, infile, dry_run=False, proposal_id=None, input_catalog=None):

    logger.info(f"Loading input data into dataframe")
    df, proposal_id = load_data(infile, proposal_id, input_catalog)

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

    logger.debug(
        f"""
        {df[["proposal_id", "input_catalog_name", "target_type_name"]]}
        """
    )

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
        default="/work/monodera/Subaru-PFS/external_data/commissioning_2022sep/cosmology/hsc_pdr3_dud_deep23_247881.csv",
        help="Input file from Yabe-san",
    )

    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Dry-run (no update of the database)",
    )

    parser.add_argument(
        "--input_catalog",
        type=str,
        default="hscssp_pdr3_dud",
        help="Input catalog name (default: hscssp_pdr3_dud).",
    )
    parser.add_argument(
        "--proposal_id",
        type=str,
        default="S22B-EN16",
        help="Proposal ID to be assigned (default: S22B-EN16).",
    )

    args = parser.parse_args()

    main(args.conf, args.infile, args.dry_run, args.proposal_id, args.input_catalog)
