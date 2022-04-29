#!/usr/bin/env python

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Note: Order of import is important!
from .proposal_category import proposal_category  # isort:skip
from .input_catalog import input_catalog  # isort:skip
from .target_type import target_type  # isort:skip
from .proposal import proposal  # isort:skip
from .sky import sky  # isort:skip
from .fluxstd import fluxstd  # isort:skip
from .target import target  # isort:skip
from .cluster import cluster  # isort:skip
