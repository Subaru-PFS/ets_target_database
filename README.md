# PFS Target Database



<!-- ABOUT THE PROJECT -->
## About The Project

PFS Target Database is an implementation of `targetDB` for Prime Focus Spectrograph at Subaru Telescope.



### Built With (or I'm developing the package with)

The following packages and their dependencies are required to use the main functionality of the package.

* [Python 3.9.7](https://www.python.org/)
* [SQLAlchemy 1.4.25](https://www.sqlalchemy.org/)
* [NumPy 1.21.2](https://numpy.org/)
* [pandas 1.3.3](https://pandas.pydata.org/)

Additionally, the following packages and their dependencies are required to use additional functionality of the package and run some example scripts.

* [SQLAlchemy-Utils 0.37.8](https://sqlalchemy-utils.readthedocs.io/en/latest/)
* [tabulate 0.8.9](https://pypi.org/project/tabulate/)
* [SchemaCrawler 16.15.4](https://www.schemacrawler.com/)
* [md-to-pdf 5.0.0](https://github.com/simonhaenisch/md-to-pdf)
* [Docker 20.10.8](https://www.docker.com/)

Some other useful tools.
* [DBeaver](https://dbeaver.io/)


<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

If you do not have a PostgreSQL server, you can use Docker container to host a database for testing without affecting the host environment. To setup a PostgreSQL Docker container, you need to install Docker from [Docker Hub](https://hub.docker.com/search?type=edition&offering=community).

### Installation

1. Clone the repo and go to the cloned directory.
   ```sh
   git clone https://github.com/monodera/pfs_target_database.git
   cd pfs_target_database
   ```

2. Build the package
   ```sh
   python ./setup.py build
   ```

3. Link the package
    ```sh
    python ./setup.py develop
    ```
    By doing this, Python imports pacakges directly from this folder. It's good for development. If you want to install the package under the python library folder, you can execute `python ./setup.py install`.  This command will install some executables under the directory where your Python executable is located.



<!-- USAGE EXAMPLES -->
## Usage

Here, we describe how to test the package.

### Setup a PostgreSQL server (optional)

If a postgres database server to create `targetDB` is not running, you can easily make one as a Docker container.

```sh
cd example/docker/postgres
mkdir db-data  # database will be stored in this directory
docker-compose -up -d
```
In this example, the local port 15432 is mapped to the port 5432 inside the container.

<!-- Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_ -->


### Create a test database

Example database (called `targetdb` ) can be created with a command-line script `pfs_targetdb_create_database`.
```sh
pfs_targetdb_create_database "postgresql://admin:admin@localhost:15432/targetdb"
```

### Create tables in the test database
Then, you can create tables in `targetdb`.
```sh
pfs_targetdb_create_schema "postgresql://admin:admin@localhost:15432/targetdb"
```
`pfs_targetdb_create_schema` can accept an option `--drop_all`.  With `--drop_all`, all tables in the database schema will be dropped before creating them.

### Generate an ER diagram of the database
Using SchemaCrawler, you can make an Entity Relationship diagram (ERD) of the `targetdb`.
```sh
./PATH_TO_SCHEMACRAWLER/_schemacrawler/schemacrawler.sh \
    --server=postgresql \
    --host=localhost \
    --port=15432 \
    --database=targetdb \
    --schemas=public \
    --user=admin \
    --password=admin \
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

### Generate a markdown table of all tables in the database

The ER diagram generated above does not include detailed comments for each column. It is useful to make a table in the markdown format.

```sh
pfs_targetdb_generate_mdtable --schema_md=../output/schema_targetdb_tables.md --basedir=../output
````

You can convert it to a PDF file.

```sh
md-to-pdf schema_targetdb_tables.pdf
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

Distributed under the MIT License. See `LICENSE` for more information.



<!-- CONTACT -->
## Contact

Masato Onodera - monodera@naoj.org

Project Link: [https://github.com/monodera/pfs_target_database](https://github.com/monodera/pfs_target_database)



<!-- ACKNOWLEDGEMENTS -->
<!-- ## Acknowledgements

* []()
* []()
* []() -->





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
