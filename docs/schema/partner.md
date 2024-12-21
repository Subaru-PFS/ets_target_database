# `partner`

## Overview

The `partner` table is used to store the information on partner institutions.

## Columns

Here are the columns in the `partner` table:

| Column Name         | Type     | Description                                                | Required[^1] | Default |
| ------------------- | -------- | ---------------------------------------------------------- | ------------ | ------- |
| partner_id          | int      | The unique identifier of the partner                       | \*           |         |
| partner_name        | str      | The name of the partner                                    | \*           |         |
| partner_description | str      | A brief description of the partner                         |              | ""      |
| created_at          | datetime | The date and time in UTC when the record was created.      |              |         |
| updated_at          | datetime | The date and time in UTC when the record was last updated. |              |         |

[^1]: Required when inserted by using the [CLI tool](../reference/cli.md) or equivalent functions.

## Unique constraint

- `partner_id` is the primary key of the table and must be unique. However, it not set as an auto-increment column.

## Available proposal categories

| partner_id | partner_name | partner_description    |
| ---------: | ------------ | ---------------------- |
|          1 | subaru       | Subaru Telescope       |
|          2 | keck         | W. M. Keck Observatory |
|          3 | gemini       | Gemini Observatory     |
|          4 | uh           | University of Hawaii   |
