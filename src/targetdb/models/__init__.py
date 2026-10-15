#!/usr/bin/env python

import enum

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import expression, text
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


class ResolutionMode(enum.Enum):
    L = "L"
    M = "M"


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


def with_default(value):
    """Return ``default=`` and the equivalent ``server_default=`` for a scalar.

    Use as ``Column(Float, **with_default(1.0))``. The client-side ``default=``
    is what ``TargetDB.insert()`` and ``utils.fill_null_with_defaults()`` read;
    the ``server_default=`` puts the same value in the table DDL, so an INSERT
    or ``COPY`` that leaves the column out gets it from the database too.

    Not for ``""`` defaults: ``COPY`` writes ``""`` as NULL, so a ``''`` server
    default would only make an absent column differ from a blank one.
    """
    if isinstance(value, bool):
        server_default = text("true" if value else "false")
    elif isinstance(value, (int, float)):
        server_default = text(repr(value))
    elif isinstance(value, str) and value != "":
        server_default = value
    else:
        raise ValueError(f"No server default for {value!r}")
    return {"default": value, "server_default": server_default}


# Note: Order of import is important!
from .filter_name import filter_name  # noqa E402
from .pfs_arm import pfs_arm  # noqa E402
from .proposal_category import proposal_category  # noqa E402
from .partner import partner  # noqa E402

# from .proposal_grade import proposal_grade  # noqa E402
from .input_catalog import input_catalog  # noqa E402
from .user_pointing import user_pointing  # noqa E402
from .target_type import target_type  # noqa E402
from .proposal import proposal  # noqa E402
from .sky import sky  # noqa E402
from .fluxstd import fluxstd  # noqa E402
from .target import target  # noqa E402


__all__ = [
    "Base",
    "filter_name",
    "pfs_arm",
    "proposal_category",
    "partner",
    # "proposal_grade",
    "input_catalog",
    "user_pointing",
    "target_type",
    "proposal",
    "sky",
    "fluxstd",
    "target",
    "input_catalog_id_start",
    "input_catalog_id_max",
    "input_catalog_id_absolute_max",
    "comment_created_at",
    "comment_updated_at",
    "utcnow",
    "with_default",
    "ResolutionMode",
]
