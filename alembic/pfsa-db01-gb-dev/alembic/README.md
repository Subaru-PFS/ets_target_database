# Generic single-database configuration.

## Basic workflow

Reference: https://alembic.sqlalchemy.org/en/latest/tutorial.html

### Modify code of targetdb


### Run alembic

Create a new revision file.

```bash
alembic -c <config file> revision --autogenerate -m "Add columns"
```

Check the output file under the `versions` directory.

Upgrade to the new revision.

```bash
alembic -c <config file> upgrade head
```

### count duplicated rows

```sql
SELECT COUNT(*)
FROM sky a
JOIN sky b ON a.obj_id = b.obj_id
              AND a.input_catalog_id = b.input_catalog_id
              AND a.version = b.version
              AND a.sky_id < b.sky_id
;
```

```sql
SELECT ct, count(*) AS ct_ct FROM (SELECT sky_id, input_catalog_id, version, count(*) AS ct FROM sky GROUP BY sky_id, input_catalog_id, version HAVING count(*) > 1) sub GROUP BY 1 ORDER BY 1;

SELECT ct, count(*) AS ct_ct FROM (SELECT obj_id, input_catalog_id, version, count(*) AS ct FROM sky WHERE version='20221031' GROUP BY obj_id, input_catalog_id, version HAVING count(*) > 1) sub GROUP BY 1 ORDER BY 1;

SELECT sky_id, input_catalog_id, version, count(*) FROM sky GROUP BY sky_id, input_catalog_id, version HAVING count(*) > 1;
SELECT DISTINCT version FROM sky;

SELECT obj_id, ra, dec, input_catalog_id, version, count(*) FROM sky GROUP BY obj_id, input_catalog_id, version HAVING count(*) > 1;

SELECT version, count(*) AS ct FROM sky GROUP BY 1;
 version  |     ct
----------+------------
 20220427 |       2747
 20220915 | 2004836366
 20221031 |  897209700
(3 rows)
```

### delete duplicated rows

```sql

```


### error

```
> time alembic -c /work/monodera/Subaru-PFS/alembic_configs/alembic_pfsa-db01-gb.ini upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade 6aec47e0f339 -> eeca77238d00, Add an index and uniqueconstraint on sky
 by obj_id, input_catalog_id, and version
Traceback (most recent call last):
  File "/work/monodera/pyvenvs/venv39/lib/python3.9/site-packages/sqlalchemy/engine/base.py", line 1964, in _exec_single
_context
    self.dialect.do_execute(
  File "/work/monodera/pyvenvs/venv39/lib/python3.9/site-packages/sqlalchemy/engine/default.py", line 748, in do_execute
    cursor.execute(statement, parameters)
psycopg2.errors.UniqueViolation: could not create unique index "uq_sky_obj_id_input_catalog_id_version"
DETAIL:  Key (obj_id, input_catalog_id, version)=(44332, 1002, 20220915) is duplicated.
```
