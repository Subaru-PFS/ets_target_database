#!/usr/bin/env python

import glob
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from astropy.table import Table
from loguru import logger
from sqlalchemy import URL

from . import TargetDB
from .models import (
    Base,
    input_catalog_id_absolute_max,
    input_catalog_id_max,
    input_catalog_id_start,
)

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def load_config(config_file):
    """
    Load configuration from a TOML file.

    Parameters
    ----------
    config_file : str
        The path to the configuration file.

    Returns
    -------
    config : dict
        The configuration dictionary.

    Raises
    ------
    FileNotFoundError
        If the configuration file does not exist.

    Notes
    -----
    This function uses the tomllib or tomli library to parse the TOML file.
    """
    with open(config_file, "rb") as fp:
        config = tomllib.load(fp)
    return config


def read_conf(config_file):
    """
    Alias for the load_config function.

    Parameters
    ----------
    config_file : str
        The path to the configuration file.

    Returns
    -------
    config : dict
        The configuration dictionary.

    Raises
    ------
    FileNotFoundError
        If the configuration file does not exist.

    Notes
    -----
    This function is an alias for the load_config function.
    It uses the load_config function to load the configuration from the TOML file.
    """

    return load_config(config_file)


def load_input_data(input_file, metadata=False, logger=logger):
    """
    Load input data from a file into a pandas DataFrame.

    Parameters
    ----------
    input_file : str
        The path to the input file (CSV, Feather, Parquet, or ECSV).
    logger : loguru.logger, optional
        The logger to use for logging messages. Defaults to the root logger.

    Returns
    -------
    df : pandas.DataFrame
        The loaded data.

    Raises
    ------
    ValueError
        If the file extension is not supported.
    FileNotFoundError
        If the input file does not exist.

    Notes
    -----
    This function uses pandas or astropy to load the data depending on the file format.
    It supports CSV, Feather, Parquet, and ECSV file formats.
    """

    _, ext = os.path.splitext(input_file)
    if ext == ".csv":
        # set keep_default_na=False to keep empty strings as empty strings
        df = pd.read_csv(input_file, keep_default_na=False)
        meta = None
    elif ext == ".feather":
        df = pd.read_feather(input_file)
        meta = None
    elif ext == ".parquet":
        df = pd.read_parquet(input_file)
        meta = None
    elif ext == ".ecsv":
        tb = Table.read(input_file)
        df = tb.to_pandas()
        meta = tb.meta
    else:
        logger.error(f"Unsupported file extension: {ext}")
        raise ValueError(f"Unsupported file extension: {ext}")

    if metadata:
        return df, meta

    return df


def read_excel(input_file, sheetnames=None):
    """
    Load data from an Excel file and return it as a dictionary of pandas DataFrames.

    Parameters
    ----------
    input_file : str
        Path to the input Excel file.

    Returns
    -------
    dict
        Dictionary containing two pandas DataFrames, 'proposal' and 'allocation',
        corresponding to the "Proposals" and "Allocation" sheets in the input Excel file.

    """

    if sheetnames is None:
        sheetnames = ["Proposals", "Allocation"]

    dataframes = {}

    for sheetname in sheetnames:
        try:
            df = pd.read_excel(input_file, sheet_name=sheetname)
            dataframes[sheetname.lower()] = df
        except Exception as e:
            logger.error(f"Error reading sheet {sheetname}: {e}")
            raise e
    return dataframes
    # df_proposal = pd.read_excel(input_file, sheet_name="Proposals")
    # df_allocation = pd.read_excel(input_file, sheet_name="Allocation")
    # return {"proposal": df_proposal, "allocation": df_allocation}


def get_url_object(config):
    """
    Create a URL object from the given configuration.

    Parameters
    ----------
    config : dict
        The configuration dictionary containing the database connection details.
        Expected keys are 'targetdb'->'db'->'dialect', 'user', 'password', 'host', 'port', 'dbname'.

    Returns
    -------
    url_object : sqlalchemy.engine.url.URL
        The created URL object representing the database connection.

    Raises
    ------
    KeyError
        If a necessary key is missing from the config dictionary.

    Examples
    --------
    >>> config = {'targetdb': {'db': {'dialect':'postgresql', 'user':'username', 'password':'password', 'host':'localhost', 'port':5432, 'dbname':'test_db'}}}
    >>> url_object = get_url_object(config)
    >>> print(url_object)
    postgresql://username:password@localhost:5432/test_db
    """
    url_object = URL.create(
        drivername=config["targetdb"]["db"]["dialect"],
        username=config["targetdb"]["db"]["user"],
        password=config["targetdb"]["db"]["password"],
        host=config["targetdb"]["db"]["host"],
        port=config["targetdb"]["db"]["port"],
        database=config["targetdb"]["db"]["dbname"],
    )

    return url_object


def install_q3c_extension(config, dry_run=False):

    # connect to the targetDB
    db = TargetDB(**config["targetdb"]["db"])
    db.connect()

    logger.info("Installing q3c extension.")
    try:
        db.execute_query("CREATE EXTENSION IF NOT EXISTS q3c", dry_run=dry_run)
    except Exception as e:
        logger.error(f"Error installing q3c extension: {e}")
        raise e

    # close the connection
    db.close()


