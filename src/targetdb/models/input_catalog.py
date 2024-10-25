#!/usr/bin/env python

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.schema import Identity

from . import (
    Base,
    comment_created_at,
    comment_updated_at,
    input_catalog_id_max,
    input_catalog_id_start,
    utcnow,
)


class input_catalog(Base):
    __tablename__ = "input_catalog"

    input_catalog_id = Column(
        Integer,
        Identity(
            start=input_catalog_id_start,
            maxvalue=input_catalog_id_max,
            cycle=False,
        ),
        primary_key=True,
        unique=True,
        comment="Unique identifier for input catalogs",
    )
    input_catalog_name = Column(
        String,
        nullable=False,
        comment="Name of the input catalog (e.g., Gaia DR2, HSC-SSP PDR3, etc.)",
    )
    input_catalog_description = Column(
        String, default="", comment="Description of the input catalog"
    )
    upload_id = Column(
        String(16),
        default="",
        comment="A 8-bit hex string (16 characters) assigned at the submission of the target list (default: empty string)",
    )
    active = Column(
        Boolean,
        default=True,
        comment="Flag to indicate if the input catalog is active (default: True)",
    )
    is_classical = Column(
        Boolean, default=False, comment="True if the classical mode is requested"
    )

    is_user_pointing = Column(
        Boolean, default=False, comment="True if user-defined pointings are provided"
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
        input_catalog_id,
        input_catalog_name,
        input_catalog_description,
        upload_id,
        active,
        is_classical,
        is_user_pointing,
        created_at,
        updated_at,
    ):
        self.input_catalog_id = input_catalog_id
        self.input_catalog_name = input_catalog_name
        self.input_catalog_description = input_catalog_description
        self.upload_id = upload_id
        self.active = active
        self.is_classical = is_classical
        self.is_user_pointing = is_user_pointing
        self.created_at = created_at
        self.updated_at = updated_at
