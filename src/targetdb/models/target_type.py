#!/usr/bin/env python

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
)

# from sqlalchemy.exc import OperationalError
# from sqlalchemy.orm import backref, relation
from . import Base, comment_created_at, comment_updated_at


class target_type(Base):
    #
    # https://github.com/Subaru-PFS/datamodel/blob/master/datamodel.txt
    #
    # The 'targetType' in the DESIGN table is an enumerated type, with values:
    #   SCIENCE = 1: the fiber is intended to be on a science target.
    #   SKY = 2: the fiber is intended to be on blank sky, and used for sky subtraction.
    #   FLUXSTD = 3: the fiber is intended to be on a flux standard, and used for flux calibration.
    #   UNASSIGNED = 4: the fiber is not targeted on anything in particular.
    #   ENGINEERING = 5: the fiber is an engineering fiber.
    #   SUNSS_IMAGING = 6: the fiber goes to the SuNSS imaging leg
    #   SUNSS_DIFFUSE = 7: the fiber goes to the SuNSS diffuse leg
    #

    __tablename__ = "target_type"

    target_type_id = Column(
        Integer,
        primary_key=True,
        unique=True,
        autoincrement=False,
        comment="Unique identifier for target types",
    )
    target_type_name = Column(
        String,
        nullable=False,
        comment="Name for the target type.",
    )
    target_type_description = Column(String, comment="Description of the target type")
    created_at = Column(DateTime, comment=comment_created_at)
    updated_at = Column(DateTime, comment=comment_updated_at)

    def __init__(
        self,
        target_type_id,
        target_type_name,
        target_type_description,
        created_at,
        updated_at,
    ):
        self.target_type_id = target_type_id
        self.target_type_name = target_type_name
        self.target_type_description = target_type_description
        self.created_at = created_at
        self.updated_at = updated_at


#
