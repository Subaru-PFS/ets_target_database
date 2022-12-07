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
    logger.error("ERROR callback args={}".format(json_file))


def my_cb(json_file):
    logger.info("SUCCESS callback args={}".format(json_file))


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
    logger.info(f"{json_keys=}")

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
            # "obj_id": np.arange(n_obj),
            # "obj_id_orig": data["objid"],
            "obj_id": data["objid"],
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
    logger.info(
        f"""
                {df}
                """
    )

    out_feather = os.path.join(out_dir, f"{out_prefix}.feather".format(out_prefix))
    logger.info(f"{out_feather=}")

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


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dry_run", action="store_true", help="Dry-run (do not save output file.)"
    )
    parser.add_argument(
        "--processes",
        type=int,
        default=32,
        help="Number of processes in multiprocessing.",
    )

    args = parser.parse_args()

    work_dir = "/work/murata/"
    work_subdirs = [
        "skyobj221031/ps1_json",
        "skyobj221031/nops1_json",
    ]

    catalog_names = [
        "sky_ps1",
        "sky_nops1",
    ]
    out_dir = "/work/monodera/Subaru-PFS/external_data/commissioning_2022nov/sky_murata/feather"
    version = "20221031"

    main(
        work_dir,
        work_subdirs,
        catalog_names,
        out_dir,
        version,
        dry_run=args.dry_run,
        processes=args.processes,
    )
