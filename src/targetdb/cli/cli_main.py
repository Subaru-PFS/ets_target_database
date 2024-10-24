#!/usr/bin/env python3
import json
import time
from enum import Enum
from pathlib import Path
from typing import Annotated, List, Optional

import rich
import typer
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists, drop_database

from ..utils import (
    add_database_rows,
    check_duplicates,
    draw_diagram,
    generate_schema_markdown,
    get_url_object,
    insert_targets_from_uploader,
    install_q3c_extension,
    load_config,
    load_input_data,
    parse_allocation_file,
    prep_fluxstd_data,
    transfer_data_from_uploader,
)

app = typer.Typer(
    help="PFS Target Database CLI Tool",
    context_settings={"help_option_names": ["--help", "-h"]},
    add_completion=False,
)


class DiagramGenerator(str, Enum):
    schemacrawler = "schemacrawler"
    tbls = "tbls"


class PyArrowFileFormat(str, Enum):
    feather = "feather"
    parquet = "parquet"


class TargetdbTable(str, Enum):
    filter_name = "filter_name"
    fluxstd = "fluxstd"
    input_catalog = "input_catalog"
    pfs_arm = "pfs_arm"
    proposal = "proposal"
    proposal_category = "proposal_category"
    sky = "sky"
    target = "target"
    target_type = "target_type"
    user_pointing = "user_pointing"


config_help_msg = "Database configuration file in the TOML format."


@app.command(help="Create a database on a PostgreSQL server.")
def create_db(
    config_file: Annotated[
        str,
        typer.Option(
            "-c",
            "--config",
            show_default=False,
            help=config_help_msg,
        ),
    ],
):
    config = load_config(config_file)
    url_object = get_url_object(config)
    engine = create_engine(url_object)

    if not database_exists(engine.url):
        logger.info(f"Creating database: {url_object.render_as_string()}")
        create_database(engine.url)
    else:
        logger.info(f"Database already exists: {url_object.render_as_string()}")


@app.command(help="Drop a database on a PostgreSQL server.")
def drop_db(
    config_file: Annotated[
        str,
        typer.Option(
            "-c",
            "--config",
            show_default=False,
            help=config_help_msg,
        ),
    ],
):
    config = load_config(config_file)
    url_object = get_url_object(config)
    engine = create_engine(url_object)

    if database_exists(engine.url):
        rich.print(
            f"DANGER: you are going to delete the database, {url_object.render_as_string()}"
        )
        # proceed = query_yes_no("Proceed? ", default="no")
        is_drop = typer.confirm("Are you sure you want to drop the database?")
        if is_drop:
            logger.info(f"Dropping database: {url_object.render_as_string()}")
            drop_database(engine.url)
    else:
        logger.info("Database does not exist: {url_object.render_as_string()}")


@app.command(help="Insert the Q3C extension.")
def install_q3c(
    config_file: Annotated[
        str,
        typer.Option(
            "-c",
            "--config",
            show_default=False,
            help=config_help_msg,
        ),
    ],
):
    config = load_config(config_file)

    install_q3c_extension(config)


@app.command(help="Create tables of the PFS tartedb in a database.")
def create_schema(
    config_file: Annotated[
        str,
        typer.Option(
            "-c",
            "--config",
            show_default=False,
            help=config_help_msg,
        ),
    ],
    drop_all: Annotated[
        bool,
        typer.Option(
            "--drop-all",
            help="Flag to drop all tables before creating schema.",
        ),
    ] = False,
):
    from ..manage import create_database_schema

    config = load_config(config_file)

    url_object = get_url_object(config)

    if drop_all:
        rich.print(
            f"DANGER: you are going to drop all tables in the database, {url_object.render_as_string()}"
        )
        _ = typer.confirm(
            "Are you sure you want to drop all the tabls in the database before creating the schema?",
            abort=True,
        )

    logger.info(f"Creating schema in the database: {url_object.render_as_string()}")
    create_database_schema(url_object, drop_all=drop_all)


