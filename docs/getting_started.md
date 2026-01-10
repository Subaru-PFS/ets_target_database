# Getting Started

This guide will help you get started with the PFS Target Database.

## Prerequisites

### PostgreSQL database

You need a [PostgreSQL](https://www.postgresql.org/) server to host the database.
If you do not have a PostgreSQL server, you can use a Docker container to host a database for testing without affecting the host environment.
To set up a PostgreSQL Docker container, you need to install Docker from [Docker Hub](https://hub.docker.com/search?type=edition&offering=community). See the [examples](examples/index.md) for more details.

#### Q3C extension

The Q3C extension is required for the database. You can install it by the following instruction in the [q3c repository](https://github.com/segasai/q3c)

### Python environment

Python and the following packages as well as their dependencies will be required for `targetdb`.
The dependencies are automatically installed when you install the `targetdb` package via `pip`.
Package versions shown here are those used for the development (as of January 2026).
Newer (and somewhat older) versions should also work.

| Package                                                                | Version |
| ---------------------------------------------------------------------- | ------: |
| [Python](https://www.python.org/)                                      | 3.12.12 |
| [alembic](https://alembic.sqlalchemy.org/en/latest/)                   |  1.18.0 |
| [Astropy](https://www.astropy.org/)                                    |    7.20 |
| [loguru](https://loguru.readthedocs.io/)                               |   0.7.3 |
| [NumPy](https://numpy.org)                                             |   2.4.0 |
| [openpyxl](https://openpyxl.readthedocs.io/en/stable/)                 |   3.1.5 |
| [pandas](https://pandas.pydata.org/)                                   |   2.3.3 |
| [psycopg2-binary](https://www.psycopg.org/)                            |  2.9.11 |
| [pyarrow](https://arrow.apache.org/docs/python/)                       |  22.0.0 |
| [requests](https://requests.readthedocs.io/en/latest/)                 |  2.32.5 |
| [SQLAlchemy](https://www.sqlalchemy.org/)                              |  2.0.45 |
| [SQLAlchemy-Utils](https://sqlalchemy-utils.readthedocs.io/en/latest/) |  0.42.1 |
| [tabulate](https://pypi.org/project/tabulate/)                         |   0.9.0 |
| [Typer](https://typer.tiangolo.com/)                                   |  0.21.1 |

For building the documentation, the following packages are required.

| Package                                                         | Version |
| --------------------------------------------------------------- | ------: |
| [MkDocs](https://www.mkdocs.org/)                               |   1.6.1 |
| [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) |   9.7.1 |

Additionally, the following tools may be useful for testing and development.

- [SchemaCrawler](https://www.schemacrawler.com/)
- [md-to-pdf](https://github.com/simonhaenisch/md-to-pdf)
- [Docker](https://www.docker.com/)
- [DBeaver](https://dbeaver.io/)
- [tbls](https://github.com/k1LoW/tbls)

## Installation

Installation of the `targetdb` package can be done by the following command:

```bash
# clone the GitHub repository
git clone https://github.com/Subaru-PFS/ets_target_database.git

# move to the directory
cd ets_target_database

# Install with uv
uv sync

# (optional) create a virtual environment and activate it
# python3 -m venv .venv
# source .venv/bin/activate
# python3 -m pip install -e .
```

## Quick Start

### Create the `targetdb`

The `dbconf.toml` is used as a configuration file for the database connection.

```toml title="dbconf.toml"
[targetdb.db]
host = "localhost"  # database host
port = 5432  # database port
dbname = "targetdb"  # database name
user = "admin"  # database user
password = "admin"  # database password
dialect = "postgresql"  # database dialect


[schemacrawler]
SCHEMACRAWLERDIR = "<path to schemacrawler directory>"  # "_schemacrawler/bin/schemacrawler.sh" under the path will be used
```

The following commands are to create the `targetdb` database, install the Q3C extension,
create tables, and generate an entity-relationship diagram of the database.

```bash
# create a database
pfs-targetdb-cli create-db -c dbconf.toml

# install the Q3C extension
pfs-targetdb-cli install-q3c -c dbconf.toml

# create tables in the database
pfs-targetdb-cli create-schema -c dbconf.toml

# when installed via uv, the command can be run as
# uv run pfs-targetdb-cli create-db -c dbconf.toml
# uv run pfs-targetdb-cli install-q3c -c dbconf.toml
# uv run pfs-targetdb-cli create-schema -c dbconf.toml
```

### Generate an ER diagram

```
# draw the ER diagram
pfs-targetdb-cli diagram -c dbconf.toml
```

An ER diagram will be generated as `erdiagram_targetdb-YYYYMMDDHHmmss.pdf` in the current directory. Note that SchemaCrawler must be installed and the directory must be set in the `dbconf.toml` file.

### Python example

To connect to the database with Python, you can use the following code snippet.

```python
from targetdb import TargetDB

# create a database connection
db = TargetDB(host="localhost", port= 5432, dbname="testdb", user="admin", password="admin")
db.connect()

# fetch all data from the input_catalog table as pandas.DataFrame
df = db.fetch_all("input_catalog")

# print the first 5 rows (should return an empty dataframe)
print(df.head())
# Empty DataFrame
# Columns: [input_catalog_id, input_catalog_name, input_catalog_description, upload_id, created_at, updated_at]
# Index: []

# close the connection
db.close()
```

## Build the Documentation

The documentation can be built by the following command:

```bash
# Install the required packages for building the documentation
python3 -m pip install -e ".[doc]"

# or via uv
# uv sync --extra doc

# Build the documentation with MkDocs
mkdocs build

# or via uv
# uv run mkdocs build
```

The documentation will be generated in the `site` directory.
