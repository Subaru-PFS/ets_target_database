# `user_pointing`

## Overview

The `user_pointing` table is used to store the information on user-defined pointings.

## Columns

Here are the columns in the `user_pointing` table:

| Column Name      | Type     | Description                                                | Unit | Required[^1] | Default |
| ---------------- | -------- | ---------------------------------------------------------- | ---- | ------------ | ------- |
| user_pointing_id | int64    | The unique identifier of the record                        |      |              |         |
| ppc_code         | str      | Name of the pointing                                       |      | \*           |         |
| ppc_ra           | float    | RA at the pointing center                                  | deg  | \*           |         |
| ppc_dec          | float    | Dec at the pointing center                                 | deg  | \*           |         |
| ppc_pa           | float    | Position angle of the pointing center                      | deg  | \*           |         |
| ppc_resolution   | str      | Resolution mode of the pointing (`L` or `M`)               |      | \*           |         |
| ppc_priority     | float    | Sum of the priority weights of the pointing                |      | \*           |         |
| input_catalog_id | int      | `input_catalog_id` in the `input_catalog` table.           |      |              |         |
| created_at       | datetime | The date and time in UTC when the record was created.      |      |              |         |
| updated_at       | datetime | The date and time in UTC when the record was last updated. |      |              |         |

[^1]: Required when inserted by using the [CLI tool](../reference/cli.md) or equivalent functions.

## Unique constraint

- `user_pointing_id` is the primary key of the table and set as an auto-increment column.

## Foreign key constraints

- `input_catalog_id` is a foreign key constraint that references the `input_catalog_id` in the `input_catalog` table.
