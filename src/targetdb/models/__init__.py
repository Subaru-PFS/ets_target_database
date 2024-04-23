#!/usr/bin/env python

from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime

input_catalog_id_start: int = 10000
input_catalog_id_max: int = 89999
input_catalog_id_absolute_max: int = 99999

comment_created_at: str = "The date and time in UTC when the record was created"
comment_updated_at: str = "The date and time in UTC when the record was last updated"

Base = declarative_base()


class utcnow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


# Note: Order of import is important!
from .filter_name import filter_name  # noqa E402
from .proposal_category import proposal_category  # noqa E402
from .input_catalog import input_catalog  # noqa E402
from .target_type import target_type  # noqa E402
from .proposal import proposal  # noqa E402
from .sky import sky  # noqa E402
from .fluxstd import fluxstd  # noqa E402
from .target import target  # noqa E402

from .cluster import cluster  # noqa E402


__all__ = [
    "Base",
    "filter_name",
    "proposal_category",
    "input_catalog",
    "target_type",
    "proposal",
    "sky",
    "fluxstd",
    "target",
    "cluster",
    "input_catalog_id_start",
    "input_catalog_id_max",
    "input_catalog_id_absolute_max",
    "comment_created_at",
    "comment_updated_at",
    "utcnow",
]
