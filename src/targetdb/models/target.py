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
from . import input_catalog
from . import object_type
from . import proposal
from . import unique_object


class target(Base):
    __tablename__ = "target"

    target_id = Column(
        BigInteger,
        primary_key=True,
        unique=True,
        autoincrement=True,
        comment="Unique identifier for each target",
    )
    unique_object_id = Column(BigInteger, ForeignKey("unique_object.unique_object_id"))

    proposal_id = Column(String, ForeignKey("proposal.proposal_id"))

    obj_id = Column(
        BigInteger,
        comment="Object ID as specified by the observer at Phase 2 (can be same as the input_catalog_object_id)",
    )  # xxxx: need to understand more

    user_ra = Column(
        Float, comment="Original RA submitted by the observer at Phase 2 (ICRS, degree)"
    )
    user_dec = Column(
        Float,
        comment="Original Dec submitted by the observer at Phase 2 (ICRS, degree)",
    )
    user_epoch = Column(
        String, comment="Origina Epoch submitted by the observer at Phase 2"
    )
    match_distance = Column(
        Float,
        comment="Distance between the matched unique_object and the original coordinate (arcsec)",
    )

    tract = Column(
        Integer,
        comment="same definition as HSC-SSP?; can be derived from the coordinate",
    )  # xxxx: needed?
    patch = Column(
        Integer,
        comment="same definition as HSC-SSP?; can be derived from the coordinate; Note that it's defined as an integer",
    )  # xxxx: needed?

    object_type_id = Column(Integer, ForeignKey("object_type.object_type_id"))

    input_catalog_id = Column(
        Integer,
        ForeignKey("input_catalog.input_catalog_id"),
        comment="Input catalog ID from the input_catalog table",
    )
    input_catalog_obj_id = Column(
        BigInteger, comment="Object ID in the specified input catalog"
    )

    fiber_mag_g = Column(Float, comment="g-band magnitude within a fiber (AB mag)")
    fiber_mag_r = Column(Float, comment="r-band magnitude within a fiber (AB mag)")
    fiber_mag_i = Column(Float, comment="i-band magnitude within a fiber (AB mag)")
    fiber_mag_z = Column(Float, comment="z-band magnitude within a fiber (AB mag)")
    fiber_mag_y = Column(Float, comment="y-band magnitude within a fiber (AB mag)")
    fiber_mag_j = Column(Float, comment="J band magnitude within a fiber (AB mag)")
    photoz = Column(Float, comment="Photometric redshift for the object")

    # priority = Column(
    #     Float,
    #     comment="Priority of the target specified by the observer within the proposal",
    # )
    # effective_exptime = Column(Float, comment="Requested effective exposure time (s)")
    # is_medium_resolution = Column(
    #     Boolean, comment="True if the medium resolution mode is requested"
    # )

    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    unique_objects = relation(unique_object, backref=backref("target"))
    proposals = relation(proposal, backref=backref("target"))
    object_types = relation(object_type, backref=backref("target"))
    input_catalogs = relation(input_catalog, backref=backref("target"))

    def __init__(
        self,
        unique_object_id,
        proposal_id,
        obj_id,
        user_ra,
        user_dec,
        user_epoch,
        match_distance,
        tract,
        patch,
        object_type_id,
        input_catalog_id,
        input_catalog_obj_id,
        fiber_mag_g,
        fiber_mag_r,
        fiber_mag_i,
        fiber_mag_z,
        fiber_mag_y,
        fiber_mag_j,
        photoz,
        # priority,
        # effective_exptime,
        # is_medium_resolution,
        created_at,
        updated_at,
    ):
        self.unique_object_id = unique_object_id
        self.proposal_id = proposal_id
        self.obj_id = obj_id
        self.user_ra = user_ra
        self.user_dec = user_dec
        self.user_epoch = user_epoch
        self.match_distance = match_distance
        self.tract = tract
        self.patch = patch
        self.object_type_id = object_type_id
        self.input_catalog_id = input_catalog_id
        self.input_catalog_obj_id = input_catalog_obj_id
        self.fiber_mag_g = fiber_mag_g
        self.fiber_mag_r = fiber_mag_r
        self.fiber_mag_i = fiber_mag_i
        self.fiber_mag_z = fiber_mag_z
        self.fiber_mag_y = fiber_mag_y
        self.fiber_mag_j = fiber_mag_j
        self.photoz = photoz
        # self.priority = priority
        # self.effective_exptime = effective_exptime
        # self.is_medium_resolution = is_medium_resolution
        self.created_at = created_at
        self.updated_at = updated_at
