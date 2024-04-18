#!/usr/bin/env python3

import json
import sys
import time
from enum import Enum
from typing import List

import rich
import typer
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists, drop_database
from typing_extensions import Annotated, Optional

from ..utils import (
    add_database_rows,
    check_fluxstd_dups,
    draw_diagram,
    generate_schema_markdown,
    get_url_object,
    load_config,
    load_input_data,
    prep_fluxstd_data,
)

app = typer.Typer(help="PFS Target Database CLI Tool")


@app.command(help="Create a database on a PostgreSQL server.")
def create_db(
    config_file: Annotated[
        str,
        typer.Option(
            "-c",
            "--config",
            show_default=False,
            help="Database configuration file (.toml)",
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
            help="Database configuration file (.toml)",
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


@app.command(help="Create tables of the PFS tartedb in a database.")
def create_schema(
    config_file: Annotated[
        str,
        typer.Option(
            "-c",
            "--config",
            show_default=False,
            help="Database configuration file (.toml)",
        ),
    ],
    drop_all: Annotated[
        bool,
        typer.Option(
            "--drop-all",
            help="Drop all tables before creating schema. (Default: False)",
        ),
    ] = False,
):
    from ..manage import create_schema

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
        create_schema(url_object, drop_all=drop_all)


@app.command(help="Check for duplicates in data files in a directory.")
def checkdups(
    directory: Annotated[
        str,
        typer.Argument(
            show_default=False,
            help="Directory path containing input files",
        ),
    ],
    file_format: Annotated[
        str,
        typer.Option(
            "--format",
            help="File format of the merged data file, feather or parquet",
        ),
    ] = "parquet",
    output_dir: Annotated[
        str,
        typer.Option(
            "-o",
            "--outdir",
            help="Path to output directory.",
        ),
    ] = ".",
    skip_save_merged: Annotated[
        bool,
        typer.Option("--skip-save-merged", help="Do not save the merged DataFrame"),
    ] = False,
    additional_columns: Annotated[
        List[str],
        typer.Option(
            "--additional-columns",
            help="Additional columns to output for the merged file.  (e.g., 'psf_mag_g' 'psf_mag_r'). "
            "The following columns are saved by default: "
            '"obj_id", "ra", "dec", "input_catalog_id", "version", "input_file", "is_fstar_gaia", "prob_f_star"',
        ),
    ] = [],
    check_columns: Annotated[
        List[str],
        typer.Option(
            "--check-columns",
            help="Columns used to check for duplicates. (default: obj_id, input_catalog_id, version)",
        ),
    ] = ["obj_id", "input_catalog_id", "version"],
):

    check_fluxstd_dups(
        indir=directory,
        outdir=output_dir,
        format=file_format,
        skip_save_merged=skip_save_merged,
        additional_columns=additional_columns,
        check_columns=check_columns,
    )


@app.command(
    help="Prepare flux standard data for the target database by supplementing additional required fields."
)
def prep_fluxstd(
    directory: Annotated[
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
            help="Version **string** for the F-star candidate catalog (e.g., '3.3')",
        ),
    ],
    input_catalog_id: Annotated[
        int,
        typer.Option(
            "--input_catalog_id",
            show_default=False,
            help="Input catalog ID for the F-star candidate catalog",
        ),
    ],
    rename_cols: Annotated[
        str,
        typer.Option(
            "--rename-cols",
            help='Dictionary to rename columns (e.g., \'{"fstar_gaia": "is_fstar_gaia"}\')',
        ),
    ] = None,
    file_format: Annotated[
        str,
        typer.Option(
            "--format",
            help="File format of the merged data file, feather or parquet",
        ),
    ] = "parquet",
):
    if rename_cols is not None:
        rename_cols = json.loads(rename_cols)

    prep_fluxstd_data(
        directory,
        output_dir,
        version,
        input_catalog_id,
        rename_cols=rename_cols,
        format=file_format,
    )


class DiagramGenerator(str, Enum):
    schemacrawler = "schemacrawler"
    tbls = "tbls"


@app.command(help="Generate an ER diagram of a database.")
def diagram(
    config_file: Annotated[
        str,
        typer.Option(
            "-c",
            "--config",
            show_default=False,
            help="Database configuration file (.toml)",
        ),
    ],
    generator: Annotated[
        DiagramGenerator,
        typer.Option(
            "--generator",
            case_sensitive=False,
            help="Program to generate ER diagram (schemacrawler or tbls)",
        ),
    ] = DiagramGenerator.schemacrawler,
    output_dir: Annotated[
        str, typer.Option("--output-dir", help="Output directory")
    ] = "diagram",
    title: Annotated[
        str, typer.Option("--title", help="Title of the ER diagram")
    ] = "PFS Target Database",
    sc_info_level: Annotated[
        str, typer.Option("--sc-info-level", help="SchemaCrawler info level")
    ] = "maximum",
    sc_log_level: Annotated[
        str, typer.Option("--sc-level-level", help="SchemaCrawler log level")
    ] = "SEVERE",
    sc_outprefix: Annotated[
        str, typer.Option("--sc-outprefix", help="Output file prefix")
    ] = "erdiagram_targetdb",
    tbls_format: Annotated[
        str, typer.Option("--tbls-format", help="tbls format")
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
        Optional[str], typer.Option("--output-file", "-o", help="Output file")
    ] = None
):
    generate_schema_markdown(output_file=output_file)


@app.command(help="Insert rows into a table in the PFS Target Database.")
def insert(
    input_file: Annotated[
        str,
        typer.Argument(
            show_default=False,
            help="Input file to be inserted to targetdb (CSV, ECSV, Feather, or Parquet format)",
        ),
    ],
    config_file: Annotated[
        str,
        typer.Option(
            "-c",
            "--config",
            show_default=False,
            help="Database configuration file (.toml)",
        ),
    ],
    table: Annotated[
        str,
        typer.Option(
            "-t", "--table", show_default=False, help="Table name to insert data"
        ),
    ],
    commit: Annotated[
        bool,
        typer.Option("--commit", help="Commit changes to the database"),
    ] = False,
    fetch: Annotated[
        bool, typer.Option("--fetch", help="Fetch data from database a the end")
    ] = False,
    from_uploader: Annotated[
        bool,
        typer.Option(
            "--from_uploader",
            help="Flag to indicate the data is coming from the PFS Target Uploader. Only required for the target table",
        ),
    ] = False,
    upload_id: Annotated[
        str,
        typer.Option(
            "--upload_id",
            show_default=False,
            help="Upload ID issued by the PFS Target Uploader. Only required for the target table",
        ),
    ] = None,
    proposal_id: Annotated[
        str,
        typer.Option(
            "--proposal_id",
            show_default=False,
            help="Proposal ID (e.g., S24B-QT001). Only required for the target table",
        ),
    ] = None,
    verbose: Annotated[
        bool, typer.Option("-v", "--verbose", help="Verbose output")
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
            help="Input file to be inserted to targetdb (CSV, ECSV, Feather, or Parquet format)",
        ),
    ],
    config_file: Annotated[
        str,
        typer.Option(
            "-c",
            "--config",
            show_default=False,
            help="Database configuration file (.toml)",
        ),
    ],
    table: Annotated[
        str,
        typer.Option(
            "-t", "--table", show_default=False, help="Table name to insert data"
        ),
    ],
    commit: Annotated[
        bool,
        typer.Option("--commit", help="Commit changes to the database"),
    ] = False,
    fetch: Annotated[
        bool, typer.Option("--fetch", help="Fetch data from database a the end")
    ] = False,
    from_uploader: Annotated[
        bool,
        typer.Option(
            "--from_uploader",
            help="Flag to indicate the data is coming from the PFS Target Uploader. Only required for the target table",
        ),
    ] = False,
    upload_id: Annotated[
        str,
        typer.Option(
            "--upload_id",
            show_default=False,
            help="Upload ID issued by the PFS Target Uploader. Only required for the target table",
        ),
    ] = None,
    proposal_id: Annotated[
        str,
        typer.Option(
            "--proposal_id",
            show_default=False,
            help="Proposal ID (e.g., S24B-QT001). Only required for the target table",
        ),
    ] = None,
    verbose: Annotated[bool, typer.Option("--verbose", help="Verbose output")] = False,
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


if __name__ == "__main__":
    pass
