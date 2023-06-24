# Input Target List

## Inputs from observers

### Proposal-related information

The following information is required for each _proposal_.

| name          | type | description                    | required | default |
|---------------|------|--------------------------------|----------|---------|
| `proposal_id` | str  | Proposal ID (e.g., S22A-QN001) | *        |         |


### Target-related information

The following information is required for each _target_.

| name                     | type  | description                                          | unit          | required | default |
|--------------------------|-------|------------------------------------------------------|---------------|----------|---------|
| `ob_code`                | str   | Code for a target entry, unique in a proposal        |               | *        |         |
| `obj_id`                 | int64 | Object ID                                            |               | *        |         |
| `ra`                     | float | RA (ICRS)                                            | degree        | *        |         |
| `dec`                    | float | Dec (ICRS)                                           | degree        | *        |         |
| `epoch`                  | str   | Epoch (e.g., J2000.0, J2016.0)                       |               |          | J2000.0 |
| `parallax`               | float | Parallax                                             | mas           |          | 1e-7    |
| `pmra`                   | float | Proper motion in right ascension direction           | mas/yr        |          | 0.0     |
| `pmdec`                  | float | Proper motion in declination direction               | mas/yr        |          | 0.0     |
| `tract`                  | int   | Same definition as HSC-SSP (TBD)                     |               |          | Null    |
| `patch`                  | int   | Same definition as HSC-SSP (TBD)                     |               |          | Null    |
| `input_catalog_name`     | str   | Input catalog name (e.g., `hscssp_pdr3_wide`)        |               |          | (TBD)   |
| `priority`               | float | Priority defined by the observer within the proposal |               | *        |         |
| `effective_exptime `     | float | Requested effective exposure time                    |               | *        |         |
| `filter_g`               | str   | g-band filter                                        |               | s        | Null    |
| `filter_r`               | str   | r-band filter                                        |               |          | Null    |
| `filter_i`               | str   | i-band filter                                        |               |          | Null    |
| `filter_z`               | str   | z-band filter                                        |               |          | Null    |
| `filter_y`               | str   | y-band filter                                        |               |          | Null    |
| `filter_j`               | str   | J band filter                                        |               |          | Null    |
| `fiber_mag_g `           | float | g-band magnitude within a fiber                      | AB mag        |          | Null    |
| `fiber_mag_r `           | float | r-band magnitude within a fiber                      | AB mag        |          | Null    |
| `fiber_mag_i `           | float | i-band magnitude within a fiber                      | AB mag        |          | Null    |
| `fiber_mag_z `           | float | z-band magnitude within a fiber                      | AB mag        |          | Null    |
| `fiber_mag_y `           | float | y-band magnitude within a fiber                      | AB mag        |          | Null    |
| `fiber_mag_j `           | float | J band magnitude within a fiber                      | AB mag        |          | Null    |
| `psf_mag_g `             | float | g-band PSF magnitude                                 | AB mag        |          | Null    |
| `psf_mag_r `             | float | r-band PSF magnitude                                 | AB mag        |          | Null    |
| `psf_mag_i `             | float | i-band PSF magnitude                                 | AB mag        |          | Null    |
| `psf_mag_z `             | float | z-band PSF magnitude                                 | AB mag        |          | Null    |
| `psf_mag_y `             | float | y-band PSF magnitude                                 | AB mag        |          | Null    |
| `psf_mag_j `             | float | J band PSF magnitude                                 | AB mag        |          | Null    |
| `psf_flux_g`             | float | g-band PSF flux                                      | nJy           |          | Null    |
| `psf_flux_r`             | float | r-band PSF flux                                      | nJy           |          | Null    |
| `psf_flux_i`             | float | i-band PSF flux                                      | nJy           |          | Null    |
| `psf_flux_z`             | float | z-band PSF flux                                      | nJy           |          | Null    |
| `psf_flux_y`             | float | y-band PSF flux                                      | nJy           |          | Null    |
| `psf_flux_j`             | float | J band PSF flux                                      | nJy           |          | Null    |
| `psf_mag_error_g `       | float | Error in g-band PSF magnitude                        | AB mag        |          | Null    |
| `psf_mag_error_r `       | float | Error in r-band PSF magnitude                        | AB mag        |          | Null    |
| `psf_mag_error_i `       | float | Error in i-band PSF magnitude                        | AB mag        |          | Null    |
| `psf_mag_error_z `       | float | Error in z-band PSF magnitude                        | AB mag        |          | Null    |
| `psf_mag_error_y `       | float | Error in y-band PSF magnitude                        | AB mag        |          | Null    |
| `psf_mag_error_j `       | float | Error in J band PSF magnitude                        | AB mag        |          | Null    |
| `psf_flux_error_g`       | float | Error in g-band PSF flux                             | nJy           |          | Null    |
| `psf_flux_error_r`       | float | Error in r-band PSF flux                             | nJy           |          | Null    |
| `psf_flux_error_i`       | float | Error in i-band PSF flux                             | nJy           |          | Null    |
| `psf_flux_error_z`       | float | Error in z-band PSF flux                             | nJy           |          | Null    |
| `psf_flux_error_y`       | float | Error in y-band PSF flux                             | nJy           |          | Null    |
| `psf_flux_error_j`       | float | Error in J band PSF flux                             | nJy           |          | Null    |
| `is_medium_resolution`   | bool  | `True` if the medium resolution mode is requested    |               |          | `False` |
| `qa_relative_throughput` | float | Relative throughput to the reference value           |               |          | 1.0     |
| `qa_relative_noise `     | float | Relative noise to the reference value                |               |          | 1.0     |
| `qa_reference_lambda `   | float | Reference wavelength for QA (angstrom or nm?)        | &#8491; or nm |          | (TBD)   |


