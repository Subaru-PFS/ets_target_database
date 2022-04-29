#!/usr/bin/env python

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import backref
from sqlalchemy.orm import relation

from . import Base
from . import input_catalog
from . import target_type


class sky(Base):
    __tablename__ = "sky"

    sky_id = Column(
        BigInteger,
        primary_key=True,
        unique=True,
        autoincrement=True,
        comment="Unique identifier for each sky position",
    )

    # This is string in Murata-san's catalog.
    # Note: int/int64 for other tables.
    obj_id = Column(
        BigInteger,
        comment="Object ID in the sky catalog",
    )

    ra = Column(Float, comment="RA (ICRS, degree)")
    dec = Column(Float, comment="Dec (ICRS, degree)")
    epoch = Column(String, comment="Epoch (e.g., J2000.0, J2015.5, etc.)")

    tract = Column(
        Integer,
        comment="Tract from HSC-SSP",
    )  # xxxx: needed?
    patch = Column(
        Integer,
        comment="Patch from HSC-SSP",
    )  # xxxx: needed?

    target_type_id = Column(
        Integer,
        ForeignKey("target_type.target_type_id"),
        comment="target_type_id from the target_type table (must be 2 for SKY)",
    )

    input_catalog_id = Column(
        Integer,
        ForeignKey("input_catalog.input_catalog_id"),
        comment="input_catalog_id from the input_catalog table",
    )

    mag_thresh = Column(
        Float,
        comment="Sky intensity threshold in mag/arcsec^2 (only for HSC-SSP).",
    )

    # is_valid = Column(
    #     Boolean,
    #     default=True,
    #     comment="False if the position turned out to be on an astronomical source.",
    # )

    # version string
    version = Column(String, comment="Version string of the sky position")

    # timestamp
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # relations to other tables
    target_types = relation(target_type, backref=backref("sky"))
    input_catalogs = relation(input_catalog, backref=backref("sky"))

    def __init__(
        self,
        obj_id,
        ra,
        dec,
        epoch,
        tract,
        patch,
        target_type_id,
        input_catalog_id,
        # is_valid,
        version,
        created_at,
        updated_at,
    ):
        self.obj_id = obj_id
        self.ra = ra
        self.dec = dec
        self.epoch = epoch
        self.tract = tract
        self.patch = patch
        self.target_type_id = target_type_id
        self.input_catalog_id = input_catalog_id
        # self.is_valid = is_valid
        self.version = version
        self.created_at = created_at
        self.updated_at = updated_at
