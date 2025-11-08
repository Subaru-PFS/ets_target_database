#!/usr/bin/env python3

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import backref, relationship

from . import (
    Base,
    comment_created_at,
    comment_updated_at,
    partner,
    proposal_category,
    # proposal_grade,
    utcnow,
)


class proposal(Base):
    """Defines a scientific observing proposal."""

    __tablename__ = "proposal"
    # __table_args__ = (UniqueConstraint("proposal_id", "group_id"), {})

    # Create index for grade column
    __table_args__ = (Index("idx_proposal_grade", "grade"), {})

    proposal_id = Column(
        String,
        primary_key=True,
        autoincrement=False,
        comment="Unique identifier for proposal (e.g, S21B-OT06)",
    )
    group_id = Column(
        String,
        # primary_key=True,
        # unique=True,
        nullable=False,
        autoincrement=False,
        comment="Group ID in STARS (e.g., o21195)",
    )
    pi_first_name = Column(String, default="", comment="PI's first name")
    pi_last_name = Column(String, nullable=False, comment="PI's last name")
    pi_middle_name = Column(String, default="", comment="PI's middle name")
    rank = Column(Float, nullable=False, comment="TAC score")
    grade = Column(
        String,
        # ForeignKey("proposal_grade.name"),
        nullable=False,
        comment="TAC grade (A/B/C/F and N/A)",
    )
    allocated_time_total = Column(
        Float, default=0.0, comment="Total fiberhours allocated by TAC (hour)"
    )
    allocated_time_lr = Column(
        Float,
        default=0.0,
        comment="Total fiberhours for the low-resolution mode allocated by TAC (hour)",
    )
    allocated_time_mr = Column(
        Float,
        default=0.0,
        comment="Total fiberhours for the medium-resolution mode allocated by TAC (hour)",
    )
    proposal_category_id = Column(
        Integer, ForeignKey("proposal_category.proposal_category_id")
    )

    partner_id = Column(
        Integer,
        ForeignKey("partner.partner_id"),
    )

    is_too = Column(Boolean, default=False, comment="True when the proposal is ToO")

    created_at = Column(DateTime, comment=comment_created_at, server_default=utcnow())
    updated_at = Column(DateTime, comment=comment_updated_at, onupdate=utcnow())

    proposal_categories = relationship(proposal_category, backref=backref("proposal"))
    # proposal_grades = relationship("proposal_grade", back_populates="proposal")

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
        partner_id,
        is_too,
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
        self.partner_id = partner_id
        self.is_too = is_too
        self.created_at = created_at
        self.updated_at = updated_at
