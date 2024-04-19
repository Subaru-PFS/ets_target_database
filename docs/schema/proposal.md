# `proposal`

## Overview

The `proposal` table is used to store the information on proposals.

## Columns

Here are the columns in the `proposal` table:

| Column Name          | Type     | Description                                                | Unit | Required[^1] | Default |
|----------------------|----------|------------------------------------------------------------|------|--------------|---------|
| proposal_id          | str      | Proposal-ID (e.g, S23B-QN901)                              |      | *            |         |
| group_id             | str      | Group ID issued by STARS (e.g., o21195)                    |      |              |         |
| pi_first_name        | str      | PI's first name                                            |      |              |         |
| pi_last_name         | str      | PI's last name                                             |      |              |         |
| pi_middle_name       | str      | PI's middle name                                           |      |              |         |
| rank                 | float    | TAC score (0 to 10, higher is better)                      |      |              |         |
| grade                | str      | TAC grade (A, B, C, D, F)                                  |      |              |         |
| allocated_time       | float    | Total allocated fiberhours                                 | h    |              |         |
| allocated_time_lr    | float    | Allocated fiberhours for low-resolution mode               | h    |              |         |
| allocated_time_mr    | float    | Allocated fiberhours for medium-resolution mode            | h    |              |         |
| proposal_category_id | int      | `proposal_category_id` in the `proposal_category` table    |      |              |         |
| created_at           | datetime | The date and time in UTC when the record was created.      |      |              |         |
| updated_at           | datetime | The date and time in UTC when the record was last updated. |      |              |         |

[^1]: Required when inserted by using the [CLI tool](../reference/cli.md) or equivalent functions.

## Unique constraint

- `proposal_id` is the primary key of the table and must be unique.

## Foreign key constraints

- `proposal_category_id` is a foreign key constraint that references the `proposal_category_id` in the `proposal_category` table.

## Notes

- `proposal_id`s are also provided by STARS. It is also important to discuss with the OCS team for the downstream process.
- `rank` is a float value from 0 to 10, where a higher value indicates a higher priority.
- `grade` is a TAC grade and is one of the following: A, B, C, D, F.