def generate_schema_markdown(output_file=None):

    out_md = ""

    for t in Base.metadata.sorted_tables:

        out_md += "\n## {:s}\n\n".format(t.name)

        df = pd.DataFrame(
            [], columns=["name", "type", "primary_key", "autoincrement", "comment"]
        )

        for c in t.columns:

            if c.autoincrement is True:
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

    # try:
    #     with open(output_file, "w") as f:
    #         f.write(out_md)
    # except TypeError:
    #     print(out_md)

    import rich

    if output_file is not None:
        try:
            with open(output_file, "w") as f:
                f.write(out_md)
        except TypeError:
            rich.print(out_md)
    else:
        rich.print(out_md)

    # return out_md


def draw_diagram(
    config,
    generator="schemacrawler",
    output_dir="diagram",
    title="PFS Target Database",
    sc_info_level="maximum",
    sc_log_level="SEVERE",
    sc_outprefix="erdiagram_targetdb",
    tbls_format="mermaid",
    logger=logger,
):

    # conf = read_conf(conf_file)

    time_string = datetime.now().strftime("%Y%m%d%H%M%S")

    if generator == "schemacrawler":
        outfile = os.path.join(output_dir, f"{sc_outprefix}-{time_string}.pdf")

        comm = [
            f"{os.path.join(config['schemacrawler']['SCHEMACRAWLERDIR'],'bin/schemacrawler.sh')}",
            # f"{os.path.join(config['schemacrawler']['SCHEMACRAWLERDIR'],'_schemacrawler/bin/schemacrawler.sh')}",
            "--command=schema",
            "--server=postgresql",
            f"--host={config['targetdb']['db']['host']}",
            f"--port={config['targetdb']['db']['port']}",
            f"--database={config['targetdb']['db']['dbname']}",
            "--schemas=public",
            f"--user={config['targetdb']['db']['user']}",
            f"--password={config['targetdb']['db']['password']}",
            f"--info-level={sc_info_level}",
            f"--log-level={sc_log_level}",
            "--portable-names",
            f"--title={title}",
            "--output-format=pdf",
            f"--output-file={outfile}",
            "--no-remarks",
        ]
        logger.debug(f"{comm}")
        subprocess.run(comm, shell=False)
    elif generator == "tbls":
        url_object = get_url_object(config)
        url_object_tbls = (
            url_object.render_as_string(hide_password=False).replace(
                "postgresql", "postgres", 1
            )
            + "?sslmode=disable"
        )

        import tempfile

        with tempfile.NamedTemporaryFile("w") as tmpf:
            tmpf.write(
                f"""
dsn: {url_object_tbls}
docPath: {output_dir}
name: {title}

er:
  format: {tbls_format}

disableOutputSchema: true"""
            )
            tmpf.seek(0)

            comm = [
                "tbls",
                "doc",
                "-c",
                f"{tmpf.name}",
                "--force",  # force create
            ]
            logger.debug(f"{comm}")
            subprocess.run(comm, shell=False)
    else:
        logger.error(f"Unsupported generator: {generator}")
        raise ValueError(f"Unsupported generator: {generator}")


def join_backref_values(df, db=None, table=None, key=None, check_key=None):
    """
    Joins a DataFrame with a table from a database on a specified key and checks for non-existing keys.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to join with the table.
    db : Database, optional
        The database object where the table is located. Defaults to None.
    table : str, optional
        The name of the table to join with the DataFrame. Defaults to None.
    key : str, optional
        The key on which to join the DataFrame and the table. Defaults to None.
    check_key : str, optional
        The key to check for non-existing values after the join. Defaults to None.

    Returns
    -------
    df_joined : pandas.DataFrame
        The DataFrame after joining with the table.

    Raises
    ------
    ValueError
        If there is at least one non-existing value in the check_key column after the join.
    """

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


