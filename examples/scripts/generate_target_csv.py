#!/usr/bin/env python

import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord
from numpy.random import default_rng

rng = default_rng()


def main(csv, out, out_offset):
    df = pd.read_csv(csv, comment="#")

    print(df)

    n_target = len(df.index)

    dfout = pd.DataFrame(
        {
            "proposal_id": ["S21B-EN01"] * n_target,
            "obj_id": df["object_id"],
            "ra": df["ra"],
            "dec": df["dec"],
            "epoch": ["J2000.0"] * n_target,
            "tract": df["tract"],
            "patch": df["patch"],
            # "object_type_name": ["SCIENCE"] * n_target,
            "input_catalog_name": ["hscssp_pdr3_dud"] * n_target,
            "input_catalog_obj_id": df["object_id"],
        }
    )
    dfout.to_csv(out, index=False)

    df_offset = dfout.copy()

    coord = SkyCoord(
        dfout["ra"] * u.deg,
        dfout["dec"] * u.deg,
        frame="icrs",
    )
    coord_offset = coord.directional_offset_by(
        90 * u.deg,
        0.3 * u.arcsec,
        # rng.random(len(df_offset.index)) * 90.0 * u.deg,
        # [0.3 * u.arcsec] * len(df_offset.index),
    )

    df_offset["ra"] = coord_offset.ra
    df_offset["dec"] = coord_offset.dec

    df_offset.to_csv(out_offset, index=False)


def main2(csv1, csv2, out):
    df1 = pd.read_csv(csv1, comment="#")
    df2 = pd.read_csv(csv2, comment="#")

    n_target = 100

    dfout1 = pd.DataFrame(
        {
            "proposal_id": ["S21B-EN01"] * n_target,
            "obj_id": df1["object_id"][:n_target],
            "ra": df1["ra"][:n_target],
            "dec": df1["dec"][:n_target],
            "epoch": ["J2000.0"] * n_target,
            "tract": df1["tract"][:n_target],
            "patch": df1["patch"][:n_target],
            # "object_type_name": ["SCIENCE"] * n_target,
            "input_catalog_name": ["hscssp_pdr3_dud"] * n_target,
            "input_catalog_obj_id": df1["object_id"][:n_target],
        }
    )
    dfout2 = pd.DataFrame(
        {
            "proposal_id": ["S21B-EN16"] * n_target,
            "obj_id": df2["object_id"][:n_target],
            "ra": df2["ra"][:n_target],
            "dec": df2["dec"][:n_target],
            "epoch": ["J2000.0"] * n_target,
            "tract": df2["tract"][:n_target],
            "patch": df2["patch"][:n_target],
            # "object_type_name": ["SCIENCE"] * n_target,
            "input_catalog_name": ["hscssp_pdr3_dud"] * n_target,
            "input_catalog_obj_id": df2["object_id"][:n_target],
        }
    )

    dfout = pd.concat([dfout1, dfout2], ignore_index=True)

    dfout.to_csv(out, index=False)

    # dfout.to_csv(out, index=False)

    # df_offset = dfout.copy()

    # coord = SkyCoord(
    #     dfout["ra"] * u.deg,
    #     dfout["dec"] * u.deg,
    #     frame="icrs",
    # )
    # coord_offset = coord.directional_offset_by(
    #     90 * u.deg,
    #     0.3 * u.arcsec,
    #     # rng.random(len(df_offset.index)) * 90.0 * u.deg,
    #     # [0.3 * u.arcsec] * len(df_offset.index),
    # )

    # df_offset["ra"] = coord_offset.ra
    # df_offset["dec"] = coord_offset.dec

    # df_offset.to_csv(out_offset, index=False)


if __name__ == "__main__":

    csv1 = "../data/hscssp_pdr3_example_gdrop_2000.csv"
    out = "../data/target_s21b-en01.csv"
    out_offset = "../data/target_s21b-en01_offset.csv"
    # main(csv1, out, out_offset)

    csv2 = "../data/hscssp_pdr3_example_cleanobjects_100.csv"
    out_mix = "../data/target_s21b-en16.csv"
    main2(csv1, csv2, out_mix)
