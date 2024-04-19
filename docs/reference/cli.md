# CLI Reference

The command-line interface (CLI) tool `pfs-targetdb-cli` is provided to work with the database.

!!! note Configuration file

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
* `download`: wip: Download data from the uploader to...
* `drop-db`: Drop a database on a PostgreSQL server.
* `insert`: Insert rows into a table in the PFS Target...
* `mdtable`: Generate a Markdown output of the schema...
* `parse-ph2`: wip: Parse a spreadsheet with TAC...
* `prep-fluxstd`: Prepare flux standard data for the target...
* `update`: Update rows in a table in the PFS Target...

---

### `checkdups`

Check for duplicates in data files in a directory.

**Usage**:

```console
$ pfs-targetdb-cli checkdups [OPTIONS] DIRECTORY
```

**Arguments**:

* `DIRECTORY`: Directory path containing input files  [required]

**Options**:

* `--format TEXT`: File format of the merged data file, feather or parquet  [default: parquet]
* `-o, --outdir TEXT`: Path to output directory.  [default: .]
* `--skip-save-merged`: Do not save the merged DataFrame
* `--additional-columns TEXT`: Additional columns to output for the merged file.  (e.g., 'psf_mag_g' 'psf_mag_r'). The following columns are saved by default: "obj_id", "ra", "dec", "input_catalog_id", "version", "input_file", "is_fstar_gaia", "prob_f_star"
* `--check-columns TEXT`: Columns used to check for duplicates. (default: obj_id, input_catalog_id, version)  [default: obj_id, input_catalog_id, version]
* `--help`: Show this message and exit.

---

### `create-db`

Create a database on a PostgreSQL server.

**Usage**:

```console
$ pfs-targetdb-cli create-db [OPTIONS]
```

**Options**:

* `-c, --config TEXT`: Database configuration file (.toml)  [required]
* `--help`: Show this message and exit.

---

### `create-schema`

Create tables of the PFS tartedb in a database.

**Usage**:

```console
$ pfs-targetdb-cli create-schema [OPTIONS]
```

**Options**:

* `-c, --config TEXT`: Database configuration file (.toml)  [required]
* `--drop-all`: Drop all tables before creating schema. (Default: False)
* `--help`: Show this message and exit.

---

### `diagram`

Generate an ER diagram of a database.

**Usage**:

```console
$ pfs-targetdb-cli diagram [OPTIONS]
```

**Options**:

* `-c, --config TEXT`: Database configuration file (.toml)  [required]
* `--generator [schemacrawler|tbls]`: Program to generate ER diagram (schemacrawler or tbls)  [default: schemacrawler]
* `--output-dir TEXT`: Output directory  [default: diagram]
* `--title TEXT`: Title of the ER diagram  [default: PFS Target Database]
* `--sc-info-level TEXT`: SchemaCrawler info level  [default: maximum]
* `--sc-level-level TEXT`: SchemaCrawler log level  [default: SEVERE]
* `--sc-outprefix TEXT`: Output file prefix  [default: erdiagram_targetdb]
* `--tbls-format TEXT`: tbls format  [default: mermaid]
* `--help`: Show this message and exit.

---

### `download`

wip: Download data from the uploader to the local machine.

**Usage**:

```console
$ pfs-targetdb-cli download [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

---

### `drop-db`

Drop a database on a PostgreSQL server.

**Usage**:

```console
$ pfs-targetdb-cli drop-db [OPTIONS]
```

**Options**:

* `-c, --config TEXT`: Database configuration file (.toml)  [required]
* `--help`: Show this message and exit.

---

### `insert`

Insert rows into a table in the PFS Target Database.

**Usage**:

```console
$ pfs-targetdb-cli insert [OPTIONS] INPUT_FILE
```

**Arguments**:

* `INPUT_FILE`: Input file to be inserted to targetdb (CSV, ECSV, Feather, or Parquet format)  [required]

**Options**:

* `-c, --config TEXT`: Database configuration file (.toml)  [required]
* `-t, --table TEXT`: Table name to insert data  [required]
* `--commit`: Commit changes to the database
* `--fetch`: Fetch data from database a the end
* `--from_uploader`: Flag to indicate the data is coming from the PFS Target Uploader. Only required for the target table
* `--upload_id TEXT`: Upload ID issued by the PFS Target Uploader. Only required for the target table
* `--proposal_id TEXT`: Proposal ID (e.g., S24B-QT001). Only required for the target table
* `-v, --verbose`: Verbose output
* `--help`: Show this message and exit.

---

### `mdtable`

Generate a Markdown output of the schema of the PFS Target Database.

**Usage**:

```console
$ pfs-targetdb-cli mdtable [OPTIONS]
```

**Options**:

* `-o, --output-file TEXT`: Output file
* `--help`: Show this message and exit.

---

### `parse-ph2`

wip: Parse a spreadsheet with TAC allocations.

**Usage**:

```console
$ pfs-targetdb-cli parse-ph2 [OPTIONS]
```

**Options**:

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

* `--version TEXT`: Version **string** for the F-star candidate catalog (e.g., '3.3')  [required]
* `--input_catalog_id INTEGER`: Input catalog ID for the F-star candidate catalog
* `--input_catalog_name TEXT`: Input catalog name for the F-star candidate catalog
* `--rename-cols TEXT`: Dictionary to rename columns (e.g., '{"fstar_gaia": "is_fstar_gaia"}')
* `--format TEXT`: File format of the output data file, feather or parquet  [default: parquet]
* `--help`: Show this message and exit.

---

### `update`

Update rows in a table in the PFS Target Database.

**Usage**:

```console
$ pfs-targetdb-cli update [OPTIONS] INPUT_FILE
```

**Arguments**:

* `INPUT_FILE`: Input file containing data to update records in the PFS Target Database (CSV, ECSV, or Feather formats) (required)  [required]

**Options**:

* `-c, --config TEXT`: Database configuration file (.toml)  [required]
* `-t, --table TEXT`: Table name to insert data  [required]
* `--commit`: Commit changes to the database
* `--fetch`: Fetch data from database a the end
* `--from_uploader`: Flag to indicate the data is coming from the PFS Target Uploader. Only required for the target table
* `--upload_id TEXT`: Upload ID issued by the PFS Target Uploader. Only required for the target table
* `--proposal_id TEXT`: Proposal ID (e.g., S24B-QT001). Only required for the target table
* `--verbose`: Verbose output
* `--help`: Show this message and exit.
