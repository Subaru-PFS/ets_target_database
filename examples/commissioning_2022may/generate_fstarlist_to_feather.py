#!/usr/bin/env python3

import os
import socket

import numpy as np
import pandas as pd


def main(
    csv,
    out_prefix,
    outdir=".",
    nline=None,
    catalog_name=None,
    version=None,
    brightest_mags=None,
    faintest_mags=None,
):

    # df = pd.read_csv(csv, comment="#")
    df = pd.read_csv(csv)

    n_target = len(df.index)

    column_mapper = {
        "GaiaEDR3_sourceid": "obj_id",
        "gPS1": "psf_mag_g",
        "rPS1": "psf_mag_r",
        "iPS1": "psf_mag_i",
        "zPS1": "psf_mag_z",
        "yPS1": "psf_mag_y",
        "gFluxJy": "psf_flux_g",
        "rFluxJy": "psf_flux_r",
        "iFluxJy": "psf_flux_i",
        "zFluxJy": "psf_flux_z",
        "yFluxJy": "psf_flux_y",
        "probfstar": "prob_f_star",
    }

    df.rename(columns=column_mapper, inplace=True)
    print(df)

    df["target_type_name"] = ["FLUXSTD"] * n_target
    df["input_catalog_name"] = [catalog_name] * n_target
    df["version"] = [version] * n_target

    df["epoch"] = df["epoch"].apply(lambda x: f"J{x:.1f}")

    # convert Jy to nJy
    for band in ["g", "r", "i", "z", "y"]:
        df[f"psf_flux_{band}"] = df[f"psf_flux_{band}"] * 1e9

    print(df)

    is_good = np.ones(n_target)
    for band in ["g", "r", "i", "z", "y"]:
        is_good = is_good & df[f"psf_mag_{band}"].between(
            brightest_mags[band], faintest_mags[band], inclusive="both"
        )

    df = df[is_good].copy()

    n_target_magcut = len(df.index)

    print(f"Number of objects before magnitude cut: {n_target}")
    print(f"Number of objects after magnitude cut : {n_target_magcut}")

    i_out = 0
    index_begin = 0

    while index_begin + nline < n_target_magcut:

        out_feather = os.path.join(
            outdir, "{:s}-{:08d}.feather".format(out_prefix, i_out)
        )
        print(out_feather)

        df[index_begin : index_begin + nline].reset_index().to_feather(out_feather)

        print(df[index_begin : index_begin + nline])

        index_begin += nline
        i_out += 1

    out_feather = os.path.join(outdir, "{:s}-{:08d}.feather".format(out_prefix, i_out))
    print(out_feather)
    df[index_begin:].reset_index().to_feather(out_feather)


if __name__ == "__main__":

    hostname = socket.gethostname()

    out_prefix = "fluxstd_v1.0"

    if hostname == "pfsa-usr01-gb.subaru.nao.ac.jp":
        csv = "../../../../star_catalog_ishigaki/commissioning_2022may/PFS_TargetList/Fstar_v1.0.csv"
        out_dir = "../../../../star_catalog_ishigaki/commissioning_2022may/PFS_TargetList/feather"
    else:
        csv = "../../../../star_catalogs_ishigaki/commissioning_2022may/Fstar_v1.0_probfstar0.5.csv"
        out_dir = "../../../../star_catalogs_ishigaki/commissioning_2022may/feather"

    catalog_name = "gaia_edr3"
    version = "1.0"

    brightest_mags = {"g": 14.0, "r": 14.0, "i": 14.0, "z": 14.0, "y": 14.0}
    faintest_mags = {"g": np.inf, "r": np.inf, "i": np.inf, "z": np.inf, "y": np.inf}

    nline = 1000000

    main(
        csv,
        out_prefix,
        outdir=out_dir,
        nline=nline,
        catalog_name=catalog_name,
        version=version,
        brightest_mags=brightest_mags,
        faintest_mags=faintest_mags,
    )
