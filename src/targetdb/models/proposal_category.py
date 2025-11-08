#!/usr/bin/env python

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
)

from . import Base, comment_created_at, comment_updated_at, utcnow


class proposal_category(Base):
    __tablename__ = "proposal_category"

    proposal_category_id = Column(
        Integer,
        primary_key=True,
        autoincrement=False,
        comment="Unique identifier of proposal category",
    )
    proposal_category_name = Column(
        String,
        unique=True,
        nullable=False,
        comment="Proposal category name (e.g., Openuse, Keck, Gemini, and UH)",
    )
    proposal_category_description = Column(
        String,
        default="",
        comment="Proposal category description (e.g., Openuse, Time exchange, etc.",
    )
    created_at = Column(
        DateTime,
        comment=comment_created_at,
        server_default=utcnow(),
    )
    updated_at = Column(
        DateTime,
        comment=comment_updated_at,
        onupdate=utcnow(),
    )

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
