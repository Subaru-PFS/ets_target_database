# Tables in the PFS Target Database

## Overview

The PFS Target Database contains the following tables:

- [filter_name](filter_name.md)
- [fluxstd](fluxstd.md)
- [input_catalog](input_catalog.md)
- [partner](partner.md)
- [pfs_arm](pfs_arm.md)
- [proposal](proposal.md)
- [proposal_category](proposal_category.md)
- [sky](sky.md)
- [target](target.md)
- [target_type](target_type.md)
- [user_pointing](user_pointing.md)

## Default values

The values in the "Default" column of each table are applied in two places:

- The CLI tool and `TargetDB.insert()` fill them in before inserting. A column
  missing from the input gets its default, and the CLI also replaces blank
  cells (empty strings, `NaN`, masked values) with it.
- Except for the `""` defaults, they are also the database's own column
  defaults. An `INSERT` that does not mention a column, from `psql` or any
  other client, stores the default. An `INSERT` that sends `NULL` explicitly
  stores `NULL`.

`""` defaults are stored as `NULL` when inserted through the CLI tool.

## Schema information by tbls

You can also look at the schema information generated
by the [tbls](https://github.com/k1LoW/tbls) package in the [tbls](../tbls/README.md) section.
They also contain the entity-relationship diagram (ERD) of the database.