@app.command(help="Check for duplicates in data files in a directory.")
def checkdups(
    directory: Annotated[
        str,
        typer.Argument(
            show_default=False,
            help="Directory path containing input files.",
        ),
    ],
    output_dir: Annotated[
        str,
        typer.Option(
            "-o",
            "--outdir",
            help="Directory path to save output files.",
        ),
    ] = ".",
    skip_save_merged: Annotated[
        bool,
        typer.Option("--skip-save-merged", help="Do not save the merged DataFrame."),
    ] = False,
    additional_columns: Annotated[
        List[str],
        typer.Option(
            "--additional-columns",
            help="Additional columns to output for the merged file.  (e.g., 'psf_mag_g' 'psf_mag_r'). "
            "The following columns are saved by default: "
            '"obj_id", "ra", "dec", "input_catalog_id", "version", "input_file", "is_fstar_gaia", "prob_f_star".',
        ),
    ] = None,
    check_columns: Annotated[
        List[str],
        typer.Option(
            "--check-columns",
            help="Columns used to check for duplicates.",
        ),
    ] = ["obj_id", "input_catalog_id", "version"],
    file_format: Annotated[
        PyArrowFileFormat,
        typer.Option(
            "--format",
            help="File format of the merged data file.",
        ),
    ] = "parquet",
):
    if additional_columns is None:
        additional_columns = []

    check_duplicates(
        indir=directory,
        outdir=output_dir,
        file_format=file_format,
        skip_save_merged=skip_save_merged,
        additional_columns=additional_columns,
        check_columns=check_columns,
    )


@app.command(
    help="Prepare flux standard data for the target database by supplementing additional required fields."
)
def prep_fluxstd(
    input_dir: Annotated[
        str,
        typer.Argument(
            show_default=False,
            help="Directory path containing input files. "
            "Files must be in one of the following formats: parquet, feather, or csv. "
            "The input files must be generated in a certain format to be compatible for targetdb.",
        ),
    ],
    output_dir: Annotated[
        str,
        typer.Argument(
            show_default=False, help="Directory path to save the output files."
        ),
    ],
    version: Annotated[
        str,
        typer.Option(
            "--version",
            show_default=False,
            help="Version **string** for the F-star candidate catalog (e.g., '3.3').",
        ),
    ],
    input_catalog_id: Annotated[
        int,
        typer.Option(
            "--input_catalog_id",
            show_default=False,
            help="Input catalog ID for the flux standard star catalog.",
        ),
    ] = None,
    input_catalog_name: Annotated[
        str,
        typer.Option(
            "--input_catalog_name",
            show_default=False,
            help="Input catalog name for the flux standard star catalog.",
        ),
    ] = None,
    rename_cols: Annotated[
        str,
        typer.Option(
            "--rename-cols",
            help='Dictionary to rename columns (e.g., \'{"fstar_gaia": "is_fstar_gaia"}\').',
        ),
    ] = None,
    file_format: Annotated[
        PyArrowFileFormat,
        typer.Option(
            "--format",
            help="File format of the output data file.",
        ),
    ] = "parquet",
):

    if input_catalog_id is None and input_catalog_name is None:
        raise typer.BadParameter(
            "Either input_catalog_id or input_catalog_name must be provided."
        )

    if rename_cols is not None:
        rename_cols = json.loads(rename_cols)

    prep_fluxstd_data(
        input_dir,
        output_dir,
        version,
        input_catalog_id,
        input_catalog_name,
        rename_cols=rename_cols,
        file_format=file_format,
    )


@app.command(help="Generate an ER diagram of a database.")
def diagram(
    config_file: Annotated[
        str,
        typer.Option(
            "-c",
            "--config",
            show_default=False,
            help=config_help_msg,
        ),
    ],
    generator: Annotated[
        DiagramGenerator,
        typer.Option(
            "--generator",
            case_sensitive=False,
            help="Program to generate ER diagram.",
        ),
    ] = DiagramGenerator.schemacrawler,
    output_dir: Annotated[
        str, typer.Option("--output-dir", help="Directory path to save output files.")
    ] = "diagram",
    title: Annotated[
        str, typer.Option("--title", help="Title of the ER diagram.")
    ] = "PFS Target Database",
    sc_info_level: Annotated[
        str, typer.Option("--sc-info-level", help="SchemaCrawler info level.")
    ] = "maximum",
    sc_log_level: Annotated[
        str, typer.Option("--sc-level-level", help="SchemaCrawler log level.")
    ] = "SEVERE",
    sc_outprefix: Annotated[
        str, typer.Option("--sc-outprefix", help="Output file prefix.")
    ] = "erdiagram_targetdb",
    tbls_format: Annotated[
        str, typer.Option("--tbls-format", help="tbls format for ER diagrams.")
    ] = "mermaid",
):

    config = load_config(config_file)

    draw_diagram(
        config,
        generator=generator,
        output_dir=output_dir,
        title=title,
        sc_info_level=sc_info_level,
        sc_log_level=sc_log_level,
        sc_outprefix=sc_outprefix,
        logger=logger,
    )


