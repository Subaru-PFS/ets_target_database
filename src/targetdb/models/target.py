#!/usr/bin/env python3

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
from . import proposal
from . import target_type


class target(Base):
    __tablename__ = "target"

    target_id = Column(
        BigInteger,
        primary_key=True,
        unique=True,
        autoincrement=True,
        comment="Unique identifier for each target",
    )

    proposal_id = Column(String, ForeignKey("proposal.proposal_id"))

    ob_code = Column(
        String,
        nullable=False,
        comment="Identifer for a combination of a target, observing mode, and exposure time in a program.",
    )

    obj_id = Column(
        BigInteger,
        comment="Object ID as specified by the observer at Phase 2 (can be same as the input_catalog_object_id)",
    )  # xxxx: need to understand more

    ra = Column(Float, comment="RA (ICRS, degree)")
    dec = Column(
        Float,
        comment="Dec (ICRS, degree)",
    )
    epoch = Column(String, default="J2000.0", comment="Epoch (default: J2000.0)")

    parallax = Column(Float, default=1e-7, comment="Parallax (mas)")
    pmra = Column(
        Float,
        default=0.0,
        comment="Proper motion in right ascension direction (mas/yr)",
    )
    pmdec = Column(
        Float, default=0.0, comment="Proper motion in declination direction (mas/yr)"
    )

    tract = Column(
        Integer,
        comment="same definition as HSC-SSP?; can be derived from the coordinate",
    )  # xxxx: needed?
    patch = Column(
        Integer,
        comment="same definition as HSC-SSP?; can be derived from the coordinate; Note that it's defined as an integer",
    )  # xxxx: needed?

    target_type_id = Column(Integer, ForeignKey("target_type.target_type_id"))

    input_catalog_id = Column(
        Integer,
        ForeignKey("input_catalog.input_catalog_id"),
        comment="Input catalog ID from the input_catalog table",
    )

    fiber_mag_g = Column(Float, comment="g-band magnitude within a fiber (AB mag)")
    fiber_mag_r = Column(Float, comment="r-band magnitude within a fiber (AB mag)")
    fiber_mag_i = Column(Float, comment="i-band magnitude within a fiber (AB mag)")
    fiber_mag_z = Column(Float, comment="z-band magnitude within a fiber (AB mag)")
    fiber_mag_y = Column(Float, comment="y-band magnitude within a fiber (AB mag)")
    fiber_mag_j = Column(Float, comment="J band magnitude within a fiber (AB mag)")

    psf_mag_g = Column(Float, comment="g-band PSF magnitude (AB mag)")
    psf_mag_r = Column(Float, comment="r-band PSF magnitude (AB mag)")
    psf_mag_i = Column(Float, comment="i-band PSF magnitude (AB mag)")
    psf_mag_z = Column(Float, comment="z-band PSF magnitude (AB mag)")
    psf_mag_y = Column(Float, comment="y-band PSF magnitude (AB mag)")
    psf_mag_j = Column(Float, comment="J band PSF magnitude (AB mag)")

    psf_mag_error_g = Column(Float, comment="Error in g-band PSF magnitude (AB mag)")
    psf_mag_error_r = Column(Float, comment="Error in r-band PSF magnitude (AB mag)")
    psf_mag_error_i = Column(Float, comment="Error in i-band PSF magnitude (AB mag)")
    psf_mag_error_z = Column(Float, comment="Error in z-band PSF magnitude (AB mag)")
    psf_mag_error_y = Column(Float, comment="Error in y-band PSF magnitude (AB mag)")
    psf_mag_error_j = Column(Float, comment="Error in J band PSF magnitude (AB mag)")

    psf_flux_g = Column(Float, comment="g-band PSF flux (nJy)")
    psf_flux_r = Column(Float, comment="r-band PSF flux (nJy)")
    psf_flux_i = Column(Float, comment="i-band PSF flux (nJy)")
    psf_flux_z = Column(Float, comment="z-band PSF flux (nJy)")
    psf_flux_y = Column(Float, comment="y-band PSF flux (nJy)")
    psf_flux_j = Column(Float, comment="J band PSF flux (nJy)")

    psf_flux_error_g = Column(Float, comment="Error in g-band PSF flux (nJy)")
    psf_flux_error_r = Column(Float, comment="Error in r-band PSF flux (nJy)")
    psf_flux_error_i = Column(Float, comment="Error in i-band PSF flux (nJy)")
    psf_flux_error_z = Column(Float, comment="Error in z-band PSF flux (nJy)")
    psf_flux_error_y = Column(Float, comment="Error in y-band PSF flux (nJy)")
    psf_flux_error_j = Column(Float, comment="Error in J band PSF flux (nJy)")

    filter_g = Column(String, comment="g-band filter (g_hsc, g_ps1, g_sdss, etc.)")
    filter_r = Column(String, comment="r-band filter (r_hsc, r_ps1, r_sdss, etc.)")
    filter_i = Column(String, comment="i-band filter (i_hsc, i_ps1, i_sdss, etc.)")
    filter_z = Column(String, comment="z-band filter (z_hsc, z_ps1, z_sdss, etc.)")
    filter_y = Column(String, comment="y-band filter (y_hsc, y_ps1, y_sdss, etc.)")
    filter_j = Column(String, comment="j-band filter (j_mko, etc.)")

    priority = Column(
        Float,
        comment="Priority of the target specified by the observer within the proposal",
    )
    effective_exptime = Column(Float, comment="Requested effective exposure time (s)")

    is_medium_resolution = Column(
        Boolean,
        default=False,
        comment="True if the medium resolution mode is requested",
    )

    # QA information
    qa_relative_throughput = Column(
        Float,
        default=1.0,
        comment="Relative throughput to the reference value requested by the observer (default: 1.0)",
    )
    qa_relative_noise = Column(
        Float,
        default=1.0,
        comment="Relative noise to the reference value requested by the observer (default: 1.0)",
    )
    qa_reference_lambda = Column(
        Float,
        comment="Reference wavelength to evaluate effective exposure time (angstrom or nm?)",
    )

    is_cluster = Column(
        Boolean,
        default=False,
        comment="True if it is a cluster of multiple targets.",
    )

    # timestamp
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # unique_objects = relation(unique_object, backref=backref("target"))
    proposals = relation(proposal, backref=backref("target"))
    target_types = relation(target_type, backref=backref("target"))
    input_catalogs = relation(input_catalog, backref=backref("target"))

    def __init__(
        self,
        proposal_id,
        ob_code,
        obj_id,
        ra,
        dec,
        epoch,
        tract,
        patch,
        target_type_id,
        input_catalog_id,
        #
        fiber_mag_g,
        fiber_mag_r,
        fiber_mag_i,
        fiber_mag_z,
        fiber_mag_y,
        fiber_mag_j,
        #
        psf_mag_g,
        psf_mag_r,
        psf_mag_i,
        psf_mag_z,
        psf_mag_y,
        psf_mag_j,
        #
        psf_mag_error_g,
        psf_mag_error_r,
        psf_mag_error_i,
        psf_mag_error_z,
        psf_mag_error_y,
        psf_mag_error_j,
        #
        psf_flux_g,
        psf_flux_r,
        psf_flux_i,
        psf_flux_z,
        psf_flux_y,
        psf_flux_j,
        #
        psf_flux_error_g,
        psf_flux_error_r,
        psf_flux_error_i,
        psf_flux_error_z,
        psf_flux_error_y,
        psf_flux_error_j,
        #
        filter_g,
        filter_r,
        filter_i,
        filter_z,
        filter_y,
        filter_j,
        #
        priority,
        effective_exptime,
        is_medium_resolution,
        #
        qa_relative_throughput,
        qa_relative_noise,
        qa_reference_lambda,
        #
        is_cluster,
        #
        created_at,
        updated_at,
    ):
        self.proposal_id = proposal_id
        self.ob_code = ob_code
        self.obj_id = obj_id
        self.ra = ra
        self.dec = dec
        self.epoch = epoch
        self.tract = tract
        self.patch = patch
        self.target_type_id = target_type_id
        self.input_catalog_id = input_catalog_id
        #
        self.fiber_mag_g = fiber_mag_g
        self.fiber_mag_r = fiber_mag_r
        self.fiber_mag_i = fiber_mag_i
        self.fiber_mag_z = fiber_mag_z
        self.fiber_mag_y = fiber_mag_y
        self.fiber_mag_j = fiber_mag_j
        #
        self.psf_mag_g = psf_mag_g
        self.psf_mag_r = psf_mag_r
        self.psf_mag_i = psf_mag_i
        self.psf_mag_z = psf_mag_z
        self.psf_mag_y = psf_mag_y
        self.psf_mag_j = psf_mag_j
        #
        self.psf_mag_error_g = psf_mag_error_g
        self.psf_mag_error_r = psf_mag_error_r
        self.psf_mag_error_i = psf_mag_error_i
        self.psf_mag_error_z = psf_mag_error_z
        self.psf_mag_error_y = psf_mag_error_y
        self.psf_mag_error_j = psf_mag_error_j
        #
        self.psf_flux_g = psf_flux_g
        self.psf_flux_r = psf_flux_r
        self.psf_flux_i = psf_flux_i
        self.psf_flux_z = psf_flux_z
        self.psf_flux_y = psf_flux_y
        self.psf_flux_j = psf_flux_j
        #
        self.psf_flux_error_g = psf_flux_error_g
        self.psf_flux_error_r = psf_flux_error_r
        self.psf_flux_error_i = psf_flux_error_i
        self.psf_flux_error_z = psf_flux_error_z
        self.psf_flux_error_y = psf_flux_error_y
        self.psf_flux_error_j = psf_flux_error_j
        #
        self.filter_g = filter_g
        self.filter_r = filter_r
        self.filter_i = filter_i
        self.filter_z = filter_z
        self.filter_y = filter_y
        self.filter_j = filter_j
        #
        self.priority = priority
        self.effective_exptime = effective_exptime
        self.is_medium_resolution = is_medium_resolution
        #
        self.qa_relative_throughput = qa_relative_throughput
        self.qa_relative_noise = qa_relative_noise
        self.qa_reference_lambda = qa_reference_lambda
        #
        self.is_cluster = is_cluster
        #
        self.created_at = created_at
        self.updated_at = updated_at
