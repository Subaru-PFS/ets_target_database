# Getting Started

This guide will help you get started with the PFS Target Database.

## Prerequisites

### PostgreSQL database

You need a [PostgreSQL](https://www.postgresql.org/) server to host the database.
If you do not have a PostgreSQL server, you can use a Docker container to host a database for testing without affecting the host environment.
To set up a PostgreSQL Docker container, you need to install Docker from [Docker Hub](https://hub.docker.com/search?type=edition&offering=community). See the [examples](examples.md) for more details.

The Q3C extension is required for the database. You can install it by the following instruction in the [q3c repository](https://github.com/segasai/q3c)

### Python environment

Python and the following packages as well as their dependencies will be required for `targetdb`.
The dependencies are automatically installed when you install the `targetdb` package via `pip`.
Package versions shown here are those used for the development (as of April 2024).
Newer (and somewhat older) versions should also work.

| Package                                                                | Version |
|------------------------------------------------------------------------|--------:|
| [Python](https://www.python.org/)                                      |  3.9.18 |
| [SQLAlchemy](https://www.sqlalchemy.org/)                              |  2.0.29 |
| [pandas](https://pandas.pydata.org/)                                   |   2.2.2 |
| [NumPy](https://numpy.org)                                             |  1.26.4 |
| [Astropy](https://www.astropy.org/)                                    |   6.0.1 |
| [loguru](https://loguru.readthedocs.io/)                               |   0.7.2 |
| [SQLAlchemy-Utils](https://sqlalchemy-utils.readthedocs.io/en/latest/) |  0.41.2 |
| [tabulate](https://pypi.org/project/tabulate/)                         |   0.9.0 |
| [alembic](https://alembic.sqlalchemy.org/en/latest/)                   |  1.13.1 |
| [pyarrow](https://arrow.apache.org/docs/python/)                       |  15.0.2 |

If you are using Python 3.10 or earlier, you may need to install [tomli](https://github.com/hukkin/tomli) package.

Additionally, the following tools may be useful for testing and development.

- [SchemaCrawler](https://www.schemacrawler.com/)
- [md-to-pdf](https://github.com/simonhaenisch/md-to-pdf)
- [Docker](https://www.docker.com/)
- [DBeaver](https://dbeaver.io/)

## Installation

Installation of the `targetdb` package can be done by the following command:

```bash
# clone the GitHub repository
git clone https://github.com/Subaru-PFS/ets_target_database.git

# move to the directory
cd ets_target_database

# (optional but recommended) create a virtual environment and activate it
# python3 -m venv .venv
# source .venv/bin/activate

# install the package
python3 -m pip install .

# You can also install the package in the editable mode
# python3 -m pip install -e .

# refresh the shell for command-line tools
hash -r
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
SCHEMACRAWLERDIR = "<path to schemacrawler>"  # "_schemacrawler/bin/schemacrawler.sh" under the path will be used
```

The following commands are to create the `targetdb` database, install the Q3C extension,
create tables, and generate an entity-relationship diagram of the database.

```bash
# create a database
pfs_targetdb_create_database -c dbconf.toml

# install the Q3C extension
psql -h localhost -U admin -d targetdb -c "CREATE EXTENSION q3c;"
Password for user admin: (enter the password)

# create tables in the database
pfs_targetdb_create_schema -c dbconf.toml
```

### Generate an ER diagram

```
# draw the ER diagram
pfs_targetdb_draw_diagram dbconf.toml
```

An ER diagram will be generated as `erdiagram_targetdb-YYYYMMDDHHmmss.pdf` in the current directory.

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