#!/usr/bin/env python3

import argparse
import json

from ..utils import check_fluxstd_dups, csv_to_pyarrow


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

    check_fluxstd_dups(
        indir=args.dir,
        outdir=args.outdir,
        format=args.format,
        skip_save_merged=args.skip_save_merged,
    )


def main_csv_to_feather():
    parser = argparse.ArgumentParser(description="Convert CSV files to Feather files")
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

    csv_to_pyarrow(
        args.input_dir,
        args.output_dir,
        args.version,
        args.input_catalog_id,
        rename_cols=args.rename_cols,
        format="feather",
    )


def main_csv_to_parquet():
    parser = argparse.ArgumentParser(description="Convert CSV files to Parquet files")
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

    csv_to_pyarrow(
        args.input_dir,
        args.output_dir,
        args.version,
        args.input_catalog_id,
        rename_cols=args.rename_cols,
        format="parquet",
    )
