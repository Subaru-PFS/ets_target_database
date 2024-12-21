# `proposal_category`

## Overview

The `proposal_catagory` table is used to store the information on proposal categories.

## Columns

Here are the columns in the `proposal_category` table:

| Column Name                   | Type     | Description                                                | Required[^1] | Default |
| ----------------------------- | -------- | ---------------------------------------------------------- | ------------ | ------- |
| proposal_category_id          | int      | The unique identifier of the proposal category             | \*           |         |
| proposal_category_name        | str      | The name of the proposal category                          | \*           |         |
| proposal_category_description | str      | A brief description of the proposal category               |              | ""      |
| created_at                    | datetime | The date and time in UTC when the record was created.      |              |         |
| updated_at                    | datetime | The date and time in UTC when the record was last updated. |              |         |

[^1]: Required when inserted by using the [CLI tool](../reference/cli.md) or equivalent functions.

## Unique constraint

- `proposal_category_id` is the primary key of the table and must be unique. However, it not set as an auto-increment column.

## Available proposal categories

| proposal_category_id | proposal_category_name | proposal_category_description |
| -------------------: | ---------------------- | ----------------------------- |
|                    1 | openuse                | Subaru openuse proposal       |