@app.command(
    help="Generate a Markdown output of the schema of the PFS Target Database."
)
def mdtable(
    output_file: Annotated[
        Optional[str], typer.Option("--output-file", "-o", help="Output file.")
    ] = None
):
    generate_schema_markdown(output_file=output_file)


@app.command(help="Insert rows into a table in the PFS Target Database.")
def insert(
    input_file: Annotated[
        str,
        typer.Argument(
            show_default=False,
            help="Input file to be inserted to targetdb (CSV, ECSV, Feather, or Parquet format).",
        ),
    ],
    config_file: Annotated[
        str,
        typer.Option(
            "-c",
            "--config",
            show_default=False,
            help=config_help_msg,
        ),
    ],
    table: Annotated[
        TargetdbTable,
        typer.Option(
            "-t", "--table", show_default=False, help="Table name to insert rows."
        ),
    ],
    commit: Annotated[
        bool,
        typer.Option("--commit", help="Commit changes to the database."),
    ] = False,
    fetch: Annotated[
        bool, typer.Option("--fetch", help="Fetch data from database a the end.")
    ] = False,
    from_uploader: Annotated[
        bool,
        typer.Option(
            "--from-uploader",
            help="Flag to indicate the data is coming from the PFS Target Uploader. Only required for the `target` table.",
        ),
    ] = False,
    upload_id: Annotated[
        str,
        typer.Option(
            "--upload_id",
            show_default=False,
            help="Upload ID issued by the PFS Target Uploader. Only required for the `target` table.",
        ),
    ] = None,
    proposal_id: Annotated[
        str,
        typer.Option(
            "--proposal_id",
            show_default=False,
            help="Proposal ID (e.g., S24B-QT001). Only required for the `target` table.",
        ),
    ] = None,
    verbose: Annotated[
        bool, typer.Option("-v", "--verbose", help="Verbose output.")
    ] = False,
):
    logger.info(f"Loading config file: {config_file}")
    config = load_config(config_file)

    logger.info(f"Loading input data from {input_file} into a DataFrame")
    t_begin = time.time()
    df = load_input_data(input_file)
    t_end = time.time()
    logger.info(f"Loaded input data in {t_end - t_begin:.2f} seconds")

    add_database_rows(
        input_file=input_file,
        table=table,
        commit=commit,
        fetch=fetch,
        verbose=verbose,
        config=config,
        df=df,
        from_uploader=from_uploader,
        proposal_id=proposal_id,
        upload_id=upload_id,
        insert=True,
    )


