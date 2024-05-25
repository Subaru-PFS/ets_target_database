# `target` table

## Overview

The `target` table is used to store the information on flux standard stars.

## Columns

Here are the columns in the `target` table:

| Column Name            | Data Type | Description                                                                                      | Unit   | Required[^1] | Default |
|------------------------|-----------|--------------------------------------------------------------------------------------------------|--------|--------------|---------|
| target_id              | int64     | The unique identifier of the target.                                                             |        | \*           |         |
| proposal_id            | str       | `proposal_id` in the `proposal` table.                                                           |        | \*           |         |
| ob_code                | str       | The unique identifier to describe a combination of the object, observing mode, and exposure time |        | \*           |         |
| obj_id                 | int64     | Object identifier                                                                                |        | \*           |         |
| ra                     | float     | Right ascension of the object on ICRS at the reference epoch                                     | deg    | \*           |         |
| dec                    | float     | Declination of the object on ICRS at the reference epoch                                         | deg    | \*           |         |
| epoch                  | str       | Reference epoch                                                                                  |        |              | J2000.0 |
| parallax               | float     | Absolute stellar parallax of the source at the reference epoch ref_epoch                         | mas    |              | 1.0e-7  |
| pmra                   | float     | Proper motion in right ascension direction                                                       | mas/yr |              | 0       |
| pmdec                  | float     | Proper motion in declination direction                                                           | mas/yr |              | 0       |
| tract                  | int       | Tract defined by, e.g., the HSC pipeline                                                         |        |              |         |
| patch                  | int       | Patch defined by, e.g., the HSC pipeline                                                         |        |              |         |
| target_type_id         | int       | `target_type_id` in the `target_type` table                                                      |        |              |         |
| input_catalog_id       | int       | `input_catalog_id` in the `input_catalog` table                                                  |        |              |         |
| fiber_mag_g            | float     | (Obsolete) Fiber magnitude in _g_-band                                                           | AB mag |              |         |
| fiber_mag_r            | float     | (Obsolete) Fiber magnitude in _r_-band                                                           | AB mag |              |         |
| fiber_mag_i            | float     | (Obsolete) Fiber magnitude in _i_-band                                                           | AB mag |              |         |
| fiber_mag_z            | float     | (Obsolete) Fiber magnitude in _z_-band                                                           | AB mag |              |         |
| fiber_mag_y            | float     | (Obsolete) Fiber magnitude in _y_-band                                                           | AB mag |              |         |
| fiber_mag_j            | float     | (Obsolete) Fiber magnitude in _j_-band                                                           | AB mag |              |         |
| psf_mag_g              | float     | (Obsolete) PSF magnitude in _g_-band                                                             | AB mag |              |         |
| psf_mag_r              | float     | (Obsolete) PSF magnitude in _r_-band                                                             | AB mag |              |         |
| psf_mag_i              | float     | (Obsolete) PSF magnitude in _i_-band                                                             | AB mag |              |         |
| psf_mag_z              | float     | (Obsolete) PSF magnitude in _z_-band                                                             | AB mag |              |         |
| psf_mag_y              | float     | (Obsolete) PSF magnitude in _y_-band                                                             | AB mag |              |         |
| psf_mag_j              | float     | (Obsolete) PSF magnitude in _j_-band                                                             | AB mag |              |         |
| psf_mag_error_g        | float     | (Obsolete) Error in PSF magnitude in _g_-band                                                    | AB mag |              |         |
| psf_mag_error_r        | float     | (Obsolete) Error in PSF magnitude in _r_-band                                                    | AB mag |              |         |
| psf_mag_error_i        | float     | (Obsolete) Error in PSF magnitude in _i_-band                                                    | AB mag |              |         |
| psf_mag_error_z        | float     | (Obsolete) Error in PSF magnitude in _z_-band                                                    | AB mag |              |         |
| psf_mag_error_y        | float     | (Obsolete) Error in PSF magnitude in _y_-band                                                    | AB mag |              |         |
| psf_mag_error_j        | float     | (Obsolete) Error in PSF magnitude in _j_-band                                                    | AB mag |              |         |
| psf_flux_g             | float     | PSF flux in _g_-band                                                                             | nJy    | (\*)         |         |
| psf_flux_r             | float     | PSF flux in _r_-band                                                                             | nJy    | (\*)         |         |
| psf_flux_i             | float     | PSF flux in _i_-band                                                                             | nJy    | (\*)         |         |
| psf_flux_z             | float     | PSF flux in _z_-band                                                                             | nJy    | (\*)         |         |
| psf_flux_y             | float     | PSF flux in _y_-band                                                                             | nJy    | (\*)         |         |
| psf_flux_j             | float     | PSF flux in _j_-band                                                                             | nJy    | (\*)         |         |
| psf_flux_error_g       | float     | Error in PSF flux in _g_-band                                                                    | nJy    | (\*)         |         |
| psf_flux_error_r       | float     | Error in PSF flux in _r_-band                                                                    | nJy    | (\*)         |         |
| psf_flux_error_i       | float     | Error in PSF flux in _i_-band                                                                    | nJy    | (\*)         |         |
| psf_flux_error_z       | float     | Error in PSF flux in _z_-band                                                                    | nJy    | (\*)         |         |
| psf_flux_error_y       | float     | Error in PSF flux in _y_-band                                                                    | nJy    | (\*)         |         |
| psf_flux_error_j       | float     | Error in PSF flux in _j_-band                                                                    | nJy    | (\*)         |         |
| filter_g               | str       | Photometric band used to measure the PSF flux in _g_-band                                        |        | (\*)         |         |
| filter_r               | str       | Photometric band used to measure the PSF flux in _r_-band                                        |        | (\*)         |         |
| filter_i               | str       | Photometric band used to measure the PSF flux in _i_-band                                        |        | (\*)         |         |
| filter_z               | str       | Photometric band used to measure the PSF flux in _z_-band                                        |        | (\*)         |         |
| filter_y               | str       | Photometric band used to measure the PSF flux in _y_-band                                        |        | (\*)         |         |
| filter_j               | str       | Photometric band used to measure the PSF flux in _j_-band                                        |        | (\*)         |         |
| priority               | float     | Priority of the target for observation.                                                          |        |              | 1.0     |
| effective_exptime      | float     | Effective exposure time required to complete the target                                          | s      | \*           |         |
| single_exptime         | float     | Individual exposure time                                                                         | s      |              | 900     |
| is_medium_resolution   | bool      | `True` if the target is observed with the medium-resolution mode                                 |        |              | False   |
| qa_relative_throughput | float     | Quality assurance metric for relative throughput.                                                |        |              | 1.0     |
| qa_relative_noise      | float     | Quality assurance metric for relative noise.                                                     |        |              | 1.0     |
| qa_reference_lambda    | float     | Quality assurance reference wavelength                                                           | nm     |              |         |
| is_cluster             | bool      | (Obsolete) `True` if the target is part of a cluster.                                            |        |              | False   |
| created_at             | datetime  | The date and time in UTC when the record was created.                                            |        |              |         |
| updated_at             | datetime  | The date and time in UTC when the record was last updated.                                       |        |              |         |

[^1]: Required when inserted by using the [CLI tool](../reference/cli.md) or equivalent functions.

## Unique constraints

- `target_id` is set as the primary key with auto-increment.
- Set of `(proposal_id, ob_code, input_catalog_id, obj_id, is_medium_resolution)` must be unique.
- Set of `(proposal_id, ob_code)` must be unique.

## Foreign keys

- `proposal_id` references the `proposal_id` in the `proposal` table.
- `target_type_id` references the `target_type_id` in the `target_type` table.
- `input_catalog_id` references the `input_catalog_id` in the `input_catalog` table.
- `filter_{g,r,i,z,y,j}` references the `filter_name` in the `filter_name` table.

## Notes

At least one photometric flux column must be filled for the technical review. See [the PFS Target Uploader documentation](https://pfs-etc.naoj.hawaii.edu/uploader/doc/inputs.html#filters) for the list of available filters allowed for each column.
