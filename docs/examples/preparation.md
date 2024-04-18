# Preparetion of input data

## Prepare fluxstd data

```bash
pfs_targetdb_fluxstd_prepdata \
    -c dbconf.toml \
    --version "3.3" \
    --input_catalog_id 3006 \
    --rename-cols '{"fstar_gaia": "is_fstar_gaia"}' \
    input_directory \
    output_directory
```

The above example does the following:
- Read input files in one of csv, ecsv feather, and parquet formats from `input_directory`.
- Add additional required columns, `version` and `input_catalog_id`.
- Rename the column `fstar_gaia` to `is_fstar_gaia`.
- Save the output files to `output_directory`.

Then, one can insert the prepared flux standard data into the `fluxstd` table in the `targetdb` database by using the above command, `pfs_targetdb_insert`.
