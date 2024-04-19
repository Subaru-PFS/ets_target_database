# Operating `targetdb`

## Configuration file

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

## Insert records into a table

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
pfs-targetdb-cli insert -c dbconf.toml -t filter_name filter_names.csv \
    --commit --fetch
```

This simple operation can be executed for the `proposal_category`, `proposal`, `input_catalog`, `target_type`, `sky`, and `filter_name` tables.

## Insert targets into the target table

For the target list uploaded via the PFS Target Uploader,
an `upload_id` is issued and `proposal_id` is assigned by the observatory.
One can insert it to the `target` table in the `targetdb` database.

```bash
pfs-targetdb-cli insert -c dbconf.toml -t target targets.ecsv \
    --from-uploader --upload-id "aabbccddeeffgghh" --proposal-id "S24B-QN001" \
    --commit
```

Note that the `input_catalog` and `proposal` tables must be filled prior to inserting the target list.
