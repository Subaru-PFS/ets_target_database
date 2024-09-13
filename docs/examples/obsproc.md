# Practical workflow for the preparation of PFS observations

This document describes a practical workflow for the preparation of PFS observations.
This is intended for the obsproc team members and other obsevatory personnel
who prepares for the PFS observations.

Here, we assume that the database has already been set up and the user has the necessary permissions to insert data into the database.
You need to prepare `db_config.toml` file to connect to the database.

The configuration file should look like this.
Replace the values with the actual values for your environment.
If you don't know the values, please ask the obsproc team.

```toml title="db_config.toml"
[targetdb.db]
host = "localhost"
port = 15432
dbname = "targetdb_local_test"
user = "admin"
password = "admin"
dialect = "postgresql"

[schemacrawler]
SCHEMACRAWLERDIR = "<path to SchemaCrawler directory>"

# The following parameters for the uploader will be used to rsync as follows.
# $ rsync -avz -e ssh user@host:data_dir/????/??/????????-??????-{upload_id}
# user can be omitted or blank ("") if the user name is the same as the local user name or an alias is defined in ~/.ssh/config.
[uploader]
host = "<hostname of uploader>"
user = "<user name of uploader>"
data_dir = "<path to the data directory on the uploader>"
```

## Working with filter names, proposal categories, and target types

### Insert to the `filter_name`, `proposal_category`, `pfs_arm`, and `target_type` tables

`filter_name`, `proposal_category`, `pfs_arm`, and `target_type` tables are expected to be very static and not frequently updated.
Note that you are most likely to skip this step as these tables are already populated in the database.

The contents of CSV files to be inserted for these tables are as follows:

```csv title="filter_names.csv"
filter_name,filter_name_description
g_hsc,HSC g filter
r_old_hsc,HSC r filter (old r filter)
r2_hsc,HSC r2 filter
i_old_hsc,HSC i filter (old i filter)
i2_hsc,HSC i2 filter
z_hsc,HSC z filter
y_hsc,HSC Y filter
g_ps1,Pan-STARRS1 g filter
r_ps1,Pan-STARRS1 r filter
i_ps1,Pan-STARRS1 i filter
z_ps1,Pan-STARRS1 z filter
y_ps1,Pan-STARRS1 y filter
bp_gaia,Gaia BP filter
rp_gaia,Gaia RP filter
g_gaia,Gaia G filter
u_sdss,SDSS u filter
g_sdss,SDSS g filter
r_sdss,SDSS r filter
i_sdss,SDSS i filter
z_sdss,SDSS z filter
```

```csv title="proposal_categories.csv"
proposal_category_id,proposal_category_name,proposal_category_description
1,openuse,Subaru openuse proposal
2,keck,Subaru/Keck time exchange proposal
3,gemini,Subaru/Gemini time exchange proposal
4,uh,University of Hawaii proposal
```

```csv title="pfs_arm.csv"
name,description
b,"blue"
r,"red"
n,"near-infrared"
m,"medium resolution red"
```

```csv title="target_types.csv"
target_type_id,target_type_name,target_type_description
1,SCIENCE,the fiber is intended to be on a science target
2,SKY,"the fiber is intended to be on blank sky, and used for sky subtraction"
3,FLUXSTD,"the fiber is intended to be on a flux standard, and used for flux calibration"
4,UNASSIGNED,the fiber is not targeted on anything in particular
5,ENGINEERING,the fiber is an engineering fiber
6,SUNSS_IMAGING,the fiber goes to the SuNSS imaging leg
7,SUNSS_DIFFUSE,the fiber goes to the SuNSS diffuse leg
8,DCB,fiber goes to DCB/DCB2
9,HOME,cobra is going to home position
10,BLACKSPOT,cobra is going to black spot position
```

You can insert these data into the database using the following commands:

```console
$ pfs-targetdb-cli insert filter_names.csv -c db_config.toml --table filter_name --commit
$ pfs-targetdb-cli insert proposal_categories.csv -c db_config.toml --table proposal_category --commit
$ pfs-targetdb-cli insert pfs_arm.csv -c db_config.toml --table pfs_arm --commit
$ pfs-targetdb-cli insert target_types.csv -c db_config.toml --table target_type --commit
```

