#!/usr/bin/env python

# ref: https://github.com/Subaru-PFS/spt_operational_database/blob/master/tests/test_models.py

import pytest
from sqlalchemy.orm import aliased

from targetdb import models


def test_relations_consistency():
    # get the first model
    model = next(iter(models.Base.registry.mappers))

    # aliased involves some consistency checks
    aliased(model)


def _scalar_default_columns():
    for mapper in models.Base.registry.mappers:
        for column in mapper.local_table.columns:
            if column.default is not None and column.default.is_scalar:
                yield column


def _server_default_value(column):
    """Read a with_default() server default back as a Python value."""
    arg = column.server_default.arg
    if isinstance(arg, str):
        return arg
    if arg.text in ("true", "false"):
        return arg.text == "true"
    return float(arg.text)


def test_scalar_defaults_have_matching_server_defaults():
    checked = 0
    for column in _scalar_default_columns():
        value = column.default.arg
        if value == "":
            # COPY stores "" as NULL, so these deliberately have no server default.
            assert column.server_default is None, column
            continue
        assert column.server_default is not None, f"{column} lacks a server default"
        server_value = _server_default_value(column)
        # == alone would let a boolean column pass with a DEFAULT of 1 or 0.
        assert isinstance(server_value, bool) == isinstance(value, bool), column
        assert server_value == value, column
        checked += 1
    assert checked == 27


@pytest.mark.parametrize("value", ["", None, [1]])
def test_with_default_rejects_values_without_a_server_default(value):
    with pytest.raises(ValueError):
        models.with_default(value)
