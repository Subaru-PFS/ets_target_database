# PFS Target Database


<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Thanks again! Now go create something AMAZING! :D
***
***
***
*** To avoid retyping too much info. Do a search and replace for the following:
*** github_username, repo_name, twitter_handle, email, project_title, project_description
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
<!-- [![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url] -->



<!-- PROJECT LOGO -->
<!-- <br />
<p align="center">
  <a href="https://github.com/github_username/repo_name">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">project_title</h3>

  <p align="center">
    project_description
    <br />
    <a href="https://github.com/github_username/repo_name"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/github_username/repo_name">View Demo</a>
    ·
    <a href="https://github.com/github_username/repo_name/issues">Report Bug</a>
    ·
    <a href="https://github.com/github_username/repo_name/issues">Request Feature</a>
  </p>
</p> -->



<!-- TABLE OF CONTENTS -->
<!-- <details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details> -->


<!-- ABOUT THE PROJECT -->
## About The Project

PFS Target Database (targetdb) is a Python package to manage and interact with a [PostgreSQL](https://www.postgresql.org/) database for Prime Focus Spectrograph at [Subaru Telescope](https://subarutelescope.org/). The `targetdb` is designed to store information from the observatory and observers on proposals and science targets. It also stores information on sky positions and flux standard stars required for PFS observation.



## Prerequisites

### PostgreSQL database

You need a PostgreSQL server to host the database. If you do not have a PostgreSQL server, you can use a Docker container to host a database for testing without affecting the host environment. To set up a PostgreSQL Docker container, you need to install Docker from [Docker Hub](https://hub.docker.com/search?type=edition&offering=community).

The Q3C extension is required for the database. You can install it by the following instruction in the [q3c repository](https://github.com/segasai/q3c)


### Python environment
Python and the following packages as well as their dependencies will be used by installing `targetdb`.
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


<!-- GETTING STARTED -->
## Getting Started

### Installation

```sh
# Clone the repository and go to the cloned directory.
git clone https://github.com/Subaru-PFS/ets_target_database.git
cd ets_target_database

# (optional) Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the package
python3 -m pip install -e .
```

By doing this, Python imports `targetdb` package directly from the cloned directory, which is convenient for development. If you want to install the package under the Python library directory, you can execute `python3 -m pip install .`.

The installation process will install some command-line tools under the directory where your Python executable is located.

<!-- USAGE EXAMPLES -->
## Usage

Here, we describe how to test the package.

### Setup a PostgreSQL server (optional)

If a postgres database server to create `targetdb` is not running, you can easily make one as a Docker container.

```sh
cd example/docker/postgres
mkdir db-data  # database will be stored in this directory
docker-compose -up -d
```
In this example, the local port 15432 is mapped to the port 5432 inside the container.

<!-- Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_ -->

### Create targetDB

Following procedures in this section is summarized in `examples/scripts/make_database.bash`. You can create a test database and schema with associated outputs at once by the following commands.

```sh
cd examples/scripts
bash ./make_database.bash
```

Note that the script must be execute as a Bash script.

We recommend to check the content of `targetdb_config.ini` (ask M. Onodera) and change the configuration if necessary (e.g., `SCHEMACRAWLERDIR`).

#### Create a test database

Example database (called `targetdb` ) can be created with a command-line script `pfs_targetdb_create_database`.
```sh
pfs_targetdb_create_database "postgresql://<user>:<password>@<hostname>:<port>/targetdb"
```

#### Create tables in the database

Then, you can create tables in `targetdb`.
```sh
pfs_targetdb_create_schema "postgresql://<user>:<password>@<hostname>:<port>/targetdb"
```
`pfs_targetdb_create_schema` can accept an option `--drop_all`.  With `--drop_all`, all tables in the database schema will be dropped before creating them.

#### Generate an ER diagram of the database

Using SchemaCrawler, you can make an Entity Relationship diagram (ERD) of the `targetdb`.
```sh
./PATH_TO_SCHEMACRAWLER/_schemacrawler/schemacrawler.sh \
    --server=postgresql \
    --host=<hostname> \
    --port=<port> \
    --database=targetdb \
    --schemas=public \
    --user=<user> \
    --password=<password> \
    --info-level=standard \
    --command=schema \
    --log-level=INFO \
    --portable-names \
    --title='PFS Target Database (Example)' \
    --output-format=pdf \
    --output-file=../output/schema_targetdb.pdf \
    --no-remarks
```
The output ERD is saved in the `examples/output` directory.

#### Generate a markdown table of all tables in the database

The ER diagram generated above does not include detailed comments for each column. It is useful to make a table in the markdown format.

```sh
pfs_targetdb_generate_mdtable --schema_md=../output/schema_targetdb_tables.md --basedir=../output
````

You can convert it to a PDF file.

```sh
md-to-pdf schema_targetdb_tables.pdf
```

### Insert test data into tables

In the `examples/scripts` directory, there is a script named `test_targetdb_api.py` and currently it insert sample data into `proposal_category`, `proposal`, `input_catalog`, and `target_type` tables.

The sample data are stored in the `examples/data` direcotry.

```sh
python ./test_targetdb_api.py -h

usage: test_targetdb_api.py [-h] [--reset] [--skip_proposal_category] [--skip_proposal] [--skip_input_catalog] [--skip_target_type] [--skip_target] [--skip_unique_object] [--target TARGET] conf

Test targetDB API

positional arguments:
  conf                  Config file for targetDB (default: './targetdb_config.ini')

optional arguments:
  -h, --help            show this help message and exit
  --reset               Reset all tables in targetdb before playing with it. (Default: False)
  --skip_proposal_category
                        Skip inserting test data into the proposal_category table (default: False)
  --skip_proposal       Skip inserting test data into the proposal table (default: False)
  --skip_input_catalog  Skip inserting test data into the input_catalog table (default: False)
  --skip_target_type    Skip inserting test data into the target_type table (default: False)
  --skip_target         Skip inserting test data into the target table (default: False)
  --skip_unique_object  Skip inserting test data into the unique_object table (default: False)
  --target TARGET       Sample csv file for targets (default: ../data/target_s21b-en01.csv)
```







<!-- ROADMAP -->
<!-- ## Roadmap

See the [open issues](https://github.com/monodera/pfs_target_database/issues) for a list of proposed features (and known issues). -->



<!-- CONTRIBUTING -->
<!-- ## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request -->



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.



<!-- CONTACT -->
## Contact

Masato Onodera - monodera@naoj.org

Project Link: [https://github.com/monodera/pfs_target_database](https://github.com/monodera/pfs_target_database)



<!-- ACKNOWLEDGEMENTS -->
<!-- ## Acknowledgements -->
## References

* [PFS Operational Database](https://github.com/Subaru-PFS/spt_operational_database)
* [PFS Datamodel](https://github.com/Subaru-PFS/datamodel)
* [Best-README-Template](https://github.com/othneildrew/Best-README-Template)
* [A Sample Python Project](https://github.com/pypa/sampleproject)






<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
<!-- [contributors-shield]: https://img.shields.io/github/contributors/monodera/repo.svg?style=for-the-badge
[contributors-url]: https://github.com/monodera/pfs_target_database/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/monodera/repo.svg?style=for-the-badge
[forks-url]: https://github.com/monodera/pfs_target_database/network/members
[stars-shield]: https://img.shields.io/github/stars/monodera/repo.svg?style=for-the-badge
[stars-url]: https://github.com/monodera/pfs_target_database/stargazers
[issues-shield]: https://img.shields.io/github/issues/monodera/repo.svg?style=for-the-badge
[issues-url]: https://github.com/monodera/pfs_target_database/issues
[license-shield]: https://img.shields.io/github/license/monodera/repo.svg?style=for-the-badge
[license-url]: https://github.com/monodera/pfs_target_database/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/monodera -->
