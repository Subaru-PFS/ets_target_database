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


class object_type(Base):
    __tablename__ = "object_type"

    object_type_id = Column(
        Integer,
        primary_key=True,
        unique=True,
        autoincrement=True,
        comment="Unique identifier for target types",
    )
    object_type_name = Column(
        String,
        unique=True,
        comment="Name for the target type (e.g., star, galaxy, quasar, etc.)",
    )
    object_type_description = Column(String, comment="Description of the target type")
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(
        self,
        # object_type_id,
        object_type_name,
        object_type_description,
        created_at,
        updated_at,
    ):
        # self.object_type_id = object_type_id
        self.object_type_name = object_type_name
        self.object_type_description = object_type_description
        self.created_at = created_at
        self.updated_at = updated_at
