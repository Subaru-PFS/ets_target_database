# `filter_name`

## Overview

The `filter_name` table is used to store the information on astronomical filters.

## Columns

Here are the columns in the `filter_name` table:

| Column Name             | Type     | Description                                                | Required[^1] | Default |
|-------------------------|----------|------------------------------------------------------------|--------------|---------|
| filter_name             | str      | The name of the filter.                                    | \*           |         |
| filter_name_description | str      | A brief description of the filter.                         |              | ""      |
| created_at              | datetime | The date and time in UTC when the record was created.      |              |         |
| updated_at              | datetime | The date and time in UTC when the record was last updated. |              |         |

[^1]: Required when inserted by using the [CLI tool](../reference/cli.md) or equivalent functions.

## Unique Constraint

- `filter_name` is the primary key of the table and must be unique.

## Notes

The records in the `filter_name` table are defined so that the data reduction pipeline can use them in the data reduction process.
Please ask the data reduction pipeline team for the list of filters before adding new records.

## Available filters

The fillowing `filter_name`s are available:

| filter_name | filter_name_description     |
|-------------|-----------------------------|
| g_hsc       | HSC g filter                |
| r_old_hsc   | HSC r filter (old r filter) |
| r2_hsc      | HSC r2 filter               |
| i_old_hsc   | HSC i filter (old i filter) |
| i2_hsc      | HSC i2 filter               |
| z_hsc       | HSC z filter                |
| y_hsc       | HSC Y filter                |
| g_ps1       | Pan-STARRS1 g filter        |
| r_ps1       | Pan-STARRS1 r filter        |
| i_ps1       | Pan-STARRS1 i filter        |
| z_ps1       | Pan-STARRS1 z filter        |
| y_ps1       | Pan-STARRS1 y filter        |
| bp_gaia     | Gaia BP filter              |
| rp_gaia     | Gaia RP filter              |
| g_gaia      | Gaia G filter               |
| u_sdss      | SDSS u filter               |
| g_sdss      | SDSS g filter               |
| r_sdss      | SDSS r filter               |
| i_sdss      | SDSS i filter               |
| z_sdss      | SDSS z filter               |