def add_backref_values(df, db=None, table=None, upload_id=None):
    """
    Add back reference values to a DataFrame based on the specified table.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to which back reference values are to be added.
    db : Database, optional
        The database object that contains the table. Defaults to None.
    table : str, optional
        The name of the table to use for back reference values. Defaults to None.
    upload_id : str, optional
        The upload (16-character string) id to be used. Defaults to None.

    Returns
    -------
    df_tmp : pandas.DataFrame
        The DataFrame after adding back reference values.

    Raises
    ------
    KeyError
        If the necessary keys for back reference are not found in the DataFrame.

    Notes
    -----
    This function makes a copy of the input DataFrame and modifies the copy.
    The function checks for the presence of certain keys in the DataFrame based on the table name.
    If the necessary keys are not found, it raises a KeyError.
    """

    df_tmp = df.copy()
    backref_tables, backref_keys, backref_check_keys = [], [], []

    if table == "target":
        backref_tables = ["proposal"]
        backref_keys = ["proposal_id"]
        backref_check_keys = ["proposal_id"]

        if "target_type_id" in df_tmp.columns:
            logger.info(
                "target_type_id is found in the DataFrame. Skip back reference detection."
            )
        else:
            if "target_type_name" in df_tmp.columns:
                backref_tables.append("target_type")
                backref_keys.append("target_type_name")
                backref_check_keys.append("target_type_id")
            else:  # "target_type_name" not in df_tmp.columns:
                logger.error("target_type_name is not found in the DataFrame.")
                raise KeyError("target_type_name is not found in the DataFrame.")

        if "upload_id" in df_tmp.columns:
            logger.info(
                "upload_id is found in the DataFrame. Use it for back reference for input_catalog"
            )
            backref_tables.append("input_catalog")
            backref_keys.append("upload_id")
            backref_check_keys.append("input_catalog_id")
        else:
            if "input_catalog_name" in df_tmp.columns:
                logger.info(
                    "upload_id is not found in the DataFrame. Use input_catalog_name instead"
                )
                backref_tables.append("input_catalog")
                backref_keys.append("input_catalog_name")
                backref_check_keys.append("input_catalog_id")
            else:
                logger.error(
                    "upload_id and input_catalog_name are not found in the DataFrame."
                )
                raise KeyError(
                    "upload_id and input_catalog_name are not found in the DataFrame."
                )

    elif table in ["fluxstd", "sky", "user_pointing"]:
        if "input_catalog_id" in df_tmp.columns:
            logger.info(
                "input_catalog_id is found in the DataFrame. Skip back reference detection."
            )
        else:
            if "input_catalog_name" in df_tmp.columns:
                logger.info("input_catalog_name is found in the DataFrame.")
                ref_key = "input_catalog_name"
            elif "upload_id" in df_tmp.columns:
                logger.info(
                    "upload_id is found in the DataFrame. Use it for back reference for input_catalog"
                )
                ref_key = "upload_id"
            elif upload_id is not None:
                logger.info(
                    f"upload_id is not found in the DataFrame. Use the provided upload_id {upload_id} instead."
                )
                df_tmp["upload_id"] = upload_id
                ref_key = "upload_id"
            else:
                logger.error(
                    "Neither upload_id nor input_catalog_name is found in the DataFrame."
                )
                raise KeyError(
                    "upload_id or input_catalog_name must exist in the input DataFrame."
                )

            backref_tables = ["input_catalog"]
            backref_keys = [ref_key]
            backref_check_keys = ["input_catalog_id"]

    elif table == "proposal":
        if "proposal_category_id" in df_tmp.columns:
            logger.info(
                "proposal_category_id is found in the DataFrame. Skip back reference detection."
            )
        else:
            if "proposal_category_name" in df_tmp.columns:
                backref_tables = ["proposal_category"]
                backref_keys = ["proposal_category_name"]
                backref_check_keys = ["proposal_category_id"]
            else:
                logger.error("proposal_category_name is not found in the DataFrame.")
                raise KeyError("proposal_category_name is not found in the DataFrame.")

        if "partner_id" in df_tmp.columns:
            logger.info(
                "partner_id is found in the DataFrame. Skip back reference detection."
            )
        else:
            if "partner_name" in df_tmp.columns:
                backref_tables.append("partner")
                backref_keys.append("partner_name")
                backref_check_keys.append("partner_id")
            else:
                logger.error("partner_name is not found in the DataFrame.")
                raise KeyError("partner_name is not found in the DataFrame.")

    # Join referenced values
    for i in range(len(backref_tables)):
        df_tmp = join_backref_values(
            df_tmp,
            db=db,
            table=backref_tables[i],
            key=backref_keys[i],
            check_key=backref_check_keys[i],
        )

    # raise an error if the number of rows is different before and after the foreign key lookup
    if df.index.size != df_tmp.index.size:
        logger.error(
            "The number of rows in the DataFrame is different before and after the foreign key lookup."
        )
        raise ValueError(
            "The number of rows in the DataFrame is different before and after the foreign key lookup."
        )

    if "created_at" in df_tmp.columns:
        df_tmp.drop(columns=["created_at"], inplace=True)
    if "updated_at" in df_tmp.columns:
        df_tmp.drop(columns=["updated_at"], inplace=True)

    return df_tmp


