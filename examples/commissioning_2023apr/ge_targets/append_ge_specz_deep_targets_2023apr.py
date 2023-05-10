#!/usr/bin/env python3

import argparse
import datetime

import numpy as np
import pandas as pd
import toml
from astropy import units as u
from astropy.table import Table
from logzero import logger
from targetdb_api_utils import insert_simple
from targetdb_api_utils import join_backref_values

from targetdb import targetdb

pd.set_option("display.max_columns", None)


def load_data(infile, proposal_id, input_catalog, epoch_str="J2000.0"):

    bands = ["g", "r", "i", "z", "y"]

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

    column_rename_mapper = {"object_id": "obj_id"}
    for band in bands:
        if f"{band}_cmodel_mag" in df.keys():
            column_rename_mapper[f"{band}_cmodel_mag"] = f"psf_mag_{band}"
        if f"{band}_cmodel_magerr" in df.keys():
            column_rename_mapper[f"{band}_cmodel_magerr"] = f"psf_mag_error_{band}"

    df.rename(columns=column_rename_mapper, inplace=True)
    df["proposal_id"] = [proposal_id] * df.index.size
    df["input_catalog_name"] = [input_catalog] * df.index.size
    df["epoch"] = [epoch_str] * df.index.size
    df["priority"] = np.full(df.index.size, 1.0, dtype=float)
    df["effective_exptime"] = np.full(df.index.size, 900.0, dtype=float)

    def error_mag2flux(flux, magerr):
        err = (np.log(10.0) / 2.5) * flux * magerr
        return err

    for band in bands:
        if f"psf_mag_{band}" in df.keys():
            df[f"psf_flux_{band}"] = (
                (df[f"psf_mag_{band}"].to_numpy() * u.ABmag).to("nJy").value
            )
        if f"psf_mag_error_{band}" in df.keys():
            df[f"psf_flux_error_{band}"] = error_mag2flux(
                df[f"psf_flux_{band}"], df[f"psf_mag_error_{band}"]
            )

    # copy dataframe (not necessary)
    df_target_tmp = df.copy(deep=True)

    df_target_tmp["target_type_name"] = ["SCIENCE"] * len(df_target_tmp.index)

    logger.info(
        f"""{df_target_tmp}
        """
    )

    return df_target_tmp, proposal_id


def fill_ob_code(df):
    # ob_codes = df['obj_id'].
    df["obj_id"].fillna(-1, inplace=True)

    ob_codes = (
        df["obj_id"].astype(np.int64).astype(str)
        + "_"
        + "yabe_ge_deep_specz_2023apr"
    )

    df["ob_code"] = np.char.add("r_", ob_codes.to_numpy(dtype=str))

    print(df["ob_code"])

    return df


def main(conf, infile, dry_run=False, proposal_id=None, input_catalog=None):

    logger.info(f"Loading input data into dataframe")
    df, proposal_id = load_data(infile, proposal_id, input_catalog)

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

    logger.debug(
        f"""
        {df[["obj_id", "proposal_id", "input_catalog_name", "target_type_name"]]}
        """
    )

    df = fill_ob_code(df)

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
        default="S22B-EN16-CO",
        help="Proposal ID to be assigned (default: S22B-EN16).",
    )

    args = parser.parse_args()

    main(args.conf, args.infile, args.dry_run, args.proposal_id, args.input_catalog)
