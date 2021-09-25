#!/usr/bin/env python

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

# from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import backref
from sqlalchemy.orm import relation

from . import Base


class input_catalog(Base):
    __tablename__ = "input_catalog"

    input_catalog_id = Column(
        Integer,
        primary_key=True,
        unique=True,
        autoincrement=True,
        comment="Unique identifier for input catalogs",
    )
    input_catalog_name = Column(
        String, comment="Name of the input catalog (e.g., Gaia DR2, HSC-SSP PDR3, etc.)"
    )
    input_catalog_description = Column(
        String, comment="Description of the input catalog"
    )
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(
        self,
        input_catalog_id,
        input_catalog_name,
        input_catalog_description,
        created_at,
        updated_at,
    ):
        self.input_catalog_id = input_catalog_id
        self.input_catalog_name = input_catalog_name
        self.input_catalog_description = input_catalog_description
        self.created_at = created_at
        self.updated_at = updated_at
