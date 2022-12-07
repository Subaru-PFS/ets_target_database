#!/usr/bin/env python

# from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint

# from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import backref
from sqlalchemy.orm import relation

from . import Base
from . import proposal_category


class filter_name(Base):
    """Defines a photometric filter names."""

    __tablename__ = "filter_name"

    filter_name = Column(
        String,
        primary_key=True,
        unique=True,
        autoincrement=False,
        comment="Filter name (e.g., g_ps1)",
    )
    filter_name_description = Column(
        String,
        comment="Descriptino of the filter",
    )

    created_at = Column(DateTime, comment="Creation time [YYYY-MM-DDThh:mm:ss] (UTC)")
    updated_at = Column(DateTime, comment="Update time [YYYY-MM-DDThh:mm:ss] (UTC)")

    def __init__(
        self,
        filter_name,
        filter_name_description,
        created_at,
        updated_at,
    ):
        self.filter_name = filter_name
        self.filter_name_description = filter_name_description
        self.created_at = created_at
        self.updated_at = updated_at
