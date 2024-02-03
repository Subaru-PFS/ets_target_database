#!/usr/bin/env python


from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
)

from . import Base


class input_catalog(Base):
    __tablename__ = "input_catalog"

    input_catalog_id = Column(
        Integer,
        primary_key=True,
        unique=True,
        autoincrement=False,
        comment="Unique identifier for input catalogs",
    )
    input_catalog_name = Column(
        String,
        unique=True,
        comment="Name of the input catalog (e.g., Gaia DR2, HSC-SSP PDR3, etc.)",
    )
    input_catalog_description = Column(
        String, comment="Description of the input catalog"
    )
    upload_id = Column(
        String(16),
        comment="A 8-bit hex string (16 characters) assigned at the submission of the target list (default: empty string)",
        default="",
    )
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(
        self,
        input_catalog_id,
        input_catalog_name,
        input_catalog_description,
        upload_id,
        created_at,
        updated_at,
    ):
        self.input_catalog_id = input_catalog_id
        self.input_catalog_name = input_catalog_name
        self.input_catalog_description = input_catalog_description
        self.upload_id = upload_id
        self.created_at = created_at
        self.updated_at = updated_at
