#!/usr/bin/env python3

import argparse

import numpy as np
import toml
from astropy.table import Table
from logzero import logger
from pfs.utils.fiberids import FiberIds
from targetdb import targetdb

from targetdb_api_utils import join_backref_values


def load_ref_catalog(infile, db):

    logger.info(f"Load the reference catalog ({infile})")
    tbref = Table.read(infile)
    proposal_id = tbref.meta["proposal_id"]

    dfref = tbref.to_pandas()
    dfref.rename(
        columns={"input_catalog": "input_catalog_name"},
        inplace=True,
    )
    dfref["proposal_id"] = proposal_id
    dfref["target_type_name"] = "SCIENCE"

    backref_tables = ["proposal", "input_catalog", "target_type"]
    backref_keys = ["proposal_id", "input_catalog_name", "target_type_name"]
    backref_check_keys = ["proposal_id", "input_catalog_id", "target_type_id"]

    for i in range(len(backref_tables)):
        dfref = join_backref_values(
            dfref,
            db=db,
            table=backref_tables[i],
            key=backref_keys[i],
            check_key=backref_check_keys[i],
        )

    return dfref


def load_design(pfs_design, db):
    logger.info(f"Load the pfsDesign file ({pfs_design})")
    tb = Table.read(pfs_design, hdu=1)
    return tb


def check_calibstars(pfs_design, conf=None, ref=None):

    config = toml.load(conf)

    logger.info(f"Connect to the database.")
    db = targetdb.TargetDB(**dict(config["targetdb"]))
    db.connect()

    # NOTE: the result is a pandas.DataFrame object
    df_ref = load_ref_catalog(ref, db)

    # NOTE: the result is an astropy.Table object
    tb_design = load_design(pfs_design, db)

    logger.info("Load the grand fiber map")
    gfm = FiberIds()  # 2604

    logger.info("Check reference objects in pfsDesign")
    is_matched = False

    for i in range(df_ref.index.size):
        idx_match = tb_design["objId"] == df_ref["obj_id"][i]
        if np.any(idx_match):
            is_matched = True
            fiber_id = tb_design["fiberId"][idx_match].value[0]
            logger.info(
                f"""Match in the catalog found!
                obj_id (ref): {df_ref['obj_id'][i]}
                obj_id (design): {tb_design["objId"][idx_match].value[0]}
                input_catalog_name: {df_ref['input_catalog_name'][i]}
                (ra_ref, dec_ref) = ({df_ref['ra'][i]}, {df_ref['dec'][i]})
                (ra_design, dec_design) = ({df_ref['ra'][i]}, {df_ref['dec'][i]})
                fiberId: {fiber_id}
                cobraId: {gfm.cobraId[fiber_id - 1]}
                spectrograph: {gfm.spectrographId[fiber_id - 1]}
                pfiNominal: ({tb_design["pfiNominal"][idx_match].value[0][0]:.3f}, {tb_design["pfiNominal"][idx_match].value[0][1]:.3f})"""
            )

    logger.info("Close connection to the database")
    db.close()

    if not is_matched:
        logger.warning("No match found in the pfsDesign.")

    return is_matched


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "pfs_design", type=str, help="pfsDesign file with the full path."
    )
    parser.add_argument(
        "--conf",
        type=str,
        default=None,
        help="Configuration file (.toml). Same as the main script.",
    )
    parser.add_argument(
        "--ref",
        type=str,
        default="targets_S22A-EN16.ecsv",
        help="input file for Yamashita-san's catalog. (Default: targets_S22A-EN16.ecsv)",
    )

    args = parser.parse_args()

    is_matched = check_calibstars(args.pfs_design, args.conf, args.ref)
