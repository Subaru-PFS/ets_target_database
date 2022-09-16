#!/usr/bin/env python3

import glob
import gzip
import json
import os

import numpy as np
import pandas as pd
from logzero import logger


def main(work_dir, work_subdirs, catalog_names, out_dir, version):

    # def main(
    #     json_file,
    #     out_prefix,
    #     outdir=".",
    #     nline=None,
    #     # proposal_id=None,
    #     # catalog_name=None,
    #     version=None,
    # ):

    for subdir, catalog_name in zip(work_subdirs, catalog_names):
        dir_path = os.path.join(work_dir, subdir)

        json_files = glob.glob(os.path.join(dir_path, "*.json*"))

        # for i in range(len(json_files)):
        for i in range(1):

            file_basename = os.path.basename(json_files[i])

            if "json.gz" in json_files[i]:
                out_prefix = file_basename.replace(".json.gz", "")
                with gzip.open(json_files[i], "r") as f:
                    data = json.loads(f.read().decode("utf-8"))
            else:
                out_prefix = file_basename.replace(".json", "")
                with open(json_files[i], "r") as f:
                    data = json.load(f)

            # keys in JSON
            # ['objid', 'ra', 'dec', 'magThresh', 'tract']
            json_keys = data.keys()
            print(json_keys)

            n_obj = len(data["objid"])

            if ("imgfile" in json_keys) and (imgfile is not None):
                logger.info(
                    "imgfile is found. trying to extract tract/patch information."
                )
                tract = np.full(n_obj, int(data["imgfile"][-13:-9]), dtype=int)
                patch = np.full(
                    n_obj, int(data["imgfile"][-8:-5].replace(",", "0")), dtype=int
                )
            elif "tract" in json_keys:
                logger.info(
                    "Tract is found in the keys, while patch is not found. Use None for patch."
                )
                tract = np.full(n_obj, data["tract"])
                patch = [None] * n_obj
            else:
                logger.warning(
                    "Both tract and patch information are not found. Use None for them."
                )
                tract = [None] * n_obj
                patch = [None] * n_obj

            if type(data["magThresh"]) is list:
                mag_thresh = data["magThresh"]
            else:
                mag_thresh = [data["magThresh"]] * n_obj

            df = pd.DataFrame(
                {
                    "obj_id": np.arange(n_obj),
                    "obj_id_orig": data["objid"],
                    "ra": data["ra"],
                    "dec": data["dec"],
                    "epoch": ["J2000.0"] * n_obj,
                    "tract": tract,
                    "patch": patch,
                    "target_type_name": ["SKY"] * n_obj,
                    "input_catalog_name": [catalog_name] * n_obj,
                    "mag_thresh": [data["magThresh"]] * n_obj,
                    "version": [version] * n_obj,
                }
            )
            print(df)

            out_feather = os.path.join(
                out_dir, f"{out_prefix}.feather".format(out_prefix)
            )
            print(out_feather)

            # df.to_feather(out_feather)

            # i_out = 0
            # index_begin = 0

            # while index_begin + nline < n_obj:

            #     out_feather = os.path.join(
            #         out_dir, "{:s}-{:08d}.feather".format(out_prefix, i_out)
            #     )
            #     print(out_feather)

            #     df[index_begin : index_begin + nline].reset_index().to_feather(
            #         out_feather
            #     )

            #     print(df[index_begin : index_begin + nline])

            #     index_begin += nline
            #     i_out += 1

            # out_feather = os.path.join(
            #     out_dir, "{:s}-{:08d}.feather".format(out_prefix, i_out)
            # )
            # print(out_feather)
            # df[index_begin:].reset_index().to_feather(out_feather)


if __name__ == "__main__":

    work_dir = "/work/murata/"
    work_subdirs = [
        "skypos_json",
        "ps1_json",
        "skyobj_220915/Gaia",
        "skyobj_220915/PS1",
    ]
    catalog_names = [
        "sky_hscssp_s21a_wide",
        "sky_ps1",
        "sky_ps1",
        "sky_gaia",
    ]

    # json_file = os.path.join(work_dir, "skypos_s21a_wide_9700_7,1.json")
    # out_prefix = "skypos_s21a_wide_9700_7,1"
    out_dir = "/work/monodera/Subaru-PFS/external_data/commissioning_2022sep/sky_murata/feather"
    version = "20220915"

    # nline = 1000000

    main(work_dir, work_subdirs, catalog_names, out_dir, version)

    # main(
    #     json_file,
    #     out_prefix,
    #     outdir=out_dir,
    #     nline=nline,
    #     # proposal_id=proposal_id,
    #     # catalog_name=catalog_name,
    #     version=version,
    # )
