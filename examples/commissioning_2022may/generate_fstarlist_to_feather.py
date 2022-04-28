#!/usr/bin/env python

import os

import pandas as pd


def main(
    csv,
    out_prefix,
    outdir=".",
    nline=None,
    proposal_id=None,
    catalog_name=None,
    version=None,
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

    df["proposal_id"] = [proposal_id] * n_target
    df["target_type_name"] = ["FLUXSTD"] * n_target
    df["input_catalog_name"] = [catalog_name] * n_target
    df["version"] = [version] * n_target

    df["epoch"] = df["epoch"].apply(lambda x: f"J{x:.1f}")

    # convert Jy to nJy
    for band in ["g", "r", "i", "z", "y"]:
        df[f"psf_flux_{band}"] = df[f"psf_flux_{band}"] * 1e9

    print(df)

    i_out = 0
    index_begin = 0

    while index_begin + nline < n_target:

        out_feather = os.path.join(
            outdir, "{:s}-{:08d}.feather".format(out_prefix, i_out)
        )
        print(out_feather)

        df[index_begin : index_begin + nline].reset_index().to_feather(out_feather)

        print(df[index_begin : index_begin + nline])

        index_begin += nline
        i_out += 1

    out_feather = os.path.join(outdir, "{:s}-{:06d}.feather".format(out_prefix, i_out))
    print(out_feather)
    df[index_begin:].reset_index().to_feather(out_feather)


if __name__ == "__main__":

    csv = "../../../../star_catalogs_ishigaki/commissioning_2022may/Fstar_v1.0_probfstar0.5.csv"
    out_prefix = "target_fstars_v1.0_s22a-en16"
    out_dir = "../../../../star_catalogs_ishigaki/commissioning_2022may/feather"
    catalog_name = "gaia_edr3"
    proposal_id = "S22A-EN16"
    version = "1.0"

    nline = 1000000

    main(
        csv,
        out_prefix,
        outdir=out_dir,
        nline=nline,
        proposal_id=proposal_id,
        catalog_name=catalog_name,
        version=version,
    )
