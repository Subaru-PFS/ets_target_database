#!/usr/bin/env python3

import argparse
import glob
import gzip
import json
import os
from multiprocessing import Pool

import numpy as np
import pandas as pd
from logzero import logger


def my_err_cb(json_file):
    print("ERROR callback args={}".format(json_file))


def my_cb(json_file):
    print("SUCCESS callback args={}".format(json_file))


def convert_sky_json2feather_targetdb(
    json_file, catalog_name, out_dir, version, dry_run=False
):

    file_basename = os.path.basename(json_file)

    if "json.gz" in json_file:
        out_prefix = file_basename.replace(".json.gz", "")
        with gzip.open(json_file, "r") as f:
            data = json.loads(f.read().decode("utf-8"))
    else:
        out_prefix = file_basename.replace(".json", "")
        with open(json_file, "r") as f:
            data = json.load(f)

    # keys in JSON
    # ['objid', 'ra', 'dec', 'magThresh', 'tract']
    json_keys = data.keys()
    print(json_keys)

    n_obj = len(data["objid"])

    if ("imgfile" in json_keys) and (data["imgfile"] is not None):
        logger.info("imgfile is found. trying to extract tract/patch information.")
        tract = np.full(n_obj, int(data["imgfile"][-13:-9]), dtype=int)
        patch = np.full(n_obj, int(data["imgfile"][-8:-5].replace(",", "0")), dtype=int)
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
            "mag_thresh": mag_thresh,
            "version": [version] * n_obj,
        }
    )
    print(df)

    out_feather = os.path.join(out_dir, f"{out_prefix}.feather".format(out_prefix))
    print(out_feather)

    if not dry_run:
        df.to_feather(out_feather)


def main(
    work_dir,
    work_subdirs,
    catalog_names,
    out_dir,
    version,
    dry_run=False,
    processes=1,
):

    for subdir, catalog_name in zip(work_subdirs, catalog_names):
        dir_path = os.path.join(work_dir, subdir)

        json_files = glob.glob(os.path.join(dir_path, "*.json*"))

        for i in range(len(json_files)):

            with Pool(processes=processes) as pool:
                pool.apply_async(
                    convert_sky_json2feather_targetdb,
                    args=(json_files[i], catalog_name, out_dir, version),
                    kwds=dict(dry_run=dry_run),
                    callback=my_cb,
                    error_callback=my_err_cb,
                )
                pool.close()
                pool.join()

            # for i in range(len(json_files)):
            # for i in range(1):

            # convert_sky_json2feather_targetdb(
            #     json_files[i], catalog_name, out_dir, version, dry_run=dry_run
            # )

            # file_basename = os.path.basename(json_files[i])

            # if "json.gz" in json_files[i]:
            #     out_prefix = file_basename.replace(".json.gz", "")
            #     with gzip.open(json_files[i], "r") as f:
            #         data = json.loads(f.read().decode("utf-8"))
            # else:
            #     out_prefix = file_basename.replace(".json", "")
            #     with open(json_files[i], "r") as f:
            #         data = json.load(f)

            # # keys in JSON
            # # ['objid', 'ra', 'dec', 'magThresh', 'tract']
            # json_keys = data.keys()
            # print(json_keys)

            # n_obj = len(data["objid"])

            # if ("imgfile" in json_keys) and (data["imgfile"] is not None):
            #     logger.info(
            #         "imgfile is found. trying to extract tract/patch information."
            #     )
            #     tract = np.full(n_obj, int(data["imgfile"][-13:-9]), dtype=int)
            #     patch = np.full(
            #         n_obj, int(data["imgfile"][-8:-5].replace(",", "0")), dtype=int
            #     )
            # elif "tract" in json_keys:
            #     logger.info(
            #         "Tract is found in the keys, while patch is not found. Use None for patch."
            #     )
            #     tract = np.full(n_obj, data["tract"])
            #     patch = [None] * n_obj
            # else:
            #     logger.warning(
            #         "Both tract and patch information are not found. Use None for them."
            #     )
            #     tract = [None] * n_obj
            #     patch = [None] * n_obj

            # if type(data["magThresh"]) is list:
            #     mag_thresh = data["magThresh"]
            # else:
            #     mag_thresh = [data["magThresh"]] * n_obj

            # df = pd.DataFrame(
            #     {
            #         "obj_id": np.arange(n_obj),
            #         "obj_id_orig": data["objid"],
            #         "ra": data["ra"],
            #         "dec": data["dec"],
            #         "epoch": ["J2000.0"] * n_obj,
            #         "tract": tract,
            #         "patch": patch,
            #         "target_type_name": ["SKY"] * n_obj,
            #         "input_catalog_name": [catalog_name] * n_obj,
            #         "mag_thresh": mag_thresh,
            #         "version": [version] * n_obj,
            #     }
            # )
            # print(df)

            # out_feather = os.path.join(
            #     out_dir, f"{out_prefix}.feather".format(out_prefix)
            # )
            # print(out_feather)

            # if not dry_run:
            #     df.to_feather(out_feather)

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

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dry_run", action="store_true", help="Dry-run (do not save output file.)"
    )
    parser.add_argument(
        "--processes",
        type=int,
        default=16,
        help="Number of processes in multiprocessing.",
    )

    args = parser.parse_args()

    work_dir = "/work/murata/"
    work_subdirs = [
        "skypos_json",
        "ps1_json",
        "skyobj_220915/PS1",
        "skyobj_220915/Gaia",
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

    main(
        work_dir,
        work_subdirs,
        catalog_names,
        out_dir,
        version,
        dry_run=args.dry_run,
        processes=args.processes,
    )

    # main(
    #     json_file,
    #     out_prefix,
    #     outdir=out_dir,
    #     nline=nline,
    #     # proposal_id=proposal_id,
    #     # catalog_name=catalog_name,
    #     version=version,
    # )