@app.command(help="Update rows in a table in the PFS Target Database.")
def update(
    input_file: Annotated[
        str,
        typer.Argument(
            show_default=False,
            help="Input file containing data to update records in the PFS Target Database (CSV, ECSV, or Feather formats).",
        ),
    ],
    config_file: Annotated[
        str,
        typer.Option(
            "-c",
            "--config",
            show_default=False,
            help=config_help_msg,
        ),
    ],
    table: Annotated[
        TargetdbTable,
        typer.Option(
            "-t", "--table", show_default=False, help="Table name to update rows."
        ),
    ],
    commit: Annotated[
        bool,
        typer.Option("--commit", help="Commit changes to the database."),
    ] = False,
    fetch: Annotated[
        bool, typer.Option("--fetch", help="Fetch data from database a the end.")
    ] = False,
    from_uploader: Annotated[
        bool,
        typer.Option(
            "--from-uploader",
            help="Flag to indicate the data is coming from the PFS Target Uploader. Only required for the `target` table.",
        ),
    ] = False,
    upload_id: Annotated[
        str,
        typer.Option(
            "--upload_id",
            show_default=False,
            help="Upload ID issued by the PFS Target Uploader. Only required for the `target` table",
        ),
    ] = None,
    proposal_id: Annotated[
        str,
        typer.Option(
            "--proposal_id",
            show_default=False,
            help="Proposal ID (e.g., S24B-QT001). Only required for the `target` table",
        ),
    ] = None,
    verbose: Annotated[bool, typer.Option("--verbose", help="Verbose output.")] = False,
):
    logger.info(f"Loading config file: {config_file}")
    config = load_config(config_file)

    logger.info(f"Loading input data from {input_file} into a DataFrame")
    t_begin = time.time()
    df = load_input_data(input_file)
    t_end = time.time()
    logger.info(f"Loaded input data in {t_end - t_begin:.2f} seconds")

    add_database_rows(
        input_file=input_file,
        table=table,
        commit=commit,
        fetch=fetch,
        verbose=verbose,
        config=config,
        df=df,
        from_uploader=from_uploader,
        proposal_id=proposal_id,
        upload_id=upload_id,
        update=True,
    )


@app.command(help="Parse an Excel file containing time allocation information.")
def parse_alloc(
    input_file: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            show_default=False,
            help='Path to the Excel file containing time allocation information (e.g., "allocations.xlsx").',
        ),
    ],
    output_dir: Annotated[
        Path,
        typer.Option(
            exists=True,
            dir_okay=True,
            writable=True,
            help="Directory path to save output files.",
        ),
    ] = ".",
    outfile_prefix: Annotated[
        str,
        typer.Option(
            show_default=False,
            help="Prefix to the output files.",
        ),
    ] = None,
):
    parse_allocation_file(
        input_file, output_dir=output_dir, outfile_prefix=outfile_prefix
    )


@app.command(help="Download target lists from the uploader to the local machine.")
def transfer_targets(
    input_file: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            show_default=False,
            help="Input catalog list file (csv).",
        ),
    ],
    config_file: Annotated[
        str,
        typer.Option(
            "-c",
            "--config",
            show_default=False,
            help=config_help_msg,
        ),
    ],
    local_dir: Annotated[
        Path,
        typer.Option(
            exists=True,
            dir_okay=True,
            writable=True,
            help="Path to the data directory in the local machine",
        ),
    ] = ".",
    force: Annotated[bool, typer.Option(help="Force download.")] = False,
):

    # print(check_ppc)
    logger.info(f"Loading config file: {config_file}")
    config = load_config(config_file)

    logger.info(f"Loading input data from {input_file} into a DataFrame")
    df = load_input_data(input_file)

    transfer_data_from_uploader(
        df,
        config,
        local_dir=local_dir,
        force=force,
    )


@app.command(help="Insert targets using a list of input catalogs and upload IDs.")
def insert_targets(
    input_catalogs: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            show_default=False,
            help="Input catalog list to insert (csv).",
        ),
    ],
    config_file: Annotated[
        str,
        typer.Option(
            "-c",
            "--config",
            show_default=False,
            help=config_help_msg,
        ),
    ],
    data_dir: Annotated[
        Path,
        typer.Option(
            exists=True,
            dir_okay=True,
            readable=True,
            help="Path to the data directory.",
        ),
    ] = ".",
    commit: Annotated[
        bool,
        typer.Option("--commit", help="Commit changes to the database."),
    ] = False,
    fetch: Annotated[
        bool, typer.Option("--fetch", help="Fetch data from database a the end.")
    ] = False,
    verbose: Annotated[
        bool, typer.Option("-v", "--verbose", help="Verbose output.")
    ] = False,
):
    logger.info(f"Loading config file: {config_file}")
    config = load_config(config_file)

    logger.info(f"Loading input catalog data from {input_catalogs} into a DataFrame")
    df_input_catalogs = load_input_data(input_catalogs)

    insert_targets_from_uploader(
        df_input_catalogs,
        config,
        data_dir=data_dir,
        commit=commit,
        fetch=fetch,
        verbose=verbose,
    )


if __name__ == "__main__":
    pass
