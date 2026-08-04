#!/usr/bin/env python

import numpy as np
import pandas as pd
import pytest

from targetdb.utils import add_backref_values, check_filter_flux_consistency


def test_add_backref_values_normalizes_missing_filter_values_for_fluxstd():
    # filter_g/filter_i are ForeignKey columns to filter_name.filter_name.
    # Empty entries in the input (NaN from a masked ecsv column, or an empty
    # string from a CSV column read with keep_default_na=False) must be
    # normalized to None, otherwise the literal "NaN"/"" is sent to the
    # database and violates the foreign key constraint. This must hold for
    # any table that goes through add_backref_values (fluxstd, sky,
    # user_pointing, and target when not coming from the uploader), not just
    # for the uploader-specific target code path.
    df = pd.DataFrame(
        {
            "input_catalog_id": [1, 1, 1],
            "filter_g": ["g_sdss", np.nan, ""],
            "filter_i": ["i_sdss", "i_sdss", "i_sdss"],
        }
    )

    df_out = add_backref_values(df, db=None, table="fluxstd")

    assert df_out["filter_g"].tolist() == ["g_sdss", None, None]
    assert df_out["filter_i"].tolist() == ["i_sdss", "i_sdss", "i_sdss"]

    # None must round-trip as None (not float NaN) through to_dict, since
    # that is what actually gets handed to bulk_insert_mappings.
    records = df_out.to_dict(orient="records")
    assert records[1]["filter_g"] is None
    assert records[2]["filter_g"] is None


def test_add_backref_values_raises_when_flux_present_without_filter():
    # A flux value is meaningless without knowing which filter it was
    # measured through, so filter_g missing while psf_flux_g is set must be
    # rejected rather than silently inserted.
    df = pd.DataFrame(
        {
            "input_catalog_id": [1, 1],
            "filter_g": ["g_sdss", np.nan],
            "psf_flux_g": [123.4, 56.7],
        }
    )

    with pytest.raises(ValueError, match="psf_flux_g"):
        add_backref_values(df, db=None, table="fluxstd")


@pytest.mark.parametrize(
    "flux_col", ["flux_g", "psf_flux_g", "total_flux_g", "psf_flux_error_g"]
)
def test_check_filter_flux_consistency_raises_for_each_flux_column_kind(flux_col):
    df = pd.DataFrame({"filter_g": [None], flux_col: [1.0]})

    with pytest.raises(ValueError, match=flux_col):
        check_filter_flux_consistency(df)


def test_check_filter_flux_consistency_allows_missing_filter_and_flux():
    df = pd.DataFrame({"filter_g": [None, "g_sdss"], "psf_flux_g": [np.nan, 1.0]})

    # should not raise
    check_filter_flux_consistency(df)
