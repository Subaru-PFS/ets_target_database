#!/usr/bin/env python3

import argparse
import glob
import json
import os
import time

import pandas as pd
from loguru import logger

from .cli_utils import load_input_data


def main_checkdups():

    parser = argparse.ArgumentParser(
        description="Check for duplicates in the F-star candidate files"
    )
    parser.add_argument("dir", type=str, help="Directory path containing input files")
    parser.add_argument(
        "--format",
        type=str,
        default="feather",
        help="File format to be used (default: feather)",
    )
    parser.add_argument(
        "-o",
        "--outdir",
        type=str,
        default=".",
        help="Path to output directory. (default: .)",
    )
    parser.add_argument(
        "--skip-save-merged",
        action="store_true",
        help="Do not save the merged DataFrame as a feather file",
    )

    args = parser.parse_args()

    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    # Get a list of all feather files in the directory
    input_files = glob.glob(os.path.join(args.dir, f"*.{args.format}"))

    if len(input_files) == 0:
        logger.error(f"No files found in the directory: {args.dir}")
        return

    logger.info(f"Total number of files: {len(dataframes)}")

    dataframes = []

    # Loop through the list of feather files
    for f in input_files:
        logger.info(f"Reading file: {f}")
        # Read the feather file into a DataFrame
        file_df = load_input_data(f, logger=logger)
        file_df["input_file"] = f.rsplit("/")[-1].replace(".feather", "")

        # only selected columns are included because of the memory limit
        dataframes.append(
            file_df.loc[
                :,
                [
                    "obj_id",
                    "ra",
                    "dec",
                    "input_catalog_id",
                    "version",
                    "input_file",
                    "is_fstar_gaia",
                    "prob_f_star",
                ],
            ]
        )

    logger.info("Finished reading all input files.")

    # Concatenate all DataFrames into a single DataFrame
    df = pd.concat(dataframes, ignore_index=True)

    # Check for duplicates
    duplicates = df.duplicated(
        subset=["obj_id", "input_catalog_id", "version"],
        keep=False,
    )

    # Print the result
    logger.info(f"Duplicates exist: {duplicates.any()}")

    if duplicates.any():
        logger.info(f"Number of duplicates: {duplicates.sum()}")
        logger.info(f"Duplicate rows: \n{df[duplicates]}")
        df[duplicates].sort_values(by=["obj_id"]).to_csv(
            os.path.join(f"{args.outdir}", "duplicates.csv"),
            index=False,
        )
    else:
        logger.info("No duplicates found.")

    # save duplicate-removed dataframe as a feather file
    if not args.skip_save_merged:
        df_cleaned = df.drop_duplicates(
            subset=["obj_id", "input_catalog_id", "version"],
            ignore_index=True,
        )
        df_cleaned.to_feather(
            os.path.join(
                f"{args.outdir}",
                "all_merged_nodups.feather",
            )
        )


def main_csv_to_feather():
    parser = argparse.ArgumentParser(
        description="Check for duplicates in the F-star candidate files"
    )
    parser.add_argument(
        "input_dir", type=str, help="Directory path containing input CSV files"
    )
    parser.add_argument(
        "output_dir", type=str, help="Directory path to save the Feather files"
    )
    parser.add_argument(
        "--version",
        type=str,
        required=True,
        help="Version **string** for the F-star candidate catalog (e.g., '3.3')",
    )
    parser.add_argument(
        "--input_catalog_id",
        type=int,
        required=True,
        help="Input catalog ID for the F-star candidate catalog",
    )
    parser.add_argument(
        "--rename-cols",
        default=None,
        type=json.loads,
        help='Dictionary to rename columns (e.g., \'{"fstar_gaia": "is_fstar_gaia"}\'; default is None)',
    )

    args = parser.parse_args()

    # Check if output directory exists, if not, create it
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # Iterate over all files in the input directory
    input_files = os.listdir(args.input_dir)
    for i, filename in enumerate(input_files):
        # Check if the file is a CSV file
        logger.info(f"Processing... {i+1}/{len(input_files)}: {filename}")
        if filename.endswith(".csv"):
            t1 = time.time()
            logger.info(f"Converting {filename} to the Feather format")

            # Read the CSV file
            df = pd.read_csv(os.path.join(args.input_dir, filename))

            # rename fstar_gaia to is_fstar_gaia
            df.rename(columns=args.rename_cols, inplace=True)

            # add input_catalog_id
            df["input_catalog_id"] = args.input_catalog_id

            # add version column to df as strings
            df["version"] = args.version

            # Convert the filename from .csv to .feather
            # feather_filename = filename.rsplit(".", 1)[0] + ".feather"
            feather_filename = f"{os.path.splitext(filename)[0]}.feather"

            # Write the DataFrame to a Feather file
            df.to_feather(os.path.join(args.output_dir, feather_filename))
            t2 = time.time()
            logger.info(f"Conversion took {t2-t1:.2f} seconds for {df.index.size} rows")
