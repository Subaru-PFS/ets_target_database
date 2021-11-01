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
            # "epoch": ["J2000.0"] * n_target,
            "epoch": df["epoch"],
            # "tract": df["tract"],
            # "patch": df["patch"],
            "target_type_name": ["FLUXSTD"] * n_target,
            "input_catalog_name": ["ps1_dr2"] * n_target,
            "priority": [1] * n_target,
            "effective_exptime": df["exptime"],
            "prob_f_star": df["probfstar"],
        }
    )

    i_csv = 0
    index_begin = 0

    while index_begin + nline < n_target:

        out_csv = os.path.join(outdir, "{:s}-{:06d}.csv".format(out_prefix, i_csv))
        print(out_csv)

        dfout[index_begin : index_begin + nline].to_csv(out_csv, index=False)

        index_begin += nline
        i_csv += 1

    out_csv = os.path.join(outdir, "{:s}-{:06d}.csv".format(out_prefix, i_csv))
    print(out_csv)
    dfout[index_begin:].to_csv(out_csv, index=False)


if __name__ == "__main__":

    csv = "data/Fstar_v0.1.csv"
    out_prefix = "target_fstars_s21b-en16"
    nline = 1000000

    main(csv, out_prefix, outdir="data", nline=nline)
