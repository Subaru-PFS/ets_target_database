#!/usr/bin/env python

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from . import Base, comment_created_at, comment_updated_at, utcnow


class partner(Base):
    __tablename__ = "partner"

    partner_id = Column(
        Integer,
        primary_key=True,
        unique=True,
        autoincrement=False,
        comment="Unique identifier of the partner",
    )
    partner_name = Column(
        String,
        unique=True,
        nullable=False,
        comment="Name of the partner (e.g., subaru, gemini, keck, and uh)",
    )
    partner_description = Column(
        String, default="", comment="Description of the partner"
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

    proposals = relationship("proposal", backref="partner")
