#!/usr/bin/env python

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
)

from . import Base


class proposal_category(Base):
    __tablename__ = "proposal_category"

    proposal_category_id = Column(
        Integer,
        primary_key=True,
        unique=True,
        autoincrement=False,
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
        proposal_category_id,
        proposal_category_name,
        proposal_category_description,
        created_at,
        updated_at,
    ):
        self.proposal_category_id = proposal_category_id
        self.proposal_category_name = proposal_category_name
        self.proposal_category_description = proposal_category_description
        self.created_at = created_at
        self.updated_at = updated_at
