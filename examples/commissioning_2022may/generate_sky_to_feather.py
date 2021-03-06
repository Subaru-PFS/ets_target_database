#!/usr/bin/env python3

import json
import os

import numpy as np
import pandas as pd


def main(
    json_file,
    out_prefix,
    outdir=".",
    nline=None,
    # proposal_id=None,
    # catalog_name=None,
    version=None,
):

    with open(json_file, "r") as f:
        data = json.load(f)

    n_obj = len(data["objid"])

    tract = int(data["imgfile"][-13:-9])
    patch = int(data["imgfile"][-8:-5].replace(",", "0"))

    df = pd.DataFrame(
        {
            "obj_id": np.arange(n_obj),
            "obj_id_orig": data["objid"],
            "ra": data["ra"],
            "dec": data["dec"],
            "epoch": ["J2000.0"] * n_obj,
            "tract": [tract] * n_obj,
            "patch": [patch] * n_obj,
            "target_type_name": ["SKY"] * n_obj,
            "input_catalog_name": ["sky_hscssp_s21a_wide"] * n_obj,
            "mag_thresh": [data["magThresh"]] * n_obj,
            "version": [version] * n_obj,
        }
    )
    print(df)

    i_out = 0
    index_begin = 0

    while index_begin + nline < n_obj:

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

    work_dir = "../../../external_data/commissioning_2022may/sky_murata/"

    json_file = os.path.join(work_dir, "skypos_s21a_wide_9700_7,1.json")
    out_prefix = "skypos_s21a_wide_9700_7,1"
    out_dir = os.path.join(work_dir, "feather")
    version = "20220427"

    nline = 1000000

    main(
        json_file,
        out_prefix,
        outdir=out_dir,
        nline=nline,
        # proposal_id=proposal_id,
        # catalog_name=catalog_name,
        version=version,
    )
