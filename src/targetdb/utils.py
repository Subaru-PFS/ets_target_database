#!/usr/bin/env python

import glob
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

import pandas as pd
from astropy.table import Table
from loguru import logger

from .models import Base
from .targetdb import TargetDB

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def load_config(config_file):
    with open(config_file, "rb") as fp:
        config = tomllib.load(fp)
    return config


def read_conf(config_file):
    # alias for load_config()
    return load_config(config_file)


def load_input_data(input_file, logger=logger):
    _, ext = os.path.splitext(input_file)
    if ext == ".csv":
        df = pd.read_csv(input_file)
    elif ext == ".feather":
        df = pd.read_feather(input_file)
    elif ext == ".ecsv":
        df = Table.read(input_file).to_pandas()
    else:
        logger.error(f"Unsupported file extension: {ext}")
        raise ValueError(f"Unsupported file extension: {ext}")
    return df


def generate_schema_markdown(schema_md=sys.stdout):

    out_md = ""

    for t in Base.metadata.sorted_tables:

        out_md += "\n## {:s}\n\n".format(t.name)

        df = pd.DataFrame(
            [], columns=["name", "type", "primary_key", "autoincrement", "comment"]
        )

        for c in t.columns:

            if c.autoincrement == True:
                autoincrement = True
            else:
                autoincrement = False

            df_tmp = pd.DataFrame(
                data={
                    "name": [c.name],
                    "type": [c.type],
                    "primary_key": [c.primary_key],
                    "autoincrement": [autoincrement],
                    "comment": [c.comment],
                },
            )
            df = pd.concat(
                [df, df_tmp],
                ignore_index=True,
            )

        out_md += df.to_markdown(index=False)

        out_md += "\n"

        # print(df.to_markdown(index=False))

    try:
        with open(schema_md, "w") as f:
            f.write(out_md)
    except TypeError:
        print(out_md)

    # return out_md


def draw_diagram(
    conf_file,
    sc_info_level="maximum",
    sc_log_level="SEVERE",
    sc_outdir=".",
    sc_outprefix="erdiagram_targetdb",
    sc_title="PFS Target Database",
    logger=logger,
):

    conf = read_conf(conf_file)

    time_string = datetime.now().strftime("%Y%m%d%H%M%S")

    outfile = os.path.join(sc_outdir, f"{sc_outprefix}-{time_string}.pdf")

    comm = [
        f"{os.path.join(conf['schemacrawler']['SCHEMACRAWLERDIR'],'_schemacrawler/bin/schemacrawler.sh')}",
        "--command=schema",
        "--server=postgresql",
        f"--host={conf['targetdb']['db']['host']}",
        f"--port={conf['targetdb']['db']['port']}",
        f"--database={conf['targetdb']['db']['dbname']}",
        "--schemas=public",
        f"--user={conf['targetdb']['db']['user']}",
        f"--password={conf['targetdb']['db']['password']}",
        f"--info-level={sc_info_level}",
        f"--log-level={sc_log_level}",
        "--portable-names",
        f"--title={sc_title}",
        "--output-format=pdf",
        f"--output-file={outfile}",
        "--no-remarks",
    ]

    logger.debug(f"{comm}")

    subprocess.run(comm, shell=False)


def join_backref_values(df, db=None, table=None, key=None, check_key=None):
    res = db.fetch_all(table)
    df_joined = df.merge(
        res,
        how="left",
        left_on=key,
        right_on=key,
    )
    if df_joined[check_key].isna().any():
        logger.error(f"There is at least one non-existing {check_key:s}.")
        raise ValueError(f"There is at least one non-existing {check_key:s}.")
    return df_joined


def add_backref_values(df, db=None, table=None):
    df_tmp = df.copy()
    backref_tables, backref_keys, backref_check_keys = [], [], []

    if table == "target":
        if "target_type_id" in df_tmp.columns:
            logger.info(
                "target_type_id is found in the DataFrame. Skip back reference detection."
            )
        elif "target_type_name" not in df_tmp.columns:
            logger.error("target_type_name is not found in the DataFrame.")
            raise KeyError("target_type_name is not found in the DataFrame.")
        else:
            if "upload_id" in df_tmp.columns:
                logger.info(
                    "upload_id is found in the DataFrame. Use it for back reference for input_catalog"
                )
                backref_tables = ["proposal", "input_catalog", "target_type"]
                backref_keys = ["proposal_id", "upload_id", "target_type_name"]
                backref_check_keys = ["proposal_id", "upload_id", "target_type_id"]
            else:
                logger.info(
                    "upload_id is not found in the DataFrame. Use input_catalog_name instead"
                )
                backref_tables = ["proposal", "input_catalog", "target_type"]
                backref_keys = ["proposal_id", "input_catalog_name", "target_type_name"]
                backref_check_keys = [
                    "proposal_id",
                    "input_catalog_id",
                    "target_type_id",
                ]

    elif table == "fluxstd":
        if "input_catalog_id" in df_tmp.columns:
            logger.info(
                "input_catalog_id is found in the DataFrame. Skip back reference detection."
            )
        elif "input_catalog_name" not in df_tmp.columns:
            logger.error("input_catalog_name is not found in the DataFrame.")
            raise KeyError("input_catalog_name is not found in the DataFrame.")
        else:
            backref_tables = ["input_catalog"]
            backref_keys = ["input_catalog_name"]
            backref_check_keys = ["input_catalog_id"]

    elif table == "sky":
        if "input_catalog_id" in df_tmp.columns:
            logger.info(
                "input_catalog_id is found in the DataFrame. Skip back reference detection."
            )
        elif "input_catalog_name" not in df_tmp.columns:
            logger.error("input_catalog_name is not found in the DataFrame.")
            raise KeyError("input_catalog_name is not found in the DataFrame.")
        else:
            backref_tables = ["input_catalog"]
            backref_keys = ["input_catalog_name"]
            backref_check_keys = ["input_catalog_id"]

    elif table == "proposal":
        if "proposal_category_id" in df_tmp.columns:
            logger.info(
                "proposal_category_id is found in the DataFrame. Skip back reference detection."
            )
        elif "proposal_category_name" not in df_tmp.columns:
            logger.error("proposal_category_name is not found in the DataFrame.")
            raise KeyError("proposal_category_name is not found in the DataFrame.")
        else:
            backref_tables = ["proposal_category"]
            backref_keys = ["proposal_category_name"]
            backref_check_keys = ["proposal_category_id"]

    # Join referenced values
    for i in range(len(backref_tables)):
        df_tmp = join_backref_values(
            df_tmp,
            db=db,
            table=backref_tables[i],
            key=backref_keys[i],
            check_key=backref_check_keys[i],
        )

    return df_tmp


