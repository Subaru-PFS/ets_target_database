# `sky`

## Overview

The `sky` table is used to store the information on proposals.

## Columns

Here are the columns in the `sky` table:

| Column Name      | Data Type | Description                                                                   | Unit            | Required | Default |
| ---------------- | --------- | ----------------------------------------------------------------------------- | --------------- | -------- | ------- |
| sky_id           | int64     | The unique identifier of the record                                           |                 |          |         |
| obj_id           | int64     | Object identifier in the catalog                                              |                 | \*       |         |
| obj_id_orig      | str       | (Obsolete) Original object identifier                                         |                 |          |         |
| ra               | float     | Right ascension of the object on ICRS at the reference epoch                  | deg             | \*       |         |
| dec              | float     | Declination of the object on ICRS at the reference epoch                      | deg             | \*       |         |
| epoch            | str       | Reference epoch                                                               |                 |          | J2000.0 |
| tract            | int       | Tract defined by, e.g., the HSC pipeline                                      |                 |          |         |
| patch            | int       | Patch defined by, e.g., the HSC pipeline                                      |                 |          |         |
| target_type_id   | int       | `target_type_id` in the `target_type` table (it is `2` for `SKY`)             |                 |          | 2       |
| input_catalog_id | int       | `input_catalog_id` in the `input_catalog` table (should be in `[1000, 2999]`) |                 | \*       |         |
| mag_thresh       | float     | Sky intensity threshold (only for HSC-SSP)                                    | AB mag/arcsec^2 |          |         |
| version          | str       | The version of the catalog                                                    |                 | \*       |         |
| created_at       | datetime  | The date and time in UTC when the record was created.                         |                 |          |         |
| updated_at       | datetime  | The date and time in UTC when the record was last updated.                    |                 |          |         |

[^1]: Required when inserted by using the [CLI tool](../reference/cli.md) or equivalent functions.

## Unique constraint

- `sky_id` is the primary key of the table and set as an auto-increment column.
- A set of `(obj_id, input_catalog_id, version)` must be unique.

## Foreign key constraints

- `target_type_id` is a foreign key constraint that references the `target_type_id` in the `target_type` table.
- `input_catalog_id` is a foreign key constraint that references the `input_catalog_id` in the `input_catalog` table.
