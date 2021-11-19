#!/usr/bin/env python

import os

import pandas as pd

# from astropy import units as u
# from astropy.coordinates import SkyCoord
# from numpy.random import default_rng


def main(csv, out_prefix, outdir=".", nline=None):
    df = pd.read_csv(csv, comment="#")

    print(df)

    n_target = len(df.index)

    dfout = pd.DataFrame(
        {
            "proposal_id": ["S21B-EN16"] * n_target,
            "obj_id": df["objid"],
            "ra": df["ra"],
            "dec": df["decl"],
            # "epoch": df["epoch"],
            "epoch": ["J2000.0"] * n_target,
            # "tract": df["tract"],
            # "patch": df["patch"],
            "target_type_name": ["FLUXSTD"] * n_target,
            "input_catalog_name": ["ps1_dr2"] * n_target,
            "priority": [1] * n_target,
            "effective_exptime": df["exptime"],
            "psf_mag_g": df["gPS1"],
            "psf_mag_r": df["rPS1"],
            "psf_mag_i": df["iPS1"],
            "psf_mag_z": df["zPS1"],
            "psf_mag_y": df["yPS1"],
            "psf_flux_g": df["gFluxJy"] * 1e9,  # [Jy] --> [nJy]
            "psf_flux_r": df["rFluxJy"] * 1e9,  # [Jy] --> [nJy]
            "psf_flux_i": df["iFluxJy"] * 1e9,  # [Jy] --> [nJy]
            "psf_flux_z": df["zFluxJy"] * 1e9,  # [Jy] --> [nJy]
            "psf_flux_y": df["yFluxJy"] * 1e9,  # [Jy] --> [nJy]
            "prob_f_star": df["probfstar"],
        }
    )

    i_out = 0
    index_begin = 0

    while index_begin + nline < n_target:

        out_feather = os.path.join(
            outdir, "{:s}-{:06d}.feather".format(out_prefix, i_out)
        )
        print(out_feather)

        dfout[index_begin : index_begin + nline].reset_index().to_feather(out_feather)

        index_begin += nline
        i_out += 1

    out_feather = os.path.join(outdir, "{:s}-{:06d}.feather".format(out_prefix, i_out))
    print(out_feather)
    dfout[index_begin:].reset_index().to_feather(out_feather)


if __name__ == "__main__":

    csv = "../../../../star_catalogs_ishigaki/Fstar_v0.3.csv"
    out_prefix = "target_fstars_v0.3_s21b-en16"
    out_dir = "../../../../star_catalogs_ishigaki"

    nline = 1000000

    main(csv, out_prefix, outdir=out_dir, nline=nline)
