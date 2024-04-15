#!/usr/bin/env python3

import argparse
import json

from ..utils import check_fluxstd_dups, prep_fluxstd_data


def main_checkdups():

    parser = argparse.ArgumentParser(
        description="Check for duplicates in the F-star candidate files"
    )
    parser.add_argument("dir", type=str, help="Directory path containing input files")
    parser.add_argument(
        "--format",
        type=str,
        default="parquet",
        help="File format to be used, feather or parquet (default: parquet)",
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
        help="Do not save the merged DataFrame as a feather or parquet file",
    )
    parser.add_argument(
        "--additional-columns",
        nargs="*",
        default=[],
        help="Additional columns to output for the merged file.  (e.g., 'psf_mag_g' 'psf_mag_r'). "
        "The following columns are saved by default: "
        '"obj_id", "ra", "dec", "input_catalog_id", "version", "input_file", "is_fstar_gaia", "prob_f_star"',
    )
    parser.add_argument(
        "--check-columns",
        nargs="*",
        default=["obj_id", "input_catalog_id", "version"],
        help="Columns used to check for duplicates. (default: obj_id, input_catalog_id, version)",
    )

    args = parser.parse_args()

    check_fluxstd_dups(
        indir=args.dir,
        outdir=args.outdir,
        format=args.format,
        skip_save_merged=args.skip_save_merged,
        additional_columns=args.additional_columns,
        check_columns=args.check_columns,
    )


def main_prep_data():
    parser = argparse.ArgumentParser(
        description="Prepare flux standard data for the target database by supplementing additional required fields."
    )
    parser.add_argument(
        "input_dir",
        type=str,
        help="Directory path containing input files. "
        "Files must be in one of the following formats: parquet, feather, or csv. "
        "The input files must be generated in a certain format to be compatible for targetdb.",
    )
    parser.add_argument(
        "output_dir", type=str, help="Directory path to save the output files."
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
    parser.add_argument(
        "--format",
        type=str,
        default="feather",
        help="File format to be used, feather or parquet (default: parquet)",
    )

    args = parser.parse_args()

    prep_fluxstd_data(
        args.input_dir,
        args.output_dir,
        args.version,
        args.input_catalog_id,
        rename_cols=args.rename_cols,
        format=args.format,
    )
