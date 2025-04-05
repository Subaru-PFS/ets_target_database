# CLI Reference

The command-line interface (CLI) tool `pfs-targetdb-cli` is provided to work with the database.

??? note "Configuration file"

    Some commands of the CLI tool introduced below requires a configuration file in [TOML](https://toml.io/en/) format to connect the database.
    The configuration file should look like teh following and provided as an option by `--config` or `-c`.

    ```toml title="dbconf.toml"
    [targetdb.db]
    host = "localhost"  # database host
    port = 5432 # database port
    dbname = "targetdb" # database name
    user = "admin" # database user
    password = "admin" # database password
    dialect = "postgresql" # database dialect

    # Optional section for SchemaCrawler
    [schemacrawler]
    # "_schemacrawler/bin/schemacrawler.sh" under the path will be used
    SCHEMACRAWLERDIR = "<path to the schemacrawler package>"

    # The following parameters for the uploader will be used to rsync as follows.
    # $ rsync -avz -e ssh user@host:data_dir/????/??/????????-??????-{upload_id}
    # user can be omitted or blank ("") if the user name is the same as the local user name or an alias is defined in ~/.ssh/config.
    [uploader]
    host = "<hostname of uploader>"
    user = "<user name of uploader>"
    data_dir = "<path to the data directory on the uploader>"
    ```

    The `schemacrawler` section is required only if you want to draw an ER diagram of the database schema with SchemaCrawler.

## `pfs-targetdb-cli`

PFS Target Database CLI Tool

**Usage**:

```console
$ pfs-targetdb-cli [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `checkdups`: Check for duplicates in data files in a...
* `create-db`: Create a database on a PostgreSQL server.
* `create-schema`: Create tables of the PFS tartedb in a...
* `diagram`: Generate an ER diagram of a database.
* `drop-db`: Drop a database on a PostgreSQL server.
* `insert`: Insert rows into a table in the PFS Target...
* `insert-targets`: Insert targets using a list of input...
* `install-q3c`: Insert the Q3C extension.
* `mdtable`: Generate a Markdown output of the schema...
* `parse-alloc`: Parse an Excel file containing time...
* `prep-fluxstd`: Prepare flux standard data for the target...
* `transfer-targets`: Download target lists from the uploader to...
* `update`: Update rows in a table in the PFS Target...
* `update-catalog-active`: Update active flag in the input_catalog...

---

### `checkdups`

Check for duplicates in data files in a directory.

**Usage**:

```console
$ pfs-targetdb-cli checkdups [OPTIONS] DIRECTORY
```

**Arguments**:

* `DIRECTORY`: Directory path containing input files.  [required]

**Options**:

* `-o, --outdir TEXT`: Directory path to save output files.  [default: .]
* `--skip-save-merged`: Do not save the merged DataFrame.
* `--additional-columns TEXT`: Additional columns to output for the merged file.  (e.g., 'psf_mag_g' 'psf_mag_r'). The following columns are saved by default: "obj_id", "ra", "dec", "input_catalog_id", "version", "input_file", "is_fstar_gaia", "prob_f_star".
* `--check-columns TEXT`: Columns used to check for duplicates.  [default: obj_id, input_catalog_id, version]
* `--format [feather|parquet]`: File format of the merged data file.  [default: parquet]
* `--help`: Show this message and exit.

---

### `create-db`

Create a database on a PostgreSQL server.

**Usage**:

```console
$ pfs-targetdb-cli create-db [OPTIONS]
```

**Options**:

* `-c, --config TEXT`: Database configuration file in the TOML format.  [required]
* `--help`: Show this message and exit.

---

### `create-schema`

Create tables of the PFS tartedb in a database.

**Usage**:

```console
$ pfs-targetdb-cli create-schema [OPTIONS]
```

**Options**:

* `-c, --config TEXT`: Database configuration file in the TOML format.  [required]
* `--drop-all`: Flag to drop all tables before creating schema.
* `--help`: Show this message and exit.

---

### `diagram`

Generate an ER diagram of a database.

**Usage**:

```console
$ pfs-targetdb-cli diagram [OPTIONS]
```

**Options**:

* `-c, --config TEXT`: Database configuration file in the TOML format.  [required]
* `--generator [schemacrawler|tbls]`: Program to generate ER diagram.  [default: schemacrawler]
* `--output-dir TEXT`: Directory path to save output files.  [default: diagram]
* `--title TEXT`: Title of the ER diagram.  [default: PFS Target Database]
* `--sc-info-level TEXT`: SchemaCrawler info level.  [default: maximum]
* `--sc-level-level TEXT`: SchemaCrawler log level.  [default: SEVERE]
* `--sc-outprefix TEXT`: Output file prefix.  [default: erdiagram_targetdb]
* `--tbls-format TEXT`: tbls format for ER diagrams.  [default: mermaid]
* `--help`: Show this message and exit.

---

### `drop-db`

Drop a database on a PostgreSQL server.

**Usage**:

```console
$ pfs-targetdb-cli drop-db [OPTIONS]
```

**Options**:

* `-c, --config TEXT`: Database configuration file in the TOML format.  [required]
* `--help`: Show this message and exit.

---

### `insert`

Insert rows into a table in the PFS Target Database.

**Usage**:

```console
$ pfs-targetdb-cli insert [OPTIONS] INPUT_FILE
```

**Arguments**:

* `INPUT_FILE`: Input file to be inserted to targetdb (CSV, ECSV, Feather, or Parquet format).  [required]

**Options**:

* `-c, --config TEXT`: Database configuration file in the TOML format.  [required]
* `-t, --table [filter_name|fluxstd|input_catalog|partner|pfs_arm|proposal|proposal_category|sky|target|target_type|user_pointing]`: Table name to insert rows.  [required]
* `--commit`: Commit changes to the database.
* `--fetch`: Fetch data from database a the end.
* `--from-uploader`: Flag to indicate the data is coming from the PFS Target Uploader. Only required for the `target` table.
* `--upload_id TEXT`: Upload ID issued by the PFS Target Uploader. Only required for the `target` table.
* `--proposal_id TEXT`: Proposal ID (e.g., S24B-QT001). Only required for the `target` table.
* `-v, --verbose`: Verbose output.
* `--help`: Show this message and exit.

---

### `insert-targets`

Insert targets using a list of input catalogs and upload IDs.

**Usage**:

```console
$ pfs-targetdb-cli insert-targets [OPTIONS] INPUT_CATALOGS
```

**Arguments**:

* `INPUT_CATALOGS`: Input catalog list to insert (csv).  [required]

**Options**:

* `-c, --config TEXT`: Database configuration file in the TOML format.  [required]
* `--data-dir PATH`: Path to the data directory.  [default: .]
* `--commit`: Commit changes to the database.
* `--fetch`: Fetch data from database a the end.
* `-v, --verbose`: Verbose output.
* `--help`: Show this message and exit.

---

### `install-q3c`

Insert the Q3C extension.

**Usage**:

```console
$ pfs-targetdb-cli install-q3c [OPTIONS]
```

**Options**:

* `-c, --config TEXT`: Database configuration file in the TOML format.  [required]
* `--help`: Show this message and exit.

---

### `mdtable`

Generate a Markdown output of the schema of the PFS Target Database.

**Usage**:

```console
$ pfs-targetdb-cli mdtable [OPTIONS]
```

**Options**:

* `-o, --output-file TEXT`: Output file.
* `--help`: Show this message and exit.

---

### `parse-alloc`

Parse an Excel file containing time allocation information.

**Usage**:

```console
$ pfs-targetdb-cli parse-alloc [OPTIONS] INPUT_FILE
```

**Arguments**:

* `INPUT_FILE`: Path to the Excel file containing time allocation information (e.g., "allocations.xlsx").  [required]

**Options**:

* `--output-dir PATH`: Directory path to save output files.  [default: .]
* `--outfile-prefix TEXT`: Prefix to the output files.
* `--help`: Show this message and exit.

---

### `prep-fluxstd`

Prepare flux standard data for the target database by supplementing additional required fields.

**Usage**:

```console
$ pfs-targetdb-cli prep-fluxstd [OPTIONS] INPUT_DIR OUTPUT_DIR
```

**Arguments**:

* `INPUT_DIR`: Directory path containing input files. Files must be in one of the following formats: parquet, feather, or csv. The input files must be generated in a certain format to be compatible for targetdb.  [required]
* `OUTPUT_DIR`: Directory path to save the output files.  [required]

**Options**:

* `--version TEXT`: Version **string** for the F-star candidate catalog (e.g., '3.3').  [required]
* `--input_catalog_id INTEGER`: Input catalog ID for the flux standard star catalog.
* `--input_catalog_name TEXT`: Input catalog name for the flux standard star catalog.
* `--rename-cols TEXT`: Dictionary to rename columns (e.g., '{"fstar_gaia": "is_fstar_gaia"}').
* `--format [feather|parquet]`: File format of the output data file.  [default: parquet]
* `--help`: Show this message and exit.

---

### `transfer-targets`

Download target lists from the uploader to the local machine.

**Usage**:

```console
$ pfs-targetdb-cli transfer-targets [OPTIONS] INPUT_FILE
```

**Arguments**:

* `INPUT_FILE`: Input catalog list file (csv).  [required]

**Options**:

* `-c, --config TEXT`: Database configuration file in the TOML format.  [required]
* `--local-dir PATH`: Path to the data directory in the local machine  [default: .]
* `--force / --no-force`: Force download.  [default: no-force]
* `--help`: Show this message and exit.

---

### `update`

Update rows in a table in the PFS Target Database.

**Usage**:

```console
$ pfs-targetdb-cli update [OPTIONS] INPUT_FILE
```

**Arguments**:

* `INPUT_FILE`: Input file containing data to update records in the PFS Target Database (CSV, ECSV, or Feather formats).  [required]

**Options**:

* `-c, --config TEXT`: Database configuration file in the TOML format.  [required]
* `-t, --table [filter_name|fluxstd|input_catalog|partner|pfs_arm|proposal|proposal_category|sky|target|target_type|user_pointing]`: Table name to update rows.  [required]
* `--commit`: Commit changes to the database.
* `--fetch`: Fetch data from database a the end.
* `--from-uploader`: Flag to indicate the data is coming from the PFS Target Uploader. Only required for the `target` table.
* `--upload_id TEXT`: Upload ID issued by the PFS Target Uploader. Only required for the `target` table
* `--proposal_id TEXT`: Proposal ID (e.g., S24B-QT001). Only required for the `target` table
* `--verbose`: Verbose output.
* `--help`: Show this message and exit.

---

### `update-catalog-active`

Update active flag in the input_catalog table.

**Usage**:

```console
$ pfs-targetdb-cli update-catalog-active [OPTIONS] INPUT_CATALOG_ID ACTIVE_FLAG
```

**Arguments**:

* `INPUT_CATALOG_ID`: Input catalog ID to be updated.  [required]
* `ACTIVE_FLAG`: Active flag to be set.  [required]

**Options**:

* `-c, --config TEXT`: Database configuration file in the TOML format.  [required]
* `--commit`: Commit changes to the database.
* `-v, --verbose`: Verbose output.
* `--help`: Show this message and exit.

