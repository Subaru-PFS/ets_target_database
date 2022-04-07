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
from . import proposal
from . import target_type


class fluxstd(Base):
    __tablename__ = "fluxstd"

    fluxstd_id = Column(
        BigInteger,
        primary_key=True,
        unique=True,
        autoincrement=True,
        comment="Unique identifier for each flux standard star",
    )

    obj_id = Column(
        BigInteger,
        comment="Gaia EDR3 sourceid",
    )  # xxxx: need to understand more

    ra = Column(Float, comment="RA (ICRS, degree)")
    dec = Column(Float, comment="Dec (ICRS, degree)")
    epoch = Column(String, comment="Epoch (e.g., J2000.0, J2015.5, etc.)")

    tract = Column(
        Integer,
        comment="same definition as HSC-SSP?; can be derived from the coordinate",
    )  # xxxx: needed?
    patch = Column(
        Integer,
        comment="same definition as HSC-SSP?; can be derived from the coordinate; Note that it's defined as an integer",
    )  # xxxx: needed?

    target_type_id = Column(
        Integer,
        ForeignKey("target_type.target_type_id"),
        comment="target_type_id from the target_type table (must be 3 for FLUXSTD)",
    )

    input_catalog_id = Column(
        Integer,
        ForeignKey("input_catalog.input_catalog_id"),
        comment="input_catalog_id from the input_catalog table",
    )

    psf_mag_g = Column(Float, comment="g-band PSF magnitude (AB mag)")
    psf_mag_r = Column(Float, comment="r-band PSF magnitude (AB mag)")
    psf_mag_i = Column(Float, comment="i-band PSF magnitude (AB mag)")
    psf_mag_z = Column(Float, comment="z-band PSF magnitude (AB mag)")
    psf_mag_y = Column(Float, comment="y-band PSF magnitude (AB mag)")
    psf_mag_j = Column(Float, comment="J band PSF magnitude (AB mag)")

    psf_flux_g = Column(Float, comment="g-band PSF flux (nJy)")
    psf_flux_r = Column(Float, comment="r-band PSF flux (nJy)")
    psf_flux_i = Column(Float, comment="i-band PSF flux (nJy)")
    psf_flux_z = Column(Float, comment="z-band PSF flux (nJy)")
    psf_flux_y = Column(Float, comment="y-band PSF flux (nJy)")
    psf_flux_j = Column(Float, comment="J band PSF flux (nJy)")

    prob_f_star = Column(Float, comment="Probability to be a F-star")
    flag_dist = Column(
        Boolean,
        comment="True if the uncertainty of the distance estimate is too large (>20%)",
    )
    flag_ebv = Column(
        Boolean, comment="True if the uncertainty of E(B-V) is too large (>0.2 mag)"
    )

    # timestamp
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # relations to other tables
    target_types = relation(target_type, backref=backref("fluxstd"))
    input_catalogs = relation(input_catalog, backref=backref("fluxstd"))

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
        psf_mag_g,
        psf_mag_r,
        psf_mag_i,
        psf_mag_z,
        psf_mag_y,
        psf_mag_j,
        psf_flux_g,
        psf_flux_r,
        psf_flux_i,
        psf_flux_z,
        psf_flux_y,
        psf_flux_j,
        prob_f_star,
        flag_dist,
        flag_ebv,
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
        self.psf_mag_g = psf_mag_g
        self.psf_mag_r = psf_mag_r
        self.psf_mag_i = psf_mag_i
        self.psf_mag_z = psf_mag_z
        self.psf_mag_y = psf_mag_y
        self.psf_mag_j = psf_mag_j
        self.psf_flux_g = psf_flux_g
        self.psf_flux_r = psf_flux_r
        self.psf_flux_i = psf_flux_i
        self.psf_flux_z = psf_flux_z
        self.psf_flux_y = psf_flux_y
        self.psf_flux_j = psf_flux_j
        self.prob_f_star = prob_f_star
        self.flag_dist = flag_dist
        self.flag_ebv = flag_ebv
        self.created_at = created_at
        self.updated_at = updated_at
