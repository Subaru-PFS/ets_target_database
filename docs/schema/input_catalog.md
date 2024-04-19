# `input_catalog`

## Overview

The `input_catalog` table is used to store the information on catalogs for sources.

## Columns

Here are the columns in the `input_catalog` table:

| Column Name               | Type     | Description                                                         | Required[^1] | Default |
|---------------------------|----------|---------------------------------------------------------------------|--------------|---------|
| input_catalog_id          | int      | The ID of the input catalog                                         | (*)          |         |
| input_catalog_name        | str      | The name of the input catalog                                       |              |         |
| input_catalog_description | str      | A brief description of the input catalog                            |              |         |
| upload_id                 | str      | A 16-character string assigned at the submission of the target list |              | ""      |
| created_at                | datetime | The date and time in UTC when the record was created.               |              |         |
| updated_at                | datetime | The date and time in UTC when the record was last updated.          |              |         |

[^1]: Required when inserted by using the [CLI tool](../reference/cli.md) or equivalent functions.

## Unique constraint

- `input_catalog_id` is a unique constraint and the primary key of the table. The `input_catalog_id` column is used as follows.

| Start |   End | Description                                           |
|------:|------:|-------------------------------------------------------|
|     0 |   999 | Reserved for major survey catalogs                    |
|  1000 |  2999 | Sky object catalogs                                   |
|  3000 |  3999 | Flux standard star catalogs                           |
| 10000 | 89999 | General use with autoincrement                        |
| 90000 | 99999 | Reserved for internal use (engineering by March 2024) |

## Notes

General catalogs must use the autoincrement feature of the `input_catalog_id` column. Therefore, don't specify the `input_catalog_id` when inserting a new record.
Command line tools will check the IDs when one tries to insert a new record with a specified `input_catalog_id` and return an error if the ID is in the range with auto-increment.


## Available catalogs

These are example of the available input catalogs.

| input_catalog_id | input_catalog_name   | input_catalog_description                      |
|-----------------:|----------------------|------------------------------------------------|
|                0 | simulated            | simulated catalog                              |
|                1 | gaia_dr1             | Gaia Data Release 1                            |
|                2 | gaia_dr2             | Gaia Data Release 2                            |
|                3 | gaia_edr3            | Gaia Early Data Release 3                      |
|                4 | gaia_dr3             | Gaia Data Release 3                            |
|                5 | hscssp_pdr1_wide     | HSC-SSP Public Data Release 1 (Wide)           |
|                6 | hscssp_pdr1_dud      | HSC-SSP Public Data Release 1 (Deep+UltraDeep) |
|                7 | hscssp_pdr2_wide     | HSC-SSP Public Data Release 2 (Wide)           |
|                8 | hscssp_pdr2_dud      | HSC-SSP Public Data Release 2 (Deep+UltraDeep) |
|                9 | hscssp_pdr3_wide     | HSC-SSP Public Data Release 3 (Wide)           |
|               10 | hscssp_pdr3_dud      | HSC-SSP Public Data Release 3 (Deep+UltraDeep) |
|               11 | hscssp_pdr4_wide     | HSC-SSP Public Data Release 4 (Wide)           |
|               12 | hscssp_pdr4_dud      | HSC-SSP Public Data Release 4 (Deep+UltraDeep) |
|             1001 | sky_hscssp_s21a_wide | Sky positions from S21A HSC-SSP (Wide)         |
|             1002 | sky_ps1              | Sky positions from PS1                         |
|             1003 | sky_gaia             | Sky positions from Gaia                        |
|             1004 | sky_nops1            | Sky positionns for regions without PS1 data    |