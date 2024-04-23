# `fluxstd` table

## Overview

The `fluxstd` table is used to store the information on flux standard stars.

## Columns

Here are the columns in the `fluxstd` table:

| Column Name        | Data Type | Description                                                                                                 | Unit   | Required | Default |
| ------------------ | --------- | ----------------------------------------------------------------------------------------------------------- | ------ | -------- | ------- |
| fluxstd_id         | int64     | The unique identifier of the record.                                                                        |        |          |         |
| obj_id             | int64     | Object identifier (e.g., `source_id` in the Gaia catalog)                                                   |        | \*       |         |
| ra                 | float     | Right ascension of the object on ICRS at the reference epoch                                                | deg    | \*       |         |
| dec                | float     | Declination of the object on ICRS at the reference epoch                                                    | deg    | \*       |         |
| epoch              | str       | Reference epoch                                                                                             |        |          | J2000.0 |
| parallax           | float     | Absolute stellar parallax of the source at the reference epoch ref_epoch                                    | mas    |          | 1.0e-7  |
| parallax_error     | float     | Standard error of the stellar parallax at the reference epoch ref_epoch                                     | mas    |          |         |
| pmra               | float     | Proper motion in right ascension direction                                                                  | mas/yr |          | 0       |
| pmra_error         | float     | Standard error in pmra                                                                                      | mas/yr |          |         |
| pmdec              | float     | Proper motion in declination direction                                                                      | mas/yr |          | 0       |
| pmdec_error        | float     | Standard error in pmdec                                                                                     | mas/yr |          |         |
| tract              | int       | Tract defined by, e.g., the HSC pipeline                                                                    |        |          |         |
| patch              | int       | Patch defined by, e.g., the HSC pipeline                                                                    |        |          |         |
| target_type_id     | int       | `target_type_id` in the `target_type` table (it is `3` for `FLUXSTD`)                                       |        |          | 3       |
| input_catalog_id   | int       | `input_catalog_id` in the `input_catalog` table (should be in `[3000, 4999]`)                               |        |          |         |
| psf_mag_g          | float     | PSF magnitude in _g_-band                                                                                   | AB mag |          |         |
| psf_mag_r          | float     | PSF magnitude in _r_-band                                                                                   | AB mag |          |         |
| psf_mag_i          | float     | PSF magnitude in _i_-band                                                                                   | AB mag |          |         |
| psf_mag_z          | float     | PSF magnitude in _z_-band                                                                                   | AB mag |          |         |
| psf_mag_y          | float     | PSF magnitude in _y_-band                                                                                   | AB mag |          |         |
| psf_mag_j          | float     | PSF magnitude in _j_-band                                                                                   | AB mag |          |         |
| psf_mag_error_g    | float     | Error in PSF magnitude in _g_-band                                                                          | AB mag |          |         |
| psf_mag_error_r    | float     | Error in PSF magnitude in _r_-band                                                                          | AB mag |          |         |
| psf_mag_error_i    | float     | Error in PSF magnitude in _i_-band                                                                          | AB mag |          |         |
| psf_mag_error_z    | float     | Error in PSF magnitude in _z_-band                                                                          | AB mag |          |         |
| psf_mag_error_y    | float     | Error in PSF magnitude in _y_-band                                                                          | AB mag |          |         |
| psf_mag_error_j    | float     | Error in PSF magnitude in _j_-band                                                                          | AB mag |          |         |
| psf_flux_g         | float     | PSF flux in _g_-band                                                                                        | nJy    | (\*)     |         |
| psf_flux_r         | float     | PSF flux in _r_-band                                                                                        | nJy    | (\*)     |         |
| psf_flux_i         | float     | PSF flux in _i_-band                                                                                        | nJy    | (\*)     |         |
| psf_flux_z         | float     | PSF flux in _z_-band                                                                                        | nJy    | (\*)     |         |
| psf_flux_y         | float     | PSF flux in _y_-band                                                                                        | nJy    | (\*)     |         |
| psf_flux_j         | float     | PSF flux in _j_-band                                                                                        | nJy    | (\*)     |         |
| psf_flux_error_g   | float     | Error in PSF flux in _g_-band                                                                               | nJy    | (\*)     |         |
| psf_flux_error_r   | float     | Error in PSF flux in _r_-band                                                                               | nJy    | (\*)     |         |
| psf_flux_error_i   | float     | Error in PSF flux in _i_-band                                                                               | nJy    | (\*)     |         |
| psf_flux_error_z   | float     | Error in PSF flux in _z_-band                                                                               | nJy    | (\*)     |         |
| psf_flux_error_y   | float     | Error in PSF flux in _y_-band                                                                               | nJy    | (\*)     |         |
| psf_flux_error_j   | float     | Error in PSF flux in _j_-band                                                                               | nJy    | (\*)     |         |
| filter_g           | str       | Photometric band used to measure the PSF flux in _g_-band                                                   |        | (\*)     |         |
| filter_r           | str       | Photometric band used to measure the PSF flux in _r_-band                                                   |        | (\*)     |         |
| filter_i           | str       | Photometric band used to measure the PSF flux in _i_-band                                                   |        | (\*)     |         |
| filter_z           | str       | Photometric band used to measure the PSF flux in _z_-band                                                   |        | (\*)     |         |
| filter_y           | str       | Photometric band used to measure the PSF flux in _y_-band                                                   |        | (\*)     |         |
| filter_j           | str       | Photometric band used to measure the PSF flux in _j_-band                                                   |        | (\*)     |         |
| prob_f_star        | float     | Probability to be F-type star (0 is less likely, 1 is likely)                                               |        | \*       |         |
| flags_dist         | bool      | (Obsolete) Distance uncertanty flag, `True` if parallax_error/parallax > 0.2                                |        |          |         |
| flags_ebv          | bool      | (Obsolete) E(B-V) uncertainty flag, `True` if E(B-V) uncertainty is greater than 20%                        |        |          |         |
| teff_brutus        | float     | Effective temperature of the star estimated by Brutus                                                       | K      | \*       |         |
| teff_brutus_low    | float     | The 16-percentile value of the posterior distribution of the teff_brutus                                    | K      | \*       |         |
| teff_brutus_high   | float     | The 84-percentile value of the posterior distribution of the teff_brutus                                    | K      | \*       |         |
| logg_brutus        | float     | Surface gravity of the star estimated by Brutus                                                             | dex    | \*       |         |
| logg_brutus_low    | float     | The 16-percentile value of the posterior distribution of the logg_brutus                                    | dex    | \*       |         |
| logg_brutus_high   | float     | The 84-percentile value of the posterior distribution of the logg_brutus                                    | dex    | \*       |         |
| teff_gspphot       | float     | Effective temperature from GSP-Phot Aeneas best library using BP/RP spectra                                 | K      | \*       |         |
| teff_gspphot_lower | float     | Lower confidence level (16%) of effective temperature from GSP-Phot Aeneas best library using BP/RP spectra | K      | \*       |         |
| teff_gspphot_upper | float     | Upper confidence level (84%) of effective temperature from GSP-Phot Aeneas best library using BP/RP spectra | K      | \*       |         |
| is_fstar_gaia      | bool      | `True` if teff_gspphot is between 6000K and 7500K                                                           |        | \*       |         |
| version            | str       | The version of the F-star candidate catalog                                                                 |        | \*       |         |
| created_at         | datetime  | The date and time in UTC when the record was created.                                                       |        |          |         |
| updated_at         | datetime  | The date and time in UTC when the record was last updated.                                                  |        |          |         |