#### Notes

##### `tract`, `patch`

If the look-up `tract` and `patch` from the coordinates is not expensive, it is possible for the observatory to automatically fill these information without asking inputs from observers.

##### `input_catalog_name`

Currently, the following catalogs are considered, and the list can be easily expanded.

```
input_catalog_id,input_catalog_name,input_catalog_description
0,"simulated","simulated catalog"
1,"gaia_dr1","Gaia Data Release 1"
2,"gaia_dr2","Gaia Data Release 2"
3,"gaia_edr3","Gaia Early Data Release 3"
4,"gaia_dr3","Gaia Data Release 3"
5,"hscssp_pdr1_wide","HSC-SSP Public Data Release 1 (Wide)"
6,"hscssp_pdr1_dud","HSC-SSP Public Data Release 1 (Deep+UltraDeep)"
7,"hscssp_pdr2_wide","HSC-SSP Public Data Release 2 (Wide)"
8,"hscssp_pdr2_dud","HSC-SSP Public Data Release 2 (Deep+UltraDeep)"
9,"hscssp_pdr3_wide","HSC-SSP Public Data Release 3 (Wide)"
10,"hscssp_pdr3_dud","HSC-SSP Public Data Release 3 (Deep+UltraDeep)"
11,"hscssp_pdr4_wide","HSC-SSP Public Data Release 4 (Wide)"
12,"hscssp_pdr4_dud","HSC-SSP Public Data Release 4 (Deep+UltraDeep)"
```

For individual proposals, either assigning a new `input_catalog_id` (e.g., s22a-qn0001_00001 with `input_catalog_id=10001`) or allow them to use pre-assigned `input_catalog` should work. Exact policy is still under discussion.


## Inputs from the observatory

In the background, the observatory needs to populate the rest of tables such as `proposal_category`, `proposal`, `target_type`, `input_catalog`, and `fluxstd`.


### `proposal_category`

Currently, `proposal_category` contains the following information.

```
proposal_category_id,proposal_category_name,proposal_category_description
1,"openuse","Subaru openuse proposal"
2,"keck","Subaru/Keck time exchange proposal"
3,"gemini","Subaru/Gemini time exchange proposal"
4,"uh","University of Hawaii proposal"
```