def make_target_df_from_uploader(
    df,
    db=None,
    table="target",
    proposal_id=None,
    upload_id=None,
    target_type_name="SCIENCE",
    insert=False,
    update=False,
):
    """
    Create a target DataFrame from an uploader.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to be processed.
    db : Database, optional
        The database object that contains the table. Defaults to None.
    table : str, optional
        The name of the table to use for back reference values. Defaults to "target".
    proposal_id : str, optional
        The proposal id to be used. Defaults to None.
    upload_id : str, optional
        The upload id to be used. Defaults to None.
    target_type_name : str, optional
        The type of the target. Defaults to "SCIENCE".
    insert : bool, optional
        If True, insert the DataFrame into the database. Defaults to False.
    update : bool, optional
        If True, update the DataFrame in the database. Defaults to False.

    Returns
    -------
    df : pandas.DataFrame
        The processed DataFrame.

    Raises
    ------
    ValueError
        If proposal_id or upload_id is not provided.

    Notes
    -----
    This function renames the 'exptime' column to 'effective_exptime' and
    'reference_arm' to 'qa_reference_arm' if they exist in the DataFrame.
    """

    logger.info(f"The default target_type_name {target_type_name} is used.")

    if proposal_id is None:
        logger.error("proposal_id is not provided.")
        raise ValueError("proposal_id is not provided.")
    else:
        logger.info(f"proposal_id is provided: {proposal_id}")

    if upload_id is None:
        logger.error("upload_id is not provided.")
        raise ValueError("upload_id is not provided.")
    else:
        logger.info(f"upload_id is provided: {upload_id}")

    if "exptime" in df.columns:
        df.rename(columns={"exptime": "effective_exptime"}, inplace=True)

    if "reference_arm" in df.columns:
        df.rename(columns={"reference_arm": "qa_reference_arm"}, inplace=True)

    # fill missing values with None or NaN for filters and fluxes
    for band in ["g", "r", "i", "z", "y", "j"]:
        if f"filter_{band}" in df.columns:
            # if the table is a masked table, fill the masked values with None for filters
            # if the table is not a masked table, just pass
            try:
                df.loc[df[f"filter_{band}"].isna(), f"filter_{band}"] = None
            except AttributeError:
                pass
        if f"flux_{band}" in df.columns:
            df.rename(columns={f"flux_{band}": f"psf_flux_{band}"}, inplace=True)
        if f"flux_error_{band}" in df.columns:
            df.rename(
                columns={f"flux_error_{band}": f"psf_flux_error_{band}"}, inplace=True
            )

    df["target_type_name"] = target_type_name
    df["proposal_id"] = proposal_id
    df["upload_id"] = upload_id

    n_target = df.index.size
    logger.info(f"{n_target=}")

    # FIXME: loop is slow for a large target list. Want to look for a fast and better way.
    if update:
        logger.info("Look up the target table by (ob_code, proposal_id)")
        df_target = pd.DataFrame()
        for i in range(df.index.size):
            df_target_tmp = db.fetch_by_id(
                table,
                ob_code=df["ob_code"][i],
                proposal_id=df["proposal_id"][i],
            )
            if not df_target_tmp.empty:
                df_target = pd.concat(
                    [df_target, df_target_tmp],
                    ignore_index=True,
                )
        logger.info(f"Merged DataFrame\n{df_target}")
        df = df.merge(
            df_target.loc[:, ["target_id", "ob_code", "proposal_id"]],
            on=["ob_code", "proposal_id"],
            how="left",
        )
        n_target_lookup = df_target.index.size
        if n_target_lookup != n_target:
            logger.error(
                "The number of targets are different before and after the table lookup. "
                f"Please check if any new targets are provided. {n_target=}, {n_target_lookup=}"
            )
            raise ValueError(
                f"The number of targets are different before and after the table lookup. {n_target=}, {n_target_lookup=}"
            )

    n_target = df.index.size
    df_backref = add_backref_values(df, db=db, table=table)

    # add the is_medium_resolution column by looking at the resolution column
    df_backref["is_medium_resolution"] = df["resolution"] == "M"

    return df_backref


def check_input_catalog(
    df,
    db=None,
    input_catalog_id_start=input_catalog_id_start,
    input_catalog_id_max=input_catalog_id_max,
):
    df_in_db = db.fetch_all("input_catalog")

    is_input_catalog_id = "input_catalog_id" in df.columns
    if is_input_catalog_id:
        logger.info("input_catalog_id is found in the DataFrame. Check values.")
    else:
        logger.info("input_catalog_id is not found in the DataFrame. Proceed.")

    for i in range(df.index.size):
        # TODO: upgrade PostgreSQL to 12 or later
        # NOTE: Since partial indexing is not supported on targetdb
        # by thePostgreSQL version 10.6, we need to check if the upload_id
        # is already in the input_catalog table manually.
        if (df["upload_id"][i] != "") and (
            df["upload_id"][i] in df_in_db["upload_id"].values
        ):
            logger.error(
                f"upload_id {df['upload_id'][i]} is already in the input_catalog table."
            )
            raise ValueError(
                f"upload_id {df['upload_id'][i]} is already in the input_catalog table."
            )
        if is_input_catalog_id:
            if (df["input_catalog_id"][i] >= input_catalog_id_start) and (
                df["input_catalog_id"][i] <= input_catalog_id_max
            ):
                logger.error(
                    f"input_catalog_id for manual insert must be outside of {input_catalog_id_start} to {input_catalog_id_max}."
                )
                raise ValueError(
                    f"input_catalog_id for manual insert must be outside of {input_catalog_id_start} to {input_catalog_id_max}."
                )
            elif df["input_catalog_id"][i] > input_catalog_id_absolute_max:
                logger.error(
                    "input_catalog_id must be less than 100000 due to datamodel constraint."
                )
                raise ValueError("input_catalog_id is too large")