[^1]: Required when inserted by using the [CLI tool](../reference/cli.md) or equivalent functions.

## Unique constraints

- `fluxstd_id` is set as the primary key with auto-increment.
- Set of `(obj_id, input_catalog_id, version)` must be unique.

## Foreign keys

- `target_type_id` references the `target_type_id` in the `target_type` table.
- `input_catalog_id` references the `input_catalog_id` in the `input_catalog` table.
- `filter_{g,r,i,z,y,j}` references the `filter_name` in the `filter_name` table.

## Notes

Photometric flux columns must be filled as much as possible for the best calibration. See [the PFS Target Uploader documentation](https://pfs-etc.naoj.hawaii.edu/uploader/doc/inputs.html#filters) for the list of available filters allowed for each column.

Photometric magnitudes are optional. Fluxes are more important.

Columns related to the Brutus calculation (`teff_brutus`, `teff_brutus_low`, `teff_brutus_high`, `logg_brutus`, `logg_brutus_low`, `logg_brutus_high`, and `prob_f_star`) are required when PS1 photometry is available and computation is possible.

## Reference

More details on the flux standard star data can be found in the [doc/catalog.md](https://github.com/Subaru-PFS/drp_fstar_photo/blob/main/doc/catalog.md) file in the [drp_fstar_photo](https://github.com/Subaru-PFS/drp_fstar_photo/) repository.
