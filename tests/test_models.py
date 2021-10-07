#!/usr/bin/env python

# ref: https://github.com/Subaru-PFS/spt_operational_database/blob/master/tests/test_models.py

from sqlalchemy.orm import aliased
from targetdb import models


def test_relations_consistency():
    # get the first model
    model = next(iter(models.Base.registry.mappers))

    # aliased involves some consistency checks
    aliased(model)
