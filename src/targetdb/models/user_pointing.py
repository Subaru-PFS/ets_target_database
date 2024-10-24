#!/usr/bin/env python3


from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import backref, relationship

from . import (
    Base,
    ResolutionMode,
    comment_created_at,
    comment_updated_at,
    input_catalog,
    utcnow,
)


class user_pointing(Base):
    __tablename__ = "user_pointing"

    user_pointing_id = Column(
        BigInteger,
        primary_key=True,
        comment="Unique identifier for each user-defined pointing (autoincremented primary key)",
    )

    ppc_code = Column(
        String,
        nullable=False,
        comment="String identifier of the pointing set either by the uploader or user",
    )

    ppc_ra = Column(
        Float, nullable=False, comment="RA of the pointing center (ICRS, degree)"
    )
    ppc_dec = Column(
        Float, nullable=False, comment="Dec of the pointing center (ICRS, degree)"
    )
    ppc_pa = Column(
        Float, nullable=False, comment="Position angle of the pointing center (degree)"
    )
    ppc_resolution = Column(
        Enum(ResolutionMode),
        nullable=False,
        comment="Resolution mode of the pointing ('L' or 'M')",
    )
    ppc_priority = Column(
        Float,
        nullable=False,
        comment="Priority of the pointing calculated by the uploader",
    )
    # f_fiber_usage = Column(
    #     Float,
    #     nullable=False,
    #     comment="Fraction of fibers used for the pointing",
    # )

    # relationship
    input_catalog_id = Column(
        Integer,
        ForeignKey("input_catalog.input_catalog_id"),
        nullable=False,
        comment="Input catalog ID from the input_catalog table",
    )

    # timestamp
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

    # define relation
    input_catalogs = relationship(input_catalog, backref=backref("user_pointing"))

    def __init__(
        self,
        ppc_id,
        ppc_code,
        ppc_ra,
        ppc_dec,
        ppc_pa,
        ppc_resolution,
        ppc_priority,
        input_catalog_id,
        created_at,
        updated_at,
    ):
        self.ppc_id = ppc_id
        self.ppc_code = ppc_code
        self.ppc_ra = ppc_ra
        self.ppc_dec = ppc_dec
        self.ppc_pa = ppc_pa
        self.ppc_resolution = ppc_resolution
        self.ppc_priority = ppc_priority
        self.input_catalog_id = input_catalog_id
        self.created_at = created_at
        self.updated_at = updated_at
