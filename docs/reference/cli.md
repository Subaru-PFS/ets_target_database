# CLI Reference

The command-line interface (CLI) tool `pfs-targetdb-cli` is provided to work with the database.

## Configuration file

The command-line tools introduced below require a configuration file in TOML format to connect the database.
The configuration file should look like teh following and provided as an argument to the command-line tools with `--config` or `-c` option.:

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

!!! Note
    The `schemacrawler` section is required only if you want to draw an ER diagram of the database schema with SchemaCrawler.

## **`pfs-targetdb-cli`**

**Usage:**

```text
pfs-targetdb-cli [OPTIONS] COMMAND [ARGS]...
```

**Options:**

- `--install-completion`: Install completion for the current shell.
- `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
- `--help`, `-h`: Show this message and exit.

---

**Commands:**

### **`checkdups`**

Check for duplicates in data files in a directory.

**Usage:**

```text
pfs-targetdb-cli checkdups [OPTIONS] DIRECTORY
```

**Arguments:**

- `directory`: Directory path containing input files (required)

**Options:**

- `--format`: File format of the merged data file, feather or parquet (default: parquet)
- `--outdir`, `-o`: Path to output directory (default: .)
- `--skip-save-merged`: Do not save the merged DataFrame
- `--additional-columns`: Additional columns to output for the merged file. For example, 'psf_mag_g' 'psf_mag_r'. The following columns are saved by default: "obj_id", "ra", "dec", "input_catalog_id", "version", "input_file", "is_fstar_gaia", "prob_f_star"
- `--check-columns`: Columns used to check for duplicates. (default: obj_id, input_catalog_id, version)
- `--help`, `-h`: Show this message and exit.

---

### **`create-db`**

Create a database on a PostgreSQL server.

**Usage:**

```text
pfs-targetdb-cli create-db [OPTIONS]
```

**Options:**

- `--config`, `-c`: Database configuration file (.toml) (required)
- `--help`, `-h`: Show this message and exit.

---

### `create-schema`

Create tables of the PFS tartedb in a database.

**Usage:**

```text
pfs-targetdb-cli create-schema [OPTIONS]
```

**Options:**

- `--config`, `-c`: Database configuration file (.toml) (required)
- `--drop-all`: Drop all tables before creating schema. (Default: False)
- `--help`, `-h`: Show this message and exit.

---

### `diagram`
Generate an ER diagram of a database. You can choose between SchemaCrawler and tbls to generate the diagram.
The chosen program must be installed.

**Usage:**

```text
pfs-targetdb-cli diagram [OPTIONS]
```

**Options:**

- `--config`, `-c`: Database configuration file (.toml) (required)
- `--generator`: Program to generate ER diagram (schemacrawler or tbls) (default: schemacrawler)
- `--output-dir`: Output directory (default: diagram)
- `--title`: Title of the ER diagram (default: PFS Target Database)
- `--sc-info-level`: SchemaCrawler info level (default: maximum)
- `--sc-level-level`: SchemaCrawler log level (default: SEVERE)
- `--sc-outprefix`: Output file prefix (default: erdiagram_targetdb)
- `--tbls-format`: tbls format (default: mermaid)
- `--help`, `-h`: Show this message and exit.

---

### `drop-db`

Drop a database on a PostgreSQL server.

**Usage:**

```text
pfs-targetdb-cli drop-db [OPTIONS]
```

**Options:**

- `--config`, `-c`: Database configuration file (.toml) (required)
- `--help`, `-h`: Show this message and exit.

---

### `insert`

Insert rows into a table in the PFS Target Database.

**Usage:**

```text
pfs-targetdb-cli insert [OPTIONS] INPUT_FILE
```

**Arguments:**

- `input_file`: Input file to be inserted to targetDB (CSV, ECSV, or Feather formats) (required)

**Options:**

- `--config`, `-c`: Database configuration file (.toml) (required)
- `--table`, `-t`: Table name to insert data (required)
- `--commit`: Commit changes to the database
- `--fetch`: Fetch data from database at the end
- `--from_uploader`: Flag to indicate the data is coming from the PFS Target Uploader. Only required for the target table
- `--upload_id`: Upload ID issued by the PFS Target Uploader. Only required for the target table
- `--proposal_id`: Proposal ID (e.g., S24B-QT001). Only required for the target table
- `--verbose`, `-v`: Verbose output
- `--help`, `-h`: Show this message and exit.

---

### `mdtable`

Generate a Markdown output of the schema of the PFS Target Database.

**Usage:**

```text
pfs-targetdb-cli mdtable [OPTIONS]
```

**Options:**

- `--output-file`, `-o`: Output file (default: None)
- `--help`, `-h`: Show this message and exit.

---

### `prep-fluxstd`

Prepare flux standard data for the target database by supplementing additional required fields.

**Usage:**

```text
pfs-targetdb-cli prep-fluxstd [OPTIONS] INPUT_DIR OUTPUT_DIR
```

**Arguments:**

- `input_dir`: Directory path containing input files. Files must be in one of the following formats: parquet, feather, or csv. The input files must be generated in a certain format to be compatible for targetdb (required)
- `output_dir`: Directory path to save the output files (required)

**Options:**

- `--version`: Version **string** for the F-star candidate catalog (e.g., '3.3') (required)
- `--input_catalog_id`: Input catalog ID for the F-star candidate catalog (required)
- `--rename-cols`: Dictionary to rename columns (e.g., '{"fstar_gaia": "is_fstar_gaia"}') (default: None)
- `--format`: File format of the merged data file, feather or parquet (default: parquet)
- `--help`, `-h`: Show this message and exit.

---

### `update`

Update rows in a table in the PFS Target Database.

**Usage:**

```text
pfs-targetdb-cli update [OPTIONS] INPUT_FILE
```

**Arguments:**

- `input_file`: Input file containing data to update rows in the PFS Target Database (CSV, ECSV, or Feather formats) (required)

**Options:**

- `--config`, `-c`: Database configuration file (.toml) (required)
- `--table`, `-t`: Table name to insert data (required)
- `--commit`: Commit changes to the database
- `--fetch`: Fetch data from database at the end
- `--from_uploader`: Flag to indicate the data is coming from the PFS Target Uploader. Only required for the target table
- `--upload_id`: Upload ID issued by the PFS Target Uploader. Only required for the target table
- `--proposal_id`: Proposal ID (e.g., S24B-QT001). Only required for the target table
- `--verbose`: Verbose output
- `--help`, `-h`: Show this message and exit.
