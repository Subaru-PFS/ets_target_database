# Various Examples

## Operating `targetdb`

### Configuration file

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

### Insert records into a table

```csv title="filter_names.csv"
filter_name,filter_name_description
u_sdss,SDSS u filter
g_sdss,SDSS g filter
r_sdss,SDSS r filter
i_sdss,SDSS i filter
z_sdss,SDSS z filter
```

Filter names in the `filter_names.csv` file can be inserted into the `filter_name` table in the `targetdb` database as follows

```bash
pfs_targetdb_insert -c dbconf.toml -t filter_name filter_names.csv --commit
```

This simple operation can be executed for the `proposal_category`, `proposal`, `input_catalog`, `target_type`, `sky`, and `filter_name` tables.

### Insert targets into the target table

For the target list uploaded via the PFS Target Uploader,
an `upload_id` is issued and `proposal_id` is assigned by the observatory.
One can insert it to the `target` table in the `targetdb` database.

```bash
pfs_targetdb_insert -c dbconf.toml -t target targets.ecsv --commit --from-uploader --upload-id "aabbccddeeffgghh" --proposal-id "S24B-QN001"
```

Note that the `input_catalog` and `proposal` tables must be filled prior to inserting the target list.

### Prepare fluxstd data

```bash
pfs_targetdb_fluxstd_prepdata -c dbconf.toml --version "3.3" --input_catalog_id 3006 --rename-cols '{"fstar_gaia": "is_fstar_gaia"}' input_directory output_directory
```

The above example does the following:
- Read input files in one of csv, ecsv feather, and parquet formats from `input_directory`.
- Add additional required columns, `version` and `input_catalog_id`.
- Rename the column `fstar_gaia` to `is_fstar_gaia`.
- Save the output files to `output_directory`.

Then, one can insert the prepared flux standard data into the `fluxstd` table in the `targetdb` database by using the above command, `pfs_targetdb_insert`.

## Querying `targetdb`

### Cone search

You can search for targets within a certain radius from a give coordinate by using Q3C.

```sql
/* Select 10 objects within 1deg radius from the center of the COSMOS region (RA=150, Dec=2) */
SELECT * FROM target WHERE q3c_radial_query(ra, dec, 150.0, 2.0, 1.0) LIMIT 10;
```

## Test in a Docker container

If you do not have a PostgreSQL server, you can use a Docker container to host a database for testing without affecting the host environment.
To set up a PostgreSQL Docker container, you need to install Docker from [Docker Hub](https://hub.docker.com/search?type=edition&offering=community).

### Build a Docker container

Example `docker-compose.yml` and `Dockerfile` files are provided in the `examples/docker` directory.

```bash
# Build the Docker container with the Q3C extension.
docker-compose build

# Start the Docker container.
docker-compose up -d
```

In the above will create a Docker container with the Q3C extension and start the PostgreSQL server.
The database data will be stored in the `examples/docker/db-data` directory and can be assessed from the host
by using the PostgreSQL client via the port 15432 (see `examples/docker/db-conf.toml`).


After finishing the test, you can stop the Docker container as follows:

```bash
# Stop the Docker container.
docker-compose down
```
