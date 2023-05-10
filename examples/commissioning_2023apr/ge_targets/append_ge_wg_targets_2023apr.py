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

    bands = ["g"]

    df = pd.read_csv(
        infile,
        dtype={
            "obj_id": np.int64,
            "ra": float,
            "dec": float,
            "mag": float,
            "priority": float,
            "components": str,
        },
    )

    #column_rename_mapper = {"object_id": "obj_id"}
    column_rename_mapper = {"mag": "psf_mag_g"}

    df.rename(columns=column_rename_mapper, inplace=True)

    df["input_catalog_name"] = [input_catalog] * df.index.size
    df["epoch"] = [epoch_str] * df.index.size
    #df["priority"] = np.full(df.index.size, 1.0, dtype=float)
    df["effective_exptime"] = np.full(df.index.size, 7200.0, dtype=float)
    df["psf_mag_error_g"] = np.full(df.index.size, 0.0, dtype=float)
    df["psf_flux_g"] = np.full(df.index.size, 0.0, dtype=float)
    df["psf_flux_error_g"] = np.full(df.index.size, 0.0, dtype=float)

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

    #if proposal_id is not None:
    #    np.random.seed(0)
    #    proposal_ids = ['S23A-QN900', 'S23A-QN901', 'S23A-QN902', 'S23A-QN903']
    #    df_target_tmp["proposal_id"] = list(np.random.choice(proposal_ids, len(df_target_tmp.index)))
    proposal_ids = []
    for c in df["components"]:
        if c=='lae':
            proposal_ids.append('S23A-QN900')
        elif c=='kdm':
            proposal_ids.append('S23A-QN900')
        elif c=='amz':
            proposal_ids.append('S23A-QN901')
        elif c=='fms':
            proposal_ids.append('S23A-QN902')
        elif c=='agn':
            proposal_ids.append('S23A-QN903')

    df_target_tmp["proposal_id"] = proposal_ids
    df_target_tmp["target_type_name"] = ["SCIENCE"] * len(df_target_tmp.index)

    logger.info(
        f"""{df_target_tmp}
        """
    )

    return df_target_tmp, proposal_id


def fill_ob_code(df, tag):
    # ob_codes = df['obj_id'].
    df["obj_id"].fillna(-1, inplace=True)

    ob_codes = (
        df["obj_id"].astype(np.int64).astype(str)
        + "_"
        + tag
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

    tag = infile.split('/')[-1].split('.csv')[0]
    df = fill_ob_code(df, tag)

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