### `target_type`

Currently, `target_type` contains teh following entries as defined by the [datamodel](https://github.com/Subaru-PFS/datamodel/blob/master/datamodel.txt).

```
target_type_id,target_type_name,target_type_description
1,"SCIENCE","the fiber is intended to be on a science target"
2,"SKY","the fiber is intended to be on blank sky, and used for sky subtraction"
3,"FLUXSTD","the fiber is intended to be on a flux standard, and used for flux calibration"
4,"UNASSIGNED","the fiber is not targeted on anything in particular"
5,"ENGINEERING","the fiber is an engineering fiber"
6,"SUNSS_IMAGING","the fiber goes to the SuNSS imaging leg"
7,"SUNSS_DIFFUSE","the fiber goes to the SuNSS diffuse leg"
```

### `proposal`

The `proposal` table's schema is the following.


| name                 | type     | primary_key | autoincrement | comment                                          |
|:---------------------|:---------|:------------|:--------------|:-------------------------------------------------|
| proposal_id          | VARCHAR  | True        | False         | Unique identifier for proposal (e.g, S21B-OT06?) |
| group_id             | VARCHAR  | False       | False         | Group ID in STARS (e.g., o21195?)                |
| pi_first_name        | VARCHAR  | False       | False         | PI's first name                                  |
| pi_last_name         | VARCHAR  | False       | False         | PI's last name                                   |
| pi_middle_name       | VARCHAR  | False       | False         | PI's middle name                                 |
| rank                 | FLOAT    | False       | False         | TAC score                                        |
| grade                | VARCHAR  | False       | False         | TAC grade (A/B/C/F in the case of HSC queue)     |
| allocated_time       | FLOAT    | False       | False         | Total fiberhours allocated by TAC (hour)         |
| proposal_category_id | INTEGER  | False       | False         |                                                  |
| created_at           | DATETIME | False       | False         | Creation time [YYYY-MM-DDThh:mm:ss] (UTC)        |
| updated_at           | DATETIME | False       | False         | Update time [YYYY-MM-DDThh:mm:ss] (UTC)          |


### Other tables

There are more tables which are still under development such as `sky` and `cluster`.


## File format

As a target list contains proposal-specific and target-specific information, a file format which can handle metadata would be preferable.

A couple of candidates can be recommended.

1. FITS binary table
2. ECSV (Enhanced CSV)

Both can be easily prepared with Astropy.

### Example

Prepare a list for targets.

```python
from astropy.table import Table
tb = Table([[42687868933508256, 42687868933508552],
            [351.32788192091937, 351.2784400775651],
            [0.713249785705446, 0.7191567004328004],
            ["J2000.0", "J2000.0"],
            [9706, 9706],
            [304, 304],
            ["hscssp_pdr3_dud", "hscssp_pdr3_dud"],
            [1.0, 1.0],
            [900.0, 900.0]],
            names=["obj_id",
                   "ra",
                   "dec",
                   "epoch",
                   "tract",
                   "patch",
                   "input_catalog",
                   "priority",
                   "effective_exptime"],
            meta={"proposal_id": "S22A-QN001"})
```

If you have a similar list as `pandas.DataFrame`, the following should work.

```python
tb = Table.from_pandas(df)
tb.meta['proposal_id'] = "S22A-QN001"
```

You can save the object into a file.

```python
tb.write('targets_s22a-qn001.fits', format='fits')
tb.write('targets_s22a-qn001.ecsv', format='ascii.ecsv')
```

Reading the data is easy.

```python
tb2 = Table.read('targets_s22a-qn001.fits')
tb2 = Table.read('targets_s22a-qn001.ecsv')

print(tb2.meta["proposal_id"])
print(tb2)

```

## Notes on future development

- Currently, only creating entries in `targetDB` is tested. Updating and removing them need to be implemented in the future.
- Also, the script/function to create entries is still as of the 2021 November commissioning. This will be modified accordingly.