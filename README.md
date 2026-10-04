# PFS Target Database

## About The Project

PFS Target Database (targetdb) is a Python package to manage and interact with a [PostgreSQL](https://www.postgresql.org/) database for Prime Focus Spectrograph at [Subaru Telescope](https://subarutelescope.org/). The `targetdb` is designed to store information from the observatory and observers on proposals and science targets. It also stores information on sky positions and flux standard stars required for PFS observation.

Please see [the documentation](https://subaru-pfs.github.io/ets_target_database/) for more details.

## Prerequisites

### PostgreSQL database

You need a PostgreSQL server to host the database. If you do not have a PostgreSQL server, you can use a Docker container to host a database for testing without affecting the host environment. To set up a PostgreSQL Docker container, you need to install Docker from [Docker Hub](https://hub.docker.com/search?type=edition&offering=community).

#### Q3C extension

The Q3C extension is required for the database. You can install it by the following instruction in the [q3c repository](https://github.com/segasai/q3c)

### Python environment

Python and the following packages as well as their dependencies will be used by installing `targetdb`.
Package versions shown here are those used for the development (as of May 2026).
Newer (and somewhat older) versions should also work.

| Package                                                                |     Version |
|------------------------------------------------------------------------|------------:|
| [Python](https://www.python.org/)                                      |      3.12.x |
| [SQLAlchemy](https://www.sqlalchemy.org/)                              |       2.0.x |
| [pandas](https://pandas.pydata.org/)                                   |       2.3.3 |
| [NumPy](https://numpy.org)                                             |       2.4.0 |
| [Astropy](https://www.astropy.org/)                                    |       7.2.0 |
| [loguru](https://loguru.readthedocs.io/)                               |       0.7.3 |
| [pfs-utils](https://github.com/Subaru-PFS/pfs_utils)                   | 7.2026.3100 |
| [psycopg](https://www.psycopg.org/)                                    |       3.3.4 |
| [SQLAlchemy-Utils](https://sqlalchemy-utils.readthedocs.io/en/latest/) |      0.42.1 |
| [tabulate](https://pypi.org/project/tabulate/)                         |       0.9.0 |
| [alembic](https://alembic.sqlalchemy.org/en/latest/)                   |      1.18.0 |
| [pyarrow](https://arrow.apache.org/docs/python/)                       |      22.0.0 |
| [Typer](https://typer.tiangolo.com/)                                   |      0.21.1 |
| [openpyxl](https://openpyxl.readthedocs.io/en/stable/)                 |       3.1.5 |

`targetdb.TargetDB` subclasses `pfs.utils.database.db.DB`, so `pfs-utils` is installed
straight from GitHub and a `.git` directory plus network access are needed at install time.

For building the documentation, the following packages are required.

| Package                                                         | Version |
|-----------------------------------------------------------------|--------:|
| [MkDocs](https://www.mkdocs.org/)                               |   1.6.1 |
| [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) |  9.6.11 |

Additionally, the following tools may be useful for testing and development.

- [SchemaCrawler](https://www.schemacrawler.com/)
- [md-to-pdf](https://github.com/simonhaenisch/md-to-pdf)
- [Docker](https://www.docker.com/)
- [DBeaver](https://dbeaver.io/)
- [tbls](https://github.com/k1LoW/tbls)


## Getting Started

### Installation

```console
# Clone the repository and go to the cloned directory.
git clone https://github.com/Subaru-PFS/ets_target_database.git
cd ets_target_database

# (optional) Create a virtual environment
# python3 -m venv .venv
# source .venv/bin/activate

# Install the package in the development mode
python3 -m pip install -e .
```

By doing this, Python imports `targetdb` package directly from the cloned directory, which is convenient for development.
If you want to install the package under the Python library directory, you can execute `python3 -m pip install .`.

The installation process will install some command-line tools under the directory where your Python executable is located.

### Development setup

If you are going to contribute, install the development dependencies and enable the pre-commit hooks:

```console
python3 -m pip install -e ".[dev]"
pre-commit install
```

The hooks run `ruff` and `black` on the files you stage, plus whitespace and syntax checks. CI runs `ruff` and `black` over all of `src` and `tests`; run `pre-commit run --all-files` to check the whole tree the way CI does.


## Usage Examples

Here, we show a few examples of how to use the `targetdb` package.

### Setup a PostgreSQL server (optional)

If a postgres database server to create `targetdb` is not running, you can easily make one as a Docker container.

```console
cd example/docker/
docker compose build
docker compose -up -d
```

In this example, the local port 15432 is mapped to the port 5432 inside the container.
The database data will be stored in the `examples/docker/db-data` directory and can be accessed from the host by using the PostgreSQL client via the port 15432 (see `examples/docker/db-conf.toml`).

### Create targetDB

Following commands create a database and tables as configured in the `dbconf.toml` file.

```console
# create a database
pfs-targetdb-cli create-db -c dbconf.toml

# install the Q3C extension
pfs-targetdb-cli install-q3c -c dbconf.toml

# create tables in the database
pfs-targetdb-cli create_schema -c dbconf.toml
```


### Generate an ER diagram of the database

Using SchemaCrawler, you can make an Entity Relationship diagram (ERD) of the `targetdb`.

```console
# draw the ER diagram
pfs-targetdb-cli diagram -c dbconf.toml
```

### Insert test data into tables

In the `examples/data` directory, example data files are located. You can insert them into the database by the following commands.

```bash
pfs-targetdb-cli insert -c dbconf.toml -t proposal_category examples/data/proposal_category.csv --commit
pfs-targetdb-cli insert -c dbconf.toml -t proposal examples/data/proposals.csv --commit
pfs-targetdb-cli insert -c dbconf.toml -t input_catalog examples/data/input_catalogs.csv --commit
pfs-targetdb-cli insert -c dbconf.toml -t target_type examples/data/target_types.csv --commit
pfs-targetdb-cli insert -c dbconf.toml -t filter_name examples/data/filter_names.csv --commit
pfs-targetdb-cli insert -c dbconf.toml -t partner examples/data/partner.csv --commit
pfs-targetdb-cli insert -c dbconf.toml -t pfs_arm examples/data/pfs_arm.csv --commit
```

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

## Contact

Masato Onodera - [GitHub](https://github.com/monodera/)

Project Link: [https://github.com/Subaru-PFS/ets_target_database](https://github.com/Subaru-PFS/ets_target_database)

## References

- [PFS Operational Database](https://github.com/Subaru-PFS/spt_operational_database)
- [PFS Datamodel](https://github.com/Subaru-PFS/datamodel)
- [Best-README-Template](https://github.com/othneildrew/Best-README-Template)
- [A Sample Python Project](https://github.com/pypa/sampleproject)
