# Command-line tools for the PFS Target Database

The following command-line tools are available to work with the PFS Target Database.

## Config file

The command-line tools introduced below require a configuration file in TOML format. The configuration file should contain the following information and provided as an argument to the command-line tools with `--config` or `-c` option.:

```toml title="dbconf.toml"
[targetdb.db]
host = "localhost"  # database host
port = 5432 # database port
dbname = "targetdb" # database name
user = "admin" # database user
password = "admin" # database password
dialect = "postgresql" # database dialect

[schemacrawler]
SCHEMACRAWLERDIR = "<path to schemacrawler>"  # "_schemacrawler/bin/schemacrawler.sh" under the path will be used
```

## Database management

### Create a database

```text
$ pfs_targetdb_create_database --help

usage: pfs_targetdb_create_database [-h] -c CONFIG

Create a database on PostgreSQL.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Database config file (.toml)
```

### Drop a database

```text
$ pfs_targetdb_drop_database --help

usage: pfs_targetdb_drop_database [-h] -c CONFIG

Drop a database on PostgreSQL.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Database config file (.toml)
```

### Create tables

```text
$ pfs_targetdb_create_schema --help

usage: pfs_targetdb_create_schema [-h] -c CONFIG [--drop_all]

Create tables of the target dabatabase in a database.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Database config file (.toml)
  --drop_all            Drop all tables before creating schema. (Default: False)
```

## Flux standard data

### Duplication check

```text
$ pfs_targetdb_fluxstd_checkdups --help

usage: pfs_targetdb_fluxstd_checkdups [-h] [--format FORMAT] [-o OUTDIR] [--skip-save-merged] [--additional-columns [ADDITIONAL_COLUMNS ...]]
                                      [--check-columns [CHECK_COLUMNS ...]]
                                      dir

Check for duplicates in the F-star candidate files

positional arguments:
  dir                   Directory path containing input files

optional arguments:
  -h, --help            show this help message and exit
  --format FORMAT       File format to be used, feather or parquet (default: parquet)
  -o OUTDIR, --outdir OUTDIR
                        Path to output directory. (default: .)
  --skip-save-merged    Do not save the merged DataFrame as a feather or parquet file
  --additional-columns [ADDITIONAL_COLUMNS ...]
                        Additional columns to output for the merged file. (e.g., 'psf_mag_g' 'psf_mag_r'). The following columns are saved by
                        default: "obj_id", "ra", "dec", "input_catalog_id", "version", "input_file", "is_fstar_gaia", "prob_f_star"
  --check-columns [CHECK_COLUMNS ...]
                        Columns used to check for duplicates. (default: obj_id, input_catalog_id, version)
```

### Prepare fluxstd data file

```text
$ pfs_targetdb_fluxstd_prepdata --help

usage: pfs_targetdb_fluxstd_prepdata [-h] --version VERSION --input_catalog_id INPUT_CATALOG_ID [--rename-cols RENAME_COLS] [--format FORMAT]
                                     input_dir output_dir

Prepare flux standard data for the target database by supplementing additional required fields.

positional arguments:
  input_dir             Directory path containing input files. Files must be in one of the following formats: parquet, feather, or csv. The
                        input files must be generated in a certain format to be compatible for targetdb.
  output_dir            Directory path to save the output files.

optional arguments:
  -h, --help            show this help message and exit
  --version VERSION     Version **string** for the F-star candidate catalog (e.g., '3.3')
  --input_catalog_id INPUT_CATALOG_ID
                        Input catalog ID for the F-star candidate catalog
  --rename-cols RENAME_COLS
                        Dictionary to rename columns (e.g., '{"fstar_gaia": "is_fstar_gaia"}'; default is None)
  --format FORMAT       File format to be used, feather or parquet (default: parquet)
```

## Database manipulation

### Insert records

```text
$ pfs_targetdb_insert --help

usage: pfs_targetdb_insert [-h] -c CONFIG -t TABLE [--commit] [--fetch] [--from-uploader] [--upload_id UPLOAD_ID] [--proposal_id PROPOSAL_ID]
                           [-v]
                           input_file

Insert data to targetDB from an input file

positional arguments:
  input_file            Input file to be inserted to targetDB (CSV, ECSV, or Feather formats)

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Database config file (.toml)
  -t TABLE, --table TABLE
                        Table name in targetDB
  --commit              Commit the changes to the database (default: False)
  --fetch               Fetch all table entries and print (default: False)
  --upload_id UPLOAD_ID
                        Upload ID issued by the uploader (only valid for the target table)
  --proposal_id PROPOSAL_ID
                        Proposal ID (e.g., S24B-QT001; only valid for the target table)
  -v, --verbose         Verbose mode
```

### Update records

```text
$ pfs_targetdb_update --help

usage: pfs_targetdb_update [-h] -c CONFIG -t TABLE [--commit] [--fetch] [--from-uploader] [--upload_id UPLOAD_ID] [--proposal_id PROPOSAL_ID]
                           [-v]
                           input_file

Update data in targetDB from an input file

positional arguments:
  input_file            Input file to be inserted to targetDB (CSV, ECSV, or Feather formats)

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Database config file (.toml)
  -t TABLE, --table TABLE
                        Table name in targetDB
  --commit              Commit the changes to the database (default: False)
  --fetch               Fetch all table entries and print (default: False)
  --from-uploader       Target list from the PFS Target Uploader (only valid for the target table)
  --upload_id UPLOAD_ID
                        Upload ID issued by the uploader (only valid for the target table)
  --proposal_id PROPOSAL_ID
                        Proposal ID (e.g., S24B-QT001; only valid for the target table)
  -v, --verbose         Verbose mode
```

## Visualize database schema

### Draw an ER diagram

SchemaCrawler must be installed and is used to generate the ER diagram of the database. The output is saved as a PDF file.

```text
$ pfs_targetdb_draw_diagram --help

usage: pfs_targetdb_draw_diagram [-h] [--sc_info_level SC_INFO_LEVEL] [--sc_log_level SC_LOG_LEVEL] [--sc_outdir SC_OUTDIR]
                                 [--sc_outprefix SC_OUTPREFIX] [--sc_title SC_TITLE]
                                 conf

Create the ER diagram of the database in PDF

positional arguments:
  conf                  Config file for the script to run. Must be a .toml file (default: config.toml)

optional arguments:
  -h, --help            show this help message and exit
  --sc_info_level SC_INFO_LEVEL
                        SchemaCrawler's info level (default: maximum)
  --sc_log_level SC_LOG_LEVEL
                        SchemaCrawler's log level (default: SEVERE)
  --sc_outdir SC_OUTDIR
                        Output directory (default: .)
  --sc_outprefix SC_OUTPREFIX
                        Prefix for the output file (default: erdiagram_targetdb)
  --sc_title SC_TITLE   Title of the output ER diagram (default: PFS Target Database)
```

### Generate markdown tables

The ER diagram of the database is generated in Markdown format based on the SQLAlchemy models (not based on the database itself).

```text
$ pfs_targetdb_generate_mdtable --help

usage: pfs_targetdb_generate_mdtable [-h] [--schema_md SCHEMA_MD]

Create tables in targetDB in Markdown format.

optional arguments:
  -h, --help            show this help message and exit
  --schema_md SCHEMA_MD
                        Output markdown file to write tables in the database (Default: sys.stdout)
```
