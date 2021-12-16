
## input_catalog

| name                      | type     | primary_key   | autoincrement   | comment                                                        |
|:--------------------------|:---------|:--------------|:----------------|:---------------------------------------------------------------|
| input_catalog_id          | INTEGER  | True          | False           | Unique identifier for input catalogs                           |
| input_catalog_name        | VARCHAR  | False         | False           | Name of the input catalog (e.g., Gaia DR2, HSC-SSP PDR3, etc.) |
| input_catalog_description | VARCHAR  | False         | False           | Description of the input catalog                               |
| created_at                | DATETIME | False         | False           |                                                                |
| updated_at                | DATETIME | False         | False           |                                                                |

## proposal_category

| name                          | type     | primary_key   | autoincrement   | comment                                                           |
|:------------------------------|:---------|:--------------|:----------------|:------------------------------------------------------------------|
| proposal_category_id          | INTEGER  | True          | False           | Unique identifier of proposal category                            |
| proposal_category_name        | VARCHAR  | False         | False           | Proposal category name (e.g., Openuse, Keck, Gemini, and UH)      |
| proposal_category_description | VARCHAR  | False         | False           | Proposal category description (e.g., Openuse, Time exchange, etc. |
| created_at                    | DATETIME | False         | False           | Creation time                                                     |
| updated_at                    | DATETIME | False         | False           | Update time                                                       |

## target_type

| name                    | type     | primary_key   | autoincrement   | comment                            |
|:------------------------|:---------|:--------------|:----------------|:-----------------------------------|
| target_type_id          | INTEGER  | True          | False           | Unique identifier for target types |
| target_type_name        | VARCHAR  | False         | False           | Name for the target type.          |
| target_type_description | VARCHAR  | False         | False           | Description of the target type     |
| created_at              | DATETIME | False         | False           |                                    |
| updated_at              | DATETIME | False         | False           |                                    |

## proposal

| name                 | type     | primary_key   | autoincrement   | comment                                           |
|:---------------------|:---------|:--------------|:----------------|:--------------------------------------------------|
| proposal_id          | VARCHAR  | True          | False           | Unique identifier for proposal (e.g, S21B-OT06?)  |
| group_id             | VARCHAR  | False         | False           | Group ID in STARS (e.g., o21195?)                 |
| pi_first_name        | VARCHAR  | False         | False           | PI's first name                                   |
| pi_last_name         | VARCHAR  | False         | False           | PI's last name                                    |
| pi_middle_name       | VARCHAR  | False         | False           | PI's middle name                                  |
| rank                 | FLOAT    | False         | False           | TAC score                                         |
| grade                | VARCHAR  | False         | False           | TAC grade (A/B/C/F in the case of HSC queue)      |
| allocated_time       | FLOAT    | False         | False           | Total fiberhours allocated by TAC (hour)          |
| proposal_category_id | INTEGER  | False         | False           |                                                   |
| created_at           | DATETIME | False         | False           | Creation time [YYYY-MM-DDThh:mm:ss] (UTC or HST?) |
| updated_at           | DATETIME | False         | False           | Update time [YYYY-MM-DDThh:mm:ss] (UTC or HST?)   |

## target

| name                   | type     | primary_key   | autoincrement   | comment                                                                                               |
|:-----------------------|:---------|:--------------|:----------------|:------------------------------------------------------------------------------------------------------|
| target_id              | BIGINT   | True          | True            | Unique identifier for each target                                                                     |
| proposal_id            | VARCHAR  | False         | False           |                                                                                                       |
| obj_id                 | BIGINT   | False         | False           | Object ID as specified by the observer at Phase 2 (can be same as the input_catalog_object_id)        |
| ra                     | FLOAT    | False         | False           | RA (ICRS, degree)                                                                                     |
| dec                    | FLOAT    | False         | False           | Dec (ICRS, degree)                                                                                    |
| epoch                  | VARCHAR  | False         | False           | Epoch                                                                                                 |
| tract                  | INTEGER  | False         | False           | same definition as HSC-SSP?; can be derived from the coordinate                                       |
| patch                  | INTEGER  | False         | False           | same definition as HSC-SSP?; can be derived from the coordinate; Note that it's defined as an integer |
| target_type_id         | INTEGER  | False         | False           |                                                                                                       |
| input_catalog_id       | INTEGER  | False         | False           | Input catalog ID from the input_catalog table                                                         |
| fiber_mag_g            | FLOAT    | False         | False           | g-band magnitude within a fiber (AB mag)                                                              |
| fiber_mag_r            | FLOAT    | False         | False           | r-band magnitude within a fiber (AB mag)                                                              |
| fiber_mag_i            | FLOAT    | False         | False           | i-band magnitude within a fiber (AB mag)                                                              |
| fiber_mag_z            | FLOAT    | False         | False           | z-band magnitude within a fiber (AB mag)                                                              |
| fiber_mag_y            | FLOAT    | False         | False           | y-band magnitude within a fiber (AB mag)                                                              |
| fiber_mag_j            | FLOAT    | False         | False           | J band magnitude within a fiber (AB mag)                                                              |
| psf_mag_g              | FLOAT    | False         | False           | g-band PSF magnitude (AB mag)                                                                         |
| psf_mag_r              | FLOAT    | False         | False           | r-band PSF magnitude (AB mag)                                                                         |
| psf_mag_i              | FLOAT    | False         | False           | i-band PSF magnitude (AB mag)                                                                         |
| psf_mag_z              | FLOAT    | False         | False           | z-band PSF magnitude (AB mag)                                                                         |
| psf_mag_y              | FLOAT    | False         | False           | y-band PSF magnitude (AB mag)                                                                         |
| psf_mag_j              | FLOAT    | False         | False           | J band PSF magnitude (AB mag)                                                                         |
| psf_flux_g             | FLOAT    | False         | False           | g-band PSF flux (nJy)                                                                                 |
| psf_flux_r             | FLOAT    | False         | False           | r-band PSF flux (nJy)                                                                                 |
| psf_flux_i             | FLOAT    | False         | False           | i-band PSF flux (nJy)                                                                                 |
| psf_flux_z             | FLOAT    | False         | False           | z-band PSF flux (nJy)                                                                                 |
| psf_flux_y             | FLOAT    | False         | False           | y-band PSF flux (nJy)                                                                                 |
| psf_flux_j             | FLOAT    | False         | False           | J band PSF flux (nJy)                                                                                 |
| priority               | FLOAT    | False         | False           | Priority of the target specified by the observer within the proposal                                  |
| effective_exptime      | FLOAT    | False         | False           | Requested effective exposure time (s)                                                                 |
| is_medium_resolution   | BOOLEAN  | False         | False           | True if the medium resolution mode is requested                                                       |
| qa_relative_throughput | FLOAT    | False         | False           | Relative throughput to the reference value requested by the observer                                  |
| qa_relative_noise      | FLOAT    | False         | False           | Relative noise to the reference value requested by the observer                                       |
| qa_reference_lambda    | FLOAT    | False         | False           | Reference wavelength to evaluate effective exposure time (angstrom or nm?)                            |
| prob_f_star            | FLOAT    | False         | False           | Probability to be a F-star                                                                            |
| created_at             | DATETIME | False         | False           |                                                                                                       |
| updated_at             | DATETIME | False         | False           |                                                                                                       |
