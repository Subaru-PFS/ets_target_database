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

