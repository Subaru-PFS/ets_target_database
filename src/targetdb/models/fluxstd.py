#!/usr/bin/env python3

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)

# from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import backref, relationship

# from . import proposal
from . import Base, filter_name, input_catalog, target_type


class fluxstd(Base):
    __tablename__ = "fluxstd"
    __table_args__ = (
        UniqueConstraint(
            "obj_id",
            "input_catalog_id",
            "version",
            name="uq_obj_id_input_catalog_id_version",
        ),
        {},
    )

    fluxstd_id = Column(
        BigInteger,
        primary_key=True,
        unique=True,
        autoincrement=True,
        comment="Unique identifier for each flux standard star",
    )

    obj_id = Column(
        BigInteger,
        nullable=False,
        comment="Gaia EDR3 sourceid",
    )  # xxxx: need to understand more

    ra = Column(Float, nullable=False, comment="RA (ICRS, degree)")
    dec = Column(Float, nullable=False, comment="Dec (ICRS, degree)")
    epoch = Column(
        String, default="J2000.0", comment="Epoch (e.g., J2000.0, J2015.5, etc.)"
    )

    parallax = Column(Float, default=1.0e-7, comment="Parallax (mas)")
    parallax_error = Column(Float, comment="Standard error of parallax (mas)")
    pmra = Column(
        Float,
        default=0.0,
        comment="Proper motion in right ascension direction (mas/yr)",
    )
    pmra_error = Column(Float, comment="Standard error of pmra (mas/yr)")
    pmdec = Column(
        Float, default=0.0, comment="Proper motion in declination direction (mas/yr)"
    )
    pmdec_error = Column(Float, comment="Standard error of pmdec (mas/yr)")

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
        default=3,
        comment="target_type_id from the target_type table (must be 3 for FLUXSTD)",
    )

    input_catalog_id = Column(
        Integer,
        ForeignKey("input_catalog.input_catalog_id"),
        nullable=False,
        comment="input_catalog_id from the input_catalog table",
    )

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

    # filter_g = Column(String, comment="g-band filter (g_hsc, g_ps1, g_sdss, etc.)")
    # filter_r = Column(String, comment="r-band filter (r_hsc, r_ps1, r_sdss, etc.)")
    # filter_i = Column(String, comment="i-band filter (i_hsc, i_ps1, i_sdss, etc.)")
    # filter_z = Column(String, comment="z-band filter (z_hsc, z_ps1, z_sdss, etc.)")
    # filter_y = Column(String, comment="y-band filter (y_hsc, y_ps1, y_sdss, etc.)")
    # filter_j = Column(String, comment="j-band filter (j_mko, etc.)")

    filter_g = Column(
        String,
        ForeignKey("filter_name.filter_name"),
        comment="g-band filter (g_hsc, g_ps1, g_sdss, etc.)",
    )
    filter_r = Column(
        String,
        ForeignKey("filter_name.filter_name"),
        comment="r-band filter (r_hsc, r_ps1, r_sdss, etc.)",
    )
    filter_i = Column(
        String,
        ForeignKey("filter_name.filter_name"),
        comment="i-band filter (i_hsc, i_ps1, i_sdss, etc.)",
    )
    filter_z = Column(
        String,
        ForeignKey("filter_name.filter_name"),
        comment="z-band filter (z_hsc, z_ps1, z_sdss, etc.)",
    )
    filter_y = Column(
        String,
        ForeignKey("filter_name.filter_name"),
        comment="y-band filter (y_hsc, y_ps1, y_sdss, etc.)",
    )
    filter_j = Column(
        String,
        ForeignKey("filter_name.filter_name"),
        comment="j-band filter (j_mko, etc.)",
    )

    prob_f_star = Column(Float, comment="Probability of being an F-type star")
    flags_dist = Column(
        Boolean,
        comment="Distance uncertanty flag, True if parallax_error/parallax > 0.2",
    )
    flags_ebv = Column(
        Boolean,
        comment="E(B-V) uncertainty flag, True if E(B-V) uncertainty is greater than 20%",
    )

    # version string
    version = Column(
        String, nullable=False, comment="Version string of the F-star selection"
    )

    # timestamp
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # relations to other tables
    target_types = relationship(target_type, backref=backref("fluxstd"))
    input_catalogs = relationship(input_catalog, backref=backref("fluxstd"))

    # tried to make a relationship to filter_name table
    # ref: https://docs.sqlalchemy.org/en/14/orm/join_conditions.html
    filter_g_rels = relationship(filter_name, foreign_keys=[filter_g])
    filter_r_rels = relationship(filter_name, foreign_keys=[filter_r])
    filter_i_rels = relationship(filter_name, foreign_keys=[filter_i])
    filter_z_rels = relationship(filter_name, foreign_keys=[filter_z])
    filter_y_rels = relationship(filter_name, foreign_keys=[filter_y])
    filter_g_rels = relationship(filter_name, foreign_keys=[filter_j])

    def __init__(
        self,
        obj_id,
        ra,
        dec,
        epoch,
        parallax,
        parallax_error,
        pmra,
        pmra_error,
        pmdec,
        pmdec_error,
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
        psf_mag_error_g,
        psf_mag_error_r,
        psf_mag_error_i,
        psf_mag_error_z,
        psf_mag_error_y,
        psf_mag_error_j,
        psf_flux_g,
        psf_flux_r,
        psf_flux_i,
        psf_flux_z,
        psf_flux_y,
        psf_flux_j,
        psf_flux_error_g,
        psf_flux_error_r,
        psf_flux_error_i,
        psf_flux_error_z,
        psf_flux_error_y,
        psf_flux_error_j,
        filter_g,
        filter_r,
        filter_i,
        filter_z,
        filter_y,
        filter_j,
        prob_f_star,
        flags_dist,
        flags_ebv,
        version,
        created_at,
        updated_at,
    ):
        self.obj_id = obj_id
        self.ra = ra
        self.dec = dec
        self.epoch = epoch
        self.parallax = parallax
        self.parallax_error = parallax_error
        self.pmra = pmra
        self.pmra_error = pmra_error
        self.pmdec = pmdec
        self.pmdec_error = pmdec_error
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
        self.psf_mag_error_g = psf_mag_error_g
        self.psf_mag_error_r = psf_mag_error_r
        self.psf_mag_error_i = psf_mag_error_i
        self.psf_mag_error_z = psf_mag_error_z
        self.psf_mag_error_y = psf_mag_error_y
        self.psf_mag_error_j = psf_mag_error_j
        self.psf_flux_g = psf_flux_g
        self.psf_flux_r = psf_flux_r
        self.psf_flux_i = psf_flux_i
        self.psf_flux_z = psf_flux_z
        self.psf_flux_y = psf_flux_y
        self.psf_flux_j = psf_flux_j
        self.psf_flux_error_g = psf_flux_error_g
        self.psf_flux_error_r = psf_flux_error_r
        self.psf_flux_error_i = psf_flux_error_i
        self.psf_flux_error_z = psf_flux_error_z
        self.psf_flux_error_y = psf_flux_error_y
        self.psf_flux_error_j = psf_flux_error_j
        self.filter_g = filter_g
        self.filter_r = filter_r
        self.filter_i = filter_i
        self.filter_z = filter_z
        self.filter_y = filter_y
        self.filter_j = filter_j
        self.prob_f_star = prob_f_star
        self.flags_dist = flags_dist
        self.flags_ebv = flags_ebv
        self.version = version
        self.created_at = created_at
        self.updated_at = updated_at
