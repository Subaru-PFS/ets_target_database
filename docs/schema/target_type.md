# `target_type`

The `target_type` table contains information about the different types of targets in the database.

## Columns

| Column Name             | Data Type | Description                                                | Unit | Required[^1] | Default |
| ----------------------- | --------- | ---------------------------------------------------------- | ---- | ------------ | ------- |
| target_type_id          | int       | The unique identifier of the target type                   |      | \*           |         |
| target_type_name        | str       | The name of the target type                                |      | \*           |         |
| target_type_description | str       | A detailed description of the target type                  |      |              | ""      |
| created_at              | datetime  | The date and time in UTC when the record was created.      |      |              |         |
| updated_at              | datetime  | The date and time in UTC when the record was last updated. |      |              |         |

[^1]: Required when inserted by using the [CLI tool](../reference/cli.md) or equivalent functions.

## Unique constraint

- `target_type_id` is the primary key of the table, but not set as an auto-increment column.

## Notes

`target_type` is defined in [the PFS datamodel](https://github.com/Subaru-PFS/datamodel/blob/master/datamodel.txt). See the datamodel for more information.

## Available target types

| target_type_id | target_type_name | target_type_description                                                       |
| -------------: | ---------------- | ----------------------------------------------------------------------------- |
|              1 | SCIENCE          | the fiber is intended to be on a science target                               |
|              2 | SKY              | the fiber is intended to be on blank sky, and used for sky subtraction        |
|              3 | FLUXSTD          | the fiber is intended to be on a flux standard, and used for flux calibration |
|              4 | UNASSIGNED       | the fiber is not targeted on anything in particular                           |
|              5 | ENGINEERING      | the fiber is an engineering fiber                                             |
|              6 | SUNSS_IMAGING    | the fiber goes to the SuNSS imaging leg                                       |
|              7 | SUNSS_DIFFUSE    | the fiber goes to the SuNSS diffuse leg                                       |
|              8 | DCB              | fiber goes to DCB/DCB2                                                        |
|              9 | HOME             | cobra is going to home position                                               |
|             10 | BLACKSPOT        | cobra is going to black spot position                                         |
|             11 | AFL              | the fiber is fed by all fiber lamp cable                                      |
|             12 | SCIENCE_MASKED   | the fiber is on a science target redacted for privacy                         |