def add_database_rows(
    input_file=None,
    config_file=None,
    table=None,
    commit=False,
    fetch=False,
    verbose=False,
    config=None,
    df=None,
    from_uploader=False,
    proposal_id=None,
    upload_id=None,
    insert=False,
    update=False,
):
    """
    Add rows to a database from an input file or DataFrame.

    Parameters
    ----------
    input_file : str, optional
        The path to the input file. Defaults to None.
    config_file : str, optional
        The path to the configuration file. Defaults to None.
    table : str, optional
        The name of the table in the database to add rows to. Defaults to None.
    commit : bool, optional
        If True, commit the changes to the database. Defaults to False.
    fetch : bool, optional
        If True, fetch the results after adding rows. Defaults to False.
    verbose : bool, optional
        If True, print verbose output. Defaults to False.
    config : dict, optional
        The configuration dictionary. Defaults to None.
    df : pandas.DataFrame, optional
        The DataFrame to add rows from. Defaults to None.
    from_uploader : bool, optional
        If True, the DataFrame is from an uploader. Defaults to False.
    proposal_id : int, optional
        The proposal id to be used. Defaults to None.
    upload_id : int, optional
        The upload id to be used. Defaults to None.
    insert : bool, optional
        If True, insert the DataFrame into the database. Defaults to False.
    update : bool, optional
        If True, update the DataFrame in the database. Defaults to False.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If neither insert nor update is selected.

    Notes
    -----
    This function connects to the targetDB and adds rows to the specified table.
    If the table is 'proposal', 'fluxstd', or 'sky', it adds back reference values to the DataFrame.
    If the table is 'target' and the DataFrame is from an uploader, it makes a target DataFrame from the uploader.
    """

    if not insert and not update:
        logger.warning("Neither insert nor update is selected. Exiting...")
        return

    logger.info("Connecting to targetDB")
    db = TargetDB(**config["targetdb"]["db"])
    db.connect()

    t_begin = time.time()
    if table in ["proposal", "fluxstd", "sky", "user_pointing"]:
        df = add_backref_values(df, db=db, table=table, upload_id=upload_id)
    elif table in ["target"]:
        if from_uploader:
            df = make_target_df_from_uploader(
                df,
                db=db,
                table=table,
                proposal_id=proposal_id,
                upload_id=upload_id,
                insert=insert,
                update=update,
            )
        else:
            df = add_backref_values(df, db=db, table=table)
    elif table in ["input_catalog"]:
        check_input_catalog(
            df,
            db=db,
            input_catalog_id_start=input_catalog_id_start,
            input_catalog_id_max=input_catalog_id_max,
        )
    t_end = time.time()
    logger.info(f"Added back reference values in {t_end - t_begin:.2f} s")

    if verbose:
        logger.debug(f"{df.columns=}")

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
        logger.info("Fetching the first 100 table entries")
        res = db.fetch_all(table)
        logger.info(f"Fetched the first 100 entries in the {table} table: \n{res}")

    logger.info("Closing targetDB")
    db.close()


