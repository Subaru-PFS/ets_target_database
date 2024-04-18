#!/usr/bin/env python

import sqlalchemy
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import backref, relationship

from . import Base, comment_created_at, comment_updated_at, input_catalog, target_type


class sky(Base):
    __tablename__ = "sky"
    # __table_args__ = (
    #     UniqueConstraint(
    #         "obj_id",
    #         "input_catalog_id",
    #         "version",
    #         name="uq_sky_obj_id_input_catalog_id_version",
    #     ),
    #     {},
    # )
    __table_args__ = (
        Index(
            "sky_q3c_ang2ipix_idx",
            sqlalchemy.text("q3c_ang2ipix(ra, dec)"),
        ),
        {},
    )

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
        nullable=False,
        comment="Object ID in the sky catalog",
    )
    obj_id_orig = Column(
        String,
        comment="Original object ID in the sky catalog",
    )

    ra = Column(Float, nullable=False, comment="RA (ICRS, degree)")
    dec = Column(Float, nullable=False, comment="Dec (ICRS, degree)")
    epoch = Column(
        String, default="J2000.0", comment="Epoch (e.g., J2000.0, J2015.5, etc.)"
    )

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
        default=2,
        comment="target_type_id from the target_type table (must be 2 for SKY)",
    )

    input_catalog_id = Column(
        Integer,
        ForeignKey("input_catalog.input_catalog_id"),
        nullable=False,
        index=True,
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
    version = Column(
        String, nullable=False, index=True, comment="Version string of the sky position"
    )

    # timestamp
    created_at = Column(DateTime, comment=comment_created_at)
    updated_at = Column(DateTime, comment=comment_updated_at)

    # relations to other tables
    target_types = relationship(target_type, backref=backref("sky"))
    input_catalogs = relationship(input_catalog, backref=backref("sky"))

    def __init__(
        self,
        obj_id,
        obj_id_orig,
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
        self.obj_id_orig = obj_id_orig
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
