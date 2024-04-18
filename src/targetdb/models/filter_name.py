#!/usr/bin/env python


from sqlalchemy import (
    Column,
    DateTime,
    String,
)

from . import Base, comment_created_at, comment_updated_at


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
        comment="Description of the filter",
    )

    created_at = Column(DateTime, comment=comment_created_at)
    updated_at = Column(DateTime, comment=comment_updated_at)

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
