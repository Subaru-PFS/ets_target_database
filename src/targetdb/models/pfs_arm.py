#!/usr/bin/env python

from sqlalchemy import (
    Column,
    DateTime,
    String,
)

from . import Base, comment_created_at, comment_updated_at, utcnow


class pfs_arm(Base):
    __tablename__ = "pfs_arm"

    name = Column(
        String,
        primary_key=True,
        unique=True,
        comment="Arm name (e.g., 'b', 'r', 'n', and 'm')",
    )
    description = Column(
        String,
        default="",
        comment="Arm description",
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
        name,
        description,
        created_at,
        updated_at,
    ):
        self.name = name
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at
