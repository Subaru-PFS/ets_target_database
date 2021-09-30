#!/usr/bin/env python

import pandas as pd


def main(csv, out):
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


if __name__ == "__main__":
    csv = "../data/hscssp_pdr3_example_gdrop_2000.csv"
    out = "../data/target_s21b-en01.csv"
    main(csv, out)
