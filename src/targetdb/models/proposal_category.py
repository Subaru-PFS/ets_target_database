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


class proposal_category(Base):
    __tablename__ = "proposal_category"

    proposal_category_id = Column(
        Integer,
        primary_key=True,
        unique=True,
        autoincrement=True,
        comment="Unique identifier of proposal category",
    )
    proposal_category_name = Column(
        String,
        unique=True,
        comment="Proposal category name (e.g., Openuse, Keck, Gemini, and UH)",
    )
    proposal_category_description = Column(
        String,
        comment="Proposal category description (e.g., Openuse, Time exchange, etc.",
    )
    created_at = Column(DateTime, comment="Creation time")
    updated_at = Column(DateTime, comment="Update time")

    def __init__(
        self,
        proposal_category_name,
        proposal_category_description,
        created_at,
        updated_at,
    ):
        self.proposal_category_name = proposal_category_name
        self.proposal_category_description = proposal_category_description
        self.created_at = created_at
        self.updated_at = updated_at
