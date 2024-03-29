#!/usr/bin/env python

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    String,
)

from . import Base


class unique_object(Base):
    __tablename__ = "unique_object"

    unique_object_id = Column(
        BigInteger,
        primary_key=True,
        unique=True,
        autoincrement=True,
        comment="Unique unique_object identifier",
    )
    ra = Column(Float, comment="ICRS (degree)")
    dec = Column(Float, comment="ICRS (degree)")
    epoch = Column(String, comment="Reference epoch, e.g., J2000.0, J2015.5, etc.")
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(
        self,
        ra,
        dec,
        epoch,
        created_at,
        updated_at,
    ):
        self.ra = ra
        self.dec = dec
        self.epoch = epoch
        self.created_at = created_at
        self.updated_at = updated_at
