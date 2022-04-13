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
from . import target


class cluster(Base):
    __tablename__ = "cluster"

    cluster_id = Column(
        BigInteger,
        primary_key=True,
        unique=False,
        autoincrement=False,
        comment="Unique identifier of clusters found at duplication checking",
    )
    target_id = Column(BigInteger, ForeignKey("target.target_id"))
    n_targets = Column(Integer, comment="Number of targets in the cluster")

    # NOTE: ra_cluster and dec_cluster are inserted into the target table and become redundant...
    ra_cluster = Column(
        Float, comment="Mean RA of targets in the cluster (ICRS, degree)"
    )
    dec_cluster = Column(
        Float, comment="Mean Dec of targets in the cluster (ICRS, degree)"
    )

    d_ra = Column(Float, comment="RA(target) - RA(cluster) (degree)")
    d_dec = Column(Float, comment="Dec(target) - Dec(cluster) (degree)")

    input_catalog_id = Column(
        Integer,
        ForeignKey("input_catalog.input_catalog_id"),
        comment="Input catalog ID from the input_catalog table",
    )

    created_at = Column(DateTime, comment="UTC")
    updated_at = Column(DateTime, comment="UTC")

    targets = relation(target, backref=backref("cluster"))
    input_catalogs = relation(input_catalog, backref=backref("target"))

    def __init__(
        self,
        cluster_id,
        target_id,
        n_targets,
        ra_cluster,
        dec_cluster,
        d_ra,
        d_dec,
        input_catalog_id,
        created_at,
        updated_at,
    ):
        self.cluster_id = cluster_id
        self.target_id = target_id
        self.n_targets = n_targets
        self.ra_cluster = ra_cluster
        self.dec_cluster = dec_cluster
        self.d_ra = d_ra
        self.d_dec = d_dec
        self.input_catalog_id = input_catalog_id
        self.created_at = created_at
        self.updated_at = updated_at
