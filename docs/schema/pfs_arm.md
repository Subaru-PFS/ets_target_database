# `pfs_arm`

The `pfs_arm` table contains the arm information of PFS.

## Columns

| Column Name | Data Type | Description                                                | Unit | Required[^1] | Default |
| ----------- | --------- | ---------------------------------------------------------- | ---- | ------------ | ------- |
| name        | str       | The name of the arm                                        |      | \*           |         |
| description | str       | A detailed description of the arm                          |      |              | ""      |
| created_at  | datetime  | The date and time in UTC when the record was created.      |      |              |         |
| updated_at  | datetime  | The date and time in UTC when the record was last updated. |      |              |         |

[^1]: Required when inserted by using the [CLI tool](../reference/cli.md) or equivalent functions.

## Unique constraint

- `name` is the primary key of the table.

## Notes

`name` is defined in [the PFS datamodel](https://github.com/Subaru-PFS/datamodel/blob/master/datamodel.txt). See the datamodel for more information.

## Available arms

| name | description           |
| ---- | --------------------- |
| b    | blue                  |
| r    | red                   |
| n    | near-infrared         |
| m    | medium resolution red |