def add_database_rows(
    input_file=None,
    config_file=None,
    table=None,
    commit=False,
    fetch=False,
    verbose=False,
    config=None,
    df=None,
    insert=False,
    update=False,
):
    if not insert and not update:
        logger.warning("Neither insert nor update is selected. Exiting...")
        return

    logger.info("Connecting to targetDB")
    db = TargetDB(**config["targetdb"]["db"])
    db.connect()

    if table in ["proposal", "fluxstd", "target", "sky"]:
        t_begin = time.time()
        df = add_backref_values(df, db=db, table=table)
        t_end = time.time()
        logger.info(f"Added back reference values in {t_end - t_begin:.2f} s")

    utcnow = datetime.now(timezone.utc)
    if insert:
        df["created_at"] = utcnow
    df["updated_at"] = utcnow

    if verbose:
        logger.debug(f"Working on the following DataFrame: \n{df}")

    try:
        t_begin = time.time()
        if commit:
            dry_run = False
            logger.info("Committing the changes to targetDB")
        else:
            dry_run = True
            logger.info("No changes will be committed to targetDB (i.e., dry run)")

        if insert:
            db.insert(table, df, dry_run=dry_run)
        elif update:
            db.update(table, df, dry_run=dry_run)
        t_end = time.time()
        logger.info(
            f"Insert data to the {table} table successful for {df.index.size} rows in {input_file} ({t_end - t_begin:.2f} s)"
            if insert
            else f"Update data in the {table} table successful for {df.index.size} rows in {input_file} ({t_end - t_begin:.2f} s)"
        )
    except Exception as e:
        logger.error(f"Operation failed: {e}: {input_file}")
        raise

    if fetch:
        logger.info("Fetching all table entries")
        res = db.fetch_all(table)
        logger.info(f"Fetched entries in the {table} table: \n{res}")

    logger.info("Closing targetDB")
    db.close()


def check_fluxstd_dups(
    indir=None, outdir=None, format="feather", skip_save_merged=False
):

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # Get a list of all feather files in the directory
    input_files = glob.glob(os.path.join(indir, f"*.{format}"))

    if len(input_files) == 0:
        logger.error(f"No files found in the directory: {indir}")
        return

    logger.info(f"Total number of files: {len(input_files)}")

    dataframes = []

    # Loop through the list of feather files
    for i, f in enumerate(input_files):
        logger.info(f"Reading file {i+1}/{len(input_files)}: {f}")
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
            os.path.join(f"{outdir}", "duplicates.csv"),
            index=False,
        )
    else:
        logger.info("No duplicates found.")

    # save duplicate-removed dataframe as a feather file
    if not skip_save_merged:
        df_cleaned = df.drop_duplicates(
            subset=["obj_id", "input_catalog_id", "version"],
            ignore_index=True,
        )
        df_cleaned.to_feather(
            os.path.join(
                f"{outdir}",
                "all_merged_nodups.feather",
            )
        )


def csv_to_feather(input_dir, output_dir, version, input_catalog_id, rename_cols=None):

    # Check if output directory exists, if not, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Iterate over all files in the input directory
    input_files = os.listdir(input_dir)
    for i, filename in enumerate(input_files):
        # Check if the file is a CSV file
        logger.info(f"Processing... {i+1}/{len(input_files)}: {filename}")
        if filename.endswith(".csv"):
            t1 = time.time()
            logger.info(f"\tConverting {filename} to the Feather format")

            # Read the CSV file
            df = pd.read_csv(os.path.join(input_dir, filename))

            # rename fstar_gaia to is_fstar_gaia
            if rename_cols is not None:
                logger.info(f"\tRenaming columns: {rename_cols}")
                df.rename(columns=rename_cols, inplace=True)

            # add input_catalog_id
            logger.info(f"\tAdding input_catalog_id: {input_catalog_id}")
            df["input_catalog_id"] = input_catalog_id

            # add version column to df as strings
            logger.info(f"\tAdding version string: {version}")
            df["version"] = version

            # Convert the filename from .csv to .feather
            # feather_filename = filename.rsplit(".", 1)[0] + ".feather"
            feather_filename = f"{os.path.splitext(filename)[0]}.feather"

            # Write the DataFrame to a Feather file
            df.to_feather(os.path.join(output_dir, feather_filename))
            t2 = time.time()
            logger.info(
                f"Done. Conversion took {t2-t1:.2f} seconds for {df.index.size} rows\n"
            )
