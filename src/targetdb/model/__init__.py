#!/usr/bin/env python

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .input_catalog import input_catalog  # isort:skip
from .object_type import object_type  # isort:skip
from .proposal import proposal  # isort:skip
from .proposal_category import proposal_category  # isort:skip
from .target import target  # isort:skip
from .unique_object import unique_object  # isort:skip