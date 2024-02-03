#!/usr/bin/env python3

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import backref, relationship

from . import Base, proposal_category


class proposal(Base):
    """Defines a scientific observing proposal."""

    __tablename__ = "proposal"
    # __table_args__ = (UniqueConstraint("proposal_id", "group_id"), {})

    proposal_id = Column(
        String,
        primary_key=True,
        unique=True,
        autoincrement=False,
        comment="Unique identifier for proposal (e.g, S21B-OT06?)",
    )
    group_id = Column(
        String,
        # primary_key=True,
        # unique=True,
        autoincrement=False,
        comment="Group ID in STARS (e.g., o21195?)",
    )
    pi_first_name = Column(String, comment="PI's first name")
    pi_last_name = Column(String, comment="PI's last name")
    pi_middle_name = Column(String, comment="PI's middle name")
    rank = Column(Float, comment="TAC score")
    grade = Column(String, comment="TAC grade (A/B/C/F in the case of HSC queue)")
    allocated_time_total = Column(
        Float, comment="Total fiberhours allocated by TAC (hour)"
    )
    allocated_time_lr = Column(
        Float,
        comment="Total fiberhours for the low-resolution mode allocated by TAC (hour)",
    )
    allocated_time_mr = Column(
        Float,
        comment="Total fiberhours for the medium-resolution mode allocated by TAC (hour)",
    )
    proposal_category_id = Column(
        Integer, ForeignKey("proposal_category.proposal_category_id")
    )

    created_at = Column(
        DateTime, comment="Creation time [YYYY-MM-DDThh:mm:ss] (UTC or HST?)"
    )
    updated_at = Column(
        DateTime, comment="Update time [YYYY-MM-DDThh:mm:ss] (UTC or HST?)"
    )

    proposal_categories = relationship(proposal_category, backref=backref("proposal"))

    def __init__(
        self,
        proposal_id,
        group_id,
        pi_first_name,
        pi_last_name,
        pi_middle_name,
        rank,
        grade,
        allocated_time_total,
        allocated_time_lr,
        allocated_time_mr,
        proposal_category_id,
        created_at,
        updated_at,
    ):
        self.proposal_id = proposal_id
        self.group_id = group_id
        self.pi_first_name = pi_first_name
        self.pi_last_name = pi_last_name
        self.pi_middle_name = pi_middle_name
        self.rank = rank
        self.grade = grade
        self.allocated_time_total = allocated_time_total
        self.allocated_time_lr = allocated_time_lr
        self.allocated_time_mr = allocated_time_mr
        self.proposal_category_id = proposal_category_id
        self.created_at = created_at
        self.updated_at = updated_at