def check_duplicates(
    indir=None,
    outdir=None,
    file_format="parquet",
    skip_save_merged=False,
    additional_columns=None,
    check_columns=None,
):
    """
    Checks for duplicates in files in a given directory.

    Parameters
    ----------
    indir : str
        The directory containing the input files. Defaults to None.
    outdir : str
        The directory where the output files will be saved. Defaults to None.
    file_format : str, optional
        The format of the input files. The Feather or Parquet formats are supported.
        Defaults to "parquet".
    skip_save_merged : bool, optional
        If True, the merged dataframe will not be saved. Defaults to False.

    Returns
    -------
    None
    """

    if additional_columns is None:
        additional_columns = []

    if check_columns is None:
        check_columns = ["obj_id", "input_catalog_id", "version"]

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # Get a list of all feather files in the directory
    input_files = glob.glob(os.path.join(indir, f"*.{file_format}"))

    if len(input_files) == 0:
        logger.error(f"No files found in the directory: {indir}")
        return

    logger.info(f"Total number of files: {len(input_files)}")

    dataframes = []

    # Loop through the list of input files
    for i, f in enumerate(input_files):
        logger.info(f"Reading file {i+1}/{len(input_files)}: {f}")
        # Read the input file into a DataFrame
        file_df = load_input_data(f, logger=logger)
        file_df["input_file"] = f.rsplit("/")[-1].replace(f".{file_format}", "")

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
                ]
                + additional_columns,
            ]
        )

    logger.info("Finished reading all input files.")

    # Concatenate all DataFrames into a single DataFrame
    df = pd.concat(dataframes, ignore_index=True)

    # Check for duplicates
    logger.info(f"Checking for duplicates using the following columns: {check_columns}")
    duplicates = df.duplicated(
        subset=check_columns,
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

    # save duplicate-removed dataframe as a feather or parquet file
    if not skip_save_merged:
        df_cleaned = df.drop_duplicates(
            subset=["obj_id", "input_catalog_id", "version"],
            ignore_index=True,
        )
        output_file = os.path.join(
            f"{outdir}",
            f"all_merged_nodups.{file_format}",
        )
        if file_format == "feather":
            df_cleaned.to_feather(output_file)
        elif file_format == "parquet":
            df_cleaned.to_parquet(output_file)
        else:
            logger.error(f"Unsupported file format: {file_format}")


def prep_fluxstd_data(
    input_dir,
    output_dir,
    version,
    input_catalog_id,
    input_catalog_name,
    rename_cols=None,
    file_format="parquet",
):
    """
    Prepare flux standard data ready to be inserted to the target database.

    Parameters
    ----------
    input_dir : str
        The directory containing the input files.
    output_dir : str
        The directory where the output files will be saved.
    version : str
        The version string to be added to the dataframe.
    input_catalog_id : int
        The input catalog ID to be added to the dataframe.
    input_catalog_name : str
        The input catalog ID name to be added to the dataframe.
    rename_cols : dict, optional
        A dictionary mapping old column names to new ones. Defaults to None.
    file_format : str, optional
        The format of the output files, "feather" or "parquet". Defaults to "parquet".

    Returns
    -------
    None

    Notes
    -----
    Either of input_catalog_id or input_catalog_name must be provided.
    If both are provided, input_catalog_name will be used.
    """

    if (input_catalog_name is None) and (input_catalog_id is None):
        logger.error(
            "Either of input_catalog_id or input_catalog_name must be provided."
        )
        raise ValueError(
            "Either of input_catalog_id or input_catalog_name must be provided."
        )

    # Check if output directory exists, if not, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Iterate over all files in the input directory
    input_files = os.listdir(input_dir)
    for i, filename in enumerate(input_files):
        # Check if the file is a CSV file
        logger.info(f"Processing... {i+1}/{len(input_files)}: {filename}")
        if filename.endswith((".csv", ".feather", ".parquet")):
            t1 = time.time()
            logger.info(f"\tConverting {filename} to the {file_format} format")

            # Read the CSV file
            df = load_input_data(os.path.join(input_dir, filename), logger=logger)

            # rename fstar_gaia to is_fstar_gaia
            if rename_cols is not None:
                logger.info(f"\tRenaming columns: {rename_cols}")
                df.rename(columns=rename_cols, inplace=True)

            # add input_catalog_id if input_catalog_name is not provided
            if input_catalog_id is not None:
                if input_catalog_name is None:
                    logger.info(f"\tAdding input_catalog_id: {input_catalog_id}")
                    df["input_catalog_id"] = input_catalog_id
                else:
                    logger.warning(
                        "\tBoth input_catalog_id and input_catalog_name are provided. "
                        "Using input_catalog_name."
                    )

            if input_catalog_name is not None:
                logger.info(f"\tAdding input_catalog_name: {input_catalog_name}")
                df["input_catalog_name"] = input_catalog_name

            # add version column to df as strings
            logger.info(f"\tAdding version string: {version}")
            df["version"] = version

            # Convert the filename from .csv to pyarrow formats
            filename_body = f"{os.path.splitext(filename)[0]}"
            if file_format == "parquet":
                parquet_filename = f"{filename_body}.parquet"
                # Write the DataFrame to a Parquet file
                df.to_parquet(os.path.join(output_dir, parquet_filename), index=False)
            elif file_format == "feather":
                feather_filename = f"{filename_body}.feather"
                # Write the DataFrame to a Feather file
                df.to_feather(os.path.join(output_dir, feather_filename))
            t2 = time.time()
            logger.info(
                f"Done. Conversion took {t2-t1:.2f} seconds for {df.index.size} rows\n"
            )
        else:
            logger.warning(
                f"Skipping... {filename} does not end with one of .csv, .feather, and .parquet"
            )


def make_proposal_data(
    dfs, sheetname_proposal="proposals", sheetname_allocation="allocation"
):
    """
    Create a new DataFrame from the 'proposals' and 'allocation' DataFrames.

    Parameters
    ----------
    dfs : dict
        Dictionary containing two pandas DataFrames, 'proposals' and 'allocation',
        corresponding to the "Proposals" and "Allocation" sheets in the input Excel file.

    Returns
    -------
    DataFrame
        A new DataFrame with selected columns from the 'proposals' and 'allocation' DataFrames.

    """

    df_proposals = pd.DataFrame(
        {
            "proposal_id": dfs[sheetname_proposal]["proposal_id"],
            "group_id": dfs[sheetname_proposal]["group_id"],
            "pi_first_name": dfs[sheetname_proposal]["pi_first_name"],
            "pi_last_name": dfs[sheetname_proposal]["pi_last_name"],
            "pi_middle_name": dfs[sheetname_proposal]["pi_middle_name"],
            "rank": dfs[sheetname_allocation]["rank"],
            "grade": dfs[sheetname_allocation]["grade"],
            "allocated_time_total": dfs[sheetname_allocation]["allocated_time_total"],
            "allocated_time_lr": dfs[sheetname_allocation]["allocated_time_lr"],
            "allocated_time_mr": dfs[sheetname_allocation]["allocated_time_mr"],
            "proposal_category_name": dfs[sheetname_proposal]["proposal_category_name"],
        }
    )
    return df_proposals.dropna(how="all")


def make_input_catalog_data(
    dfs, sheetname_proposal="proposals", sheetname_allocation="allocation"
):
    """
    Create a new DataFrame from the 'proposal' DataFrame for input catalog data.

    Parameters
    ----------
    dfs : dict
        Dictionary containing a pandas DataFrame, 'proposal',
        corresponding to the "Proposals" sheet in the input Excel file.

    Returns
    -------
    DataFrame
        A new DataFrame with selected columns from the 'proposal' DataFrame related to input catalog data.

    """
    df_input_catalog = pd.DataFrame(
        {
            "input_catalog_name": dfs[sheetname_proposal]["input_catalog_name"],
            "input_catalog_description": dfs[sheetname_proposal][
                "input_catalog_description"
            ],
            "upload_id": dfs[sheetname_proposal]["upload_id"],
            "proposal_id": dfs[sheetname_proposal]["proposal_id"],
        }
    )
    return df_input_catalog.dropna(how="all")


def parse_allocation_file(input_file, output_dir=Path("."), outfile_prefix=None):

    dataframes = read_excel(input_file)

    try:
        logger.info(f"\n{dataframes['proposals']}")
        logger.info(f"\n{dataframes['allocation']}")
    except KeyError as e:
        logger.error(f"KeyError: {e}")
        raise e

    # create a proposal list
    df_proposals = make_proposal_data(dataframes)

    # create a input_catalog list
    df_input_catalog = make_input_catalog_data(dataframes)

    logger.info(f"\n{df_proposals}")
    logger.info(f"\n{df_input_catalog}")

    # save the dataframes to csv files
    if outfile_prefix is not None:
        outfile_proposals = output_dir / f"{outfile_prefix}_proposals.csv"
        outfile_input_catalog = output_dir / f"{outfile_prefix}_input_catalogs.csv"
    else:
        outfile_proposals = output_dir / "proposals.csv"
        outfile_input_catalog = output_dir / "input_catalogs.csv"

    df_proposals.to_csv(outfile_proposals, index=False)
    df_input_catalog.to_csv(outfile_input_catalog, index=False)


def transfer_data_from_uploader(
    df,
    config,
    local_dir=Path("."),
    force=False,
):
    status = []
    n_transfer = []
    # is_user_ppc = []

    for upload_id in df["upload_id"]:
        # datadirs = glob.glob(local_dir / f"????????-??????-{upload_id}")
        # datadirs = list(local_dir.cwd().glob(f"????????-??????-{upload_id}"))
        datadirs = list(local_dir.glob(f"????????-??????-{upload_id}"))
        skip_transfer = False
        # logger.info(f"{local_dir=} {local_dir.cwd()} {len(datadirs)=}")
        if len(datadirs) == 1:
            skip_transfer = True if not force else False
            if skip_transfer:
                logger.info(
                    f"Data directory, {datadirs[0]}, is found locally. Skip transfer"
                )
            else:
                logger.info(
                    f"Data directory, {datadirs[0]}, is found locally, but force transfer"
                )
        elif len(datadirs) > 1:
            logger.error(
                f"Multiple data directories are found in the destination directory: {datadirs}."
            )
            raise ValueError(
                f"Multiple data directories are found in the destination directory for {upload_id}: {datadirs}"
            )
        else:
            logger.info(
                f"Data directory for upload_id: {upload_id} is not found locally. Try transfer"
            )

        if not skip_transfer:
            logger.info(
                f"Transferring data for upload_id: {upload_id} from the uploader server"
            )

            # Define the source and destination directories
            source_dir = os.path.join(
                config["uploader"]["data_dir"], f"????/??/????????-??????-{upload_id}"
            )
            dest_dir = local_dir.as_posix()
            logger.info(
                f"Searching for the source directory on the remote host: {source_dir}"
            )

            # Construct the rsync command
            if config["uploader"]["host"] == "localhost":
                rsync_remote = f"{source_dir}"
                # rsync_command = [
                #     "rsync",
                #     "-av",
                #     rsync_remote,
                #     dest_dir,
                # ]
                rsync_command = f"rsync -av --ignore-times {rsync_remote} {dest_dir}"
                use_shell = True
            else:
                if (
                    "user" in config["uploader"].keys()
                    and config["uploader"]["user"] != ""
                ):
                    rsync_remote = f"{config['uploader']['user']}@{config['uploader']['host']}:{source_dir}"
                else:
                    rsync_remote = f"{config['uploader']['host']}:{source_dir}"

                rsync_command = [
                    "rsync",
                    "-avz",
                    "--ignore-times",
                    "-e",
                    "ssh",
                    rsync_remote,
                    dest_dir,
                ]
                use_shell = False

            # Execute the rsync command
            try:
                proc = subprocess.run(
                    rsync_command,
                    shell=use_shell,
                    check=True,
                    stdout=subprocess.PIPE,
                    encoding="utf-8",
                )
                logger.info(f"{source_dir=} {dest_dir=}")
                logger.info(f"{proc.stdout}")
                str_uploaded_dirs = [
                    line
                    for line in proc.stdout.splitlines()
                    if upload_id in line
                    if line.endswith("/")
                ]
                logger.info(f"Transferred directories: {str_uploaded_dirs}")

                n_dirs = len(str_uploaded_dirs)
                n_transfer.append(n_dirs)

                if n_dirs == 1:
                    status.append("success")
                else:
                    status.append("WARNING")
                # is_user_ppc.append(True)
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to transfer data for upload_id: {upload_id}")
                logger.error(e)
                # raise Exception(f"Failed to transfer data for upload_id: {upload_id}")
                # raise
                n_transfer.append(0)
                status.append("FAILED")
                # is_user_ppc.append(False)
        else:
            status.append("skipped")
            n_transfer.append(0)
            # is_user_ppc.append(False)

    custom_status_dict = {"success": 0, "WARNING": 1, "FAILED": 3}
    df_status = pd.DataFrame(
        {
            "upload_id": df["upload_id"],
            "status": status,
            "n_transfer": n_transfer,
            # "is_user_ppc": is_user_ppc,
        }
    )
    df_status.sort_values(by=["status"], key=lambda x: x.map(custom_status_dict))
    df_status_out = df_status.sort_values(
        by=["status"], key=lambda x: x.map(custom_status_dict)
    )
    logger.info(f"Transfer status: \n{df_status_out.to_string(index=False)}")

    if np.all(df_status["status"] == "success"):
        logger.info("All data transfer is successful.")
    else:
        logger.error(
            "There are some issues with data transfer. Please check the status."
        )


def insert_targets_from_uploader(
    df_input_catalogs,
    config,
    data_dir=Path("."),
    file_prefix="target",
    commit=False,
    fetch=False,
    verbose=False,
):

    for _, row in df_input_catalogs.iterrows():
        proposal_id = row["proposal_id"]
        upload_id = row["upload_id"]

        # input_file = list(
        #     data_dir.cwd().glob(
        #         f"????????-??????-{upload_id}/{file_prefix}_{upload_id}.ecsv"
        #     )
        # )
        input_file = list(
            data_dir.glob(f"????????-??????-{upload_id}/{file_prefix}_{upload_id}.ecsv")
        )

        if len(input_file) == 0:
            logger.error(f"Input file for upload_id: {upload_id} is not found.")
            raise FileNotFoundError(
                f"Input file for upload_id: {upload_id} is not found."
            )
        elif len(input_file) > 1:
            logger.error(f"Multiple input files are found for upload_id: {upload_id}")
            raise ValueError(
                f"Multiple input files are found for upload_id: {upload_id}"
            )

        logger.info(f"Loading input data from {input_file} into a DataFrame")
        t_begin = time.time()
        df = load_input_data(input_file[0])
        t_end = time.time()
        logger.info(f"Loaded input data in {t_end - t_begin:.2f} seconds")

        add_database_rows(
            input_file=input_file[0],
            table="target",
            commit=commit,
            fetch=fetch,
            verbose=verbose,
            config=config,
            df=df,
            from_uploader=True,
            proposal_id=proposal_id,
            upload_id=upload_id,
            insert=True,
        )


def update_input_catalog_active(
    input_catalog_id: int,
    active_flag: bool,
    config: dict,
    commit: bool = False,
    verbose: bool = False,
):
    """
    Update the active status of an input catalog in the database.

    Parameters
    ----------
    input_catalog_id : int
        The ID of the input catalog to be updated.
    active_flag : bool
        The new active status to set for the input catalog.
    config : dict
        Configuration dictionary containing database connection details.
    commit : bool, optional
        If True, commit the changes to the database. If False, perform a dry run
        without committing the changes. Default is False.
    verbose : bool, optional
        If True, log additional information about the update process. Default is False.

    Notes
    -----
    This function connects to the database, updates the active status of the specified
    input catalog, and optionally commits the changes. If `verbose` is enabled, it logs
    detailed information about the update process, including the updated table contents
    after the operation.

    Examples
    --------
    >>> config = {
    ...     "targetdb": {
    ...         "db": {
    ...             "host": "localhost",
    ...             "port": 5432,
    ...             "user": "user",
    ...             "password": "password",
    ...             "database": "targetdb"
    ...         }
    ...     }
    ... }
    >>> update_input_catalog_active(123, True, config, commit=True, verbose=True)
    """

    db = TargetDB(**config["targetdb"]["db"])
    db.connect()

    df = pd.DataFrame(
        {"input_catalog_id": [input_catalog_id], "active": [active_flag]},
        # index="input_catalog_id",
    )

    if verbose:
        logger.info(
            f"Updating input_catalog_id {input_catalog_id} to active={active_flag}"
        )
        df_res = db.fetch_by_id(
            "input_catalog",
            input_catalog_id=input_catalog_id,
        )
        logger.info(f"Original input_catalog table: \n{df_res}")

    if commit:
        logger.info(
            f"Updating input_catalog_id {input_catalog_id} to active={active_flag}"
        )
    else:
        logger.info(
            f"Updating input_catalog_id {input_catalog_id} to active={active_flag} (dry run)"
        )

    db.update("input_catalog", df, dry_run=not commit)

    if verbose:
        df_res = db.fetch_by_id(
            "input_catalog",
            input_catalog_id=input_catalog_id,
        )
        logger.info(f"Updated input_catalog table: \n{df_res}")

    db.close()