## Working with flux standard stars

### Insert to the `input_catalog` table for `fluxstd`

First, you need to make sure your flux standard star catalog is already in the `input_catalog` table.
If it's not, you need to insert the `input_catalog` row for flux standard stars you are working with.
Suppose you are going to insert the F-star catalog version `3.3` of the `fluxstd` data.
Then, you need to prepare the following CSV file:

```csv title="input_catalog_fluxstd.csv"
input_catalog_id,input_catalog_name,input_catalog_description,upload_id
3006,"Fstar_v3.3","F-type star candidates version 3.3 for flux calibration",
```

Note that you need to supply `input_catalog_id` manually for input catalogs of calibration data.
Use of `input_catalog_id` can be found in [input_catalog](../schema/input_catalog.md#unique-constraint)
and you should get agreement with the other obsproc team members to avoid confusion.

Then, you can insert the `input_catalog` data into the database using the following command:

```console
$ pfs-targetdb-cli insert input_catalog_fluxstd.csv -c db_config.toml --table input_catalog --commit
```

### Prepare `fluxstd` data

Suppose you have a set of `feather` file in the directory `fluxstd/feather-original`
and you are going to supply addional columns to the data and save them in the directory `fluxstd/feather`
to be ready to insert into the database.

In the example below, we are going to rename the column `fstar_gaia` to `is_fstar_gaia`
in addition to supplying the version string `"3.3"` and the `input_catalog_id` of `3006`.

```text
$ pfs-targetdb-cli prep-fluxstd fluxstd/feather-original fluxstd/feather \
    --version="3.3" \
    --input_catalog_id 3006
    --rename-cols='{"fstar_gaia": "is_fstar_gaia"}'
    --format feather
```

### Insert `fluxstd` data

You can now insert the `fluxstd` data into the database similar to other tables using the following command:

```console
$ pfs-targetdb-cli insert fluxstd/feather/ra354.8_354.9_dec-40.0_90.0.feather \
    -c db_config.toml --table fluxstd --commit
```

## Working with sky objects

### Insert `sky` data

WIP

## Working with target lists

### Parse an allocation summary file

Suppose you have an Excel file named `pfs_allocation_summary.xlsx` with 2 sheets, `Proposals` and `Allocation`, as shown below.

**`Proposals` Sheet**:

| proposal_id | input_catalog_name | input_catalog_description | group_id | pi_first_name | pi_last_name | pi_middle_name | proposal_category_name | upload_id        | n_obj | fiberhour_total | fiberhour_lr | fiberhour_mr | rot_total | rot_lr | rot_mr |
| ----------- | ------------------ | ------------------------- | -------- | ------------- | ------------ | -------------- | ---------------------- | ---------------- | ----- | --------------- | ------------ | ------------ | --------- | ------ | ------ |
| S99A-QT001  | pfs_example_1      | Example target list 1     | o99101   | Eiichi        | Shibusawa    |                | openuse                | d6e94eae259faf4e | 1572  | 379.5           | 379.5        |              | 5.2       | 5.2    |        |
| S99A-QT002  | pfs_example_2      | Example target list 2     | o99102   | Umeko         | Tsuda        |                | openuse                | 5f695375c60f34c7 | 9712  | 17504           | 17504        |              | 15.83     | 15.83  |        |
| S99A-QT003  | pfs_example_3      | Example target list 3     | o99103   | Shibasaburo   | Kitasato     |                | openuse                | ba59115da8084653 | 2047  | 395.25          | 395.25       |              | 12.7      | 12.7   |        |

**`Allocation` Sheet**:

| proposal_id | grade | rank | allocated_rot_total | allocated_rot_lr | allocated_rot_mr | allocated_time_total | allocated_time_lr | allocated_time_mr | n_ppc | allocation_rate_lr | allocation_rate_mr | completion_rate_lr | completion_rate_mr |
| ----------- | ----- | ---- | ------------------- | ---------------- | ---------------- | -------------------- | ----------------- | ----------------- | ----- | ------------------ | ------------------ | ------------------ | ------------------ |
| S99A-QT001  | A     | 9    | 2.8                 |                  | 2.8              | 284.25               | 0                 | 284.25            | 9     | 0.749011858        |                    | 0.723              |                    |
| S99A-QT002  | B     | 6.5  | 6.5                 | 6.5              |                  | 8140.5               | 8140.5            | 0                 | 21    | 0.465065128        |                    | 0.279              |                    |
| S99A-QT003  | B     | 6    | 9.6                 | 9.6              |                  | 350.25               | 350.25            | 0                 | 31    | 0.886148008        |                    | 0.684              |                    |

Then, execute the following command to parse the Excel file and generate CSV files to be used to insert data into the database.:

```console
$ pfs-targetdb-cli parse-alloc pfs_allocation_summary.xlsx
```

The command will generate the following CSV files in the current directory.

```csv title="proposal.csv"
proposal_id,group_id,pi_first_name,pi_last_name,pi_middle_name,rank,grade,allocated_time_total,allocated_time_lr,allocated_time_mr,proposal_category_name,is_too
S99A-QT001,o99101,Eiichi,Shibusawa,,9.0,A,284.25,0.0,284.25,openuse,false
S99A-QT002,o99102,Umeko,Tsuda,,6.5,B,8140.5,8140.5,0.0,openuse,false
S99A-QT003,o99103,Shibasaburo,Kitasato,,6.0,B,350.25,350.25,0.0,openuse,true
```

```csv title="input_catalogs.csv"
input_catalog_name,input_catalog_description,upload_id,proposal_id,is_classical
pfs_example_1,Example target list 1,d6e94eae259faf4e,S99A-QT001,false
pfs_example_2,Example target list 2,5f695375c60f34c7,S99A-QT002,false
pfs_example_3,Example target list 3,ba59115da8084653,S99A-QT003,true
```

### Insert to the `proposal` and `input_catalog` tables for `target` data

You can insert them into the database using the following commands:

```console
$ pfs-targetdb-cli insert proposal.csv -c db_config.toml --table proposal --commit
$ pfs-targetdb-cli insert input_catalogs.csv -c db_config.toml --table input_catalog --commit
```

### Transfer target lists from the uploader to local storage

You need to transfer the target lists from the uploader to the local storage.

```console
$ pfs-targetdb-cli transfer-targets input_catalogs.csv -c db_config.toml
```

At the end of the command, a summary will be shown as follows.

```
       upload_id  status  n_transfer
d6e94eae259faf4e success           1
5f695375c60f34c7 WARNING           2
ba59115da8084653  FAILED           0
```

You should look at the `WARNING` and `FAILED` entries to complete the transfer.
In the cases above, `WARNING` is shown because there are more than one directories with `upload_id=5f695375c60f34c7 ` transfered (`n_transfer=2`).
The `FAILED` is shown because it failed to find an appropriate directory.

This command will transfer the target lists from the uploader to the local storage.
For example, you will see the following directories in the current directory:

```
20240221-001431-d6e94eae259faf4e/
20240228-050253-5f695375c60f34c7/
20240229-013729-ba59115da8084653/
```

### Insert to the `target` table

You can insert the target data into the database using the following command:

```console
$ pfs-targetdb-cli insert-targets ./input_catalogs.csv -c db_config.toml --commit
```

You can also insert individual target lists into the database using the following command:

```
$ pfs-targetdb-cli insert 20240221-001431-d6e94eae259faf4e/target_d6e94eae259faf4e.ecsv -c db_config.toml -t target --from-uploader --upload_id d6e94eae259faf4e --proposal_id S99A-QT001 --commit
$ pfs-targetdb-cli insert 20240228-050253-5f695375c60f34c7/target_5f695375c60f34c7.ecsv -c db_config.toml -t target --from-uploader --upload_id 5f695375c60f34c7 --proposal_id S99A-QT002 --commit
$ pfs-targetdb-cli insert 20240229-013729-ba59115da8084653/target_ba59115da8084653.ecsv -c db_config.toml -t target --from-uploader --upload_id ba59115da8084653 --proposal_id S99A-QT003 --commit
```
