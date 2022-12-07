#!/usr/bin/env python3

import glob
import os
from multiprocessing import Pool

import numpy as np
import pandas as pd
from logzero import logger


def my_err_cb(json_file):
    logger.error("ERROR callback args={}".format(json_file))


def my_cb(json_file):
    logger.info("SUCCESS callback args={}".format(json_file))


def convert_fluxstd_csv2feather_targetdb(csv_file, outdir, version, dry_run=False):
    df = pd.read_csv(csv_file)

    n_target = len(df.index)

    column_mapper = {
        "catalog": "input_catalog_name",
        #
        "gPS1": "psf_mag_g",
        "rPS1": "psf_mag_r",
        "iPS1": "psf_mag_i",
        "zPS1": "psf_mag_z",
        "yPS1": "psf_mag_y",
        #
        "gFluxJy": "psf_flux_g",
        "rFluxJy": "psf_flux_r",
        "iFluxJy": "psf_flux_i",
        "zFluxJy": "psf_flux_z",
        "yFluxJy": "psf_flux_y",
        #
        "gFluxJy_err": "psf_flux_error_g",
        "rFluxJy_err": "psf_flux_error_r",
        "iFluxJy_err": "psf_flux_error_i",
        "zFluxJy_err": "psf_flux_error_z",
        "yFluxJy_err": "psf_flux_error_y",
        #
        "probfstar": "prob_f_star",
    }

    df.rename(columns=column_mapper, inplace=True)
    logger.info(f"""{df}""")

    df["target_type_name"] = ["FLUXSTD"] * n_target

    df["filter_g"] = ["g_ps1"] * n_target
    df["filter_r"] = ["r_ps1"] * n_target
    df["filter_i"] = ["i_ps1"] * n_target
    df["filter_z"] = ["z_ps1"] * n_target
    df["filter_y"] = ["y_ps1"] * n_target

    if not df.loc[
        (df["input_catalog_name"] != "GaiaDR3"),
        "input_catalog_name",
    ].empty:
        logger.error("need to update the catalog name")
        logger.error(
            f"""{df.loc[df["input_catalog_name"] != "GaiaDR3", "input_catalog_name"]}"""
        )
        exit()
    else:
        df.loc[df["input_catalog_name"] == "GaiaDR3", "input_catalog_name"] = "gaia_dr3"

    df["version"] = [version] * n_target

    df["epoch"] = df["epoch"].apply(lambda x: f"J{x:.1f}")

    logger.info(f"""{df}""")

    logger.info(f"Number of objects before magnitude cut: {n_target}")

    out_prefix = os.path.splitext(os.path.basename(csv_file))[0]
    out_feather = os.path.join(outdir, f"{out_prefix}.feather")

    logger.info(f"Writing...: {out_feather}")
    df.to_feather(out_feather)


def main(csv_files, outdir=".", version=None, processes=32, dry_run=False):

    for i in range(len(csv_files)):
        with Pool(processes=processes) as pool:
            pool.apply_async(
                convert_fluxstd_csv2feather_targetdb,
                args=(csv_files[i], out_dir, version),
                kwds=dict(dry_run=dry_run),
                callback=my_cb,
                error_callback=my_err_cb,
            )
            pool.close()
            pool.join()


if __name__ == "__main__":

    work_dir = "/work/monodera/Subaru-PFS/external_data/commissioning_2022nov/fluxstd/Fstar_v2.0"

    in_dir = os.path.join(work_dir, "csv")
    csv_files = glob.glob(in_dir + "/*.csv")

    out_dir = os.path.join(work_dir, "feather", "v2.1")

    version = "2.1"

    main(csv_files, outdir=out_dir, version=version)
