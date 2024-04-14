#!/usr/bin/env python

# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base

input_catalog_id_start = 10000
input_catalog_id_max = 89999
input_catalog_id_absolute_max = 99999

Base = declarative_base()

# Note: Order of import is important!
from .filter_name import filter_name  # isort:skip
from .proposal_category import proposal_category  # isort:skip
from .input_catalog import input_catalog  # isort:skip
from .target_type import target_type  # isort:skip
from .proposal import proposal  # isort:skip
from .sky import sky  # isort:skip
from .fluxstd import fluxstd  # isort:skip
from .target import target  # isort:skip

from .cluster import cluster  # isort:skip


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
]
