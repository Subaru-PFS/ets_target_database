
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

## fluxstd

| name             | type     | primary_key   | autoincrement   | comment                                                                                               |
|:-----------------|:---------|:--------------|:----------------|:------------------------------------------------------------------------------------------------------|
| fluxstd_id       | BIGINT   | True          | True            | Unique identifier for each flux standard star                                                         |
| obj_id           | BIGINT   | False         | False           | Gaia EDR3 sourceid                                                                                    |
| ra               | FLOAT    | False         | False           | RA (ICRS, degree)                                                                                     |
| dec              | FLOAT    | False         | False           | Dec (ICRS, degree)                                                                                    |
| epoch            | VARCHAR  | False         | False           | Epoch (e.g., J2000.0, J2015.5, etc.)                                                                  |
| parallax         | FLOAT    | False         | False           | Parallax (mas)                                                                                        |
| parallax_error   | FLOAT    | False         | False           | Standard error of parallax (mas)                                                                      |
| pmra             | FLOAT    | False         | False           | Proper motion in right ascension direction (mas/yr)                                                   |
| pmra_error       | FLOAT    | False         | False           | Standard error of pmra (mas/yr)                                                                       |
| pmdec            | FLOAT    | False         | False           | Proper motion in declination direction (mas/yr)                                                       |
| pmdec_error      | FLOAT    | False         | False           | Standard error of pmdec (mas/yr)                                                                      |
| tract            | INTEGER  | False         | False           | same definition as HSC-SSP?; can be derived from the coordinate                                       |
| patch            | INTEGER  | False         | False           | same definition as HSC-SSP?; can be derived from the coordinate; Note that it's defined as an integer |
| target_type_id   | INTEGER  | False         | False           | target_type_id from the target_type table (must be 3 for FLUXSTD)                                     |
| input_catalog_id | INTEGER  | False         | False           | input_catalog_id from the input_catalog table                                                         |
| psf_mag_g        | FLOAT    | False         | False           | g-band PSF magnitude (AB mag)                                                                         |
| psf_mag_r        | FLOAT    | False         | False           | r-band PSF magnitude (AB mag)                                                                         |
| psf_mag_i        | FLOAT    | False         | False           | i-band PSF magnitude (AB mag)                                                                         |
| psf_mag_z        | FLOAT    | False         | False           | z-band PSF magnitude (AB mag)                                                                         |
| psf_mag_y        | FLOAT    | False         | False           | y-band PSF magnitude (AB mag)                                                                         |
| psf_mag_j        | FLOAT    | False         | False           | J band PSF magnitude (AB mag)                                                                         |
| psf_flux_g       | FLOAT    | False         | False           | g-band PSF flux (nJy)                                                                                 |
| psf_flux_r       | FLOAT    | False         | False           | r-band PSF flux (nJy)                                                                                 |
| psf_flux_i       | FLOAT    | False         | False           | i-band PSF flux (nJy)                                                                                 |
| psf_flux_z       | FLOAT    | False         | False           | z-band PSF flux (nJy)                                                                                 |
| psf_flux_y       | FLOAT    | False         | False           | y-band PSF flux (nJy)                                                                                 |
| psf_flux_j       | FLOAT    | False         | False           | J band PSF flux (nJy)                                                                                 |
| prob_f_star      | FLOAT    | False         | False           | Probability of being an F-type star                                                                   |
| flags_dist       | BOOLEAN  | False         | False           | Distance uncertanty flag, True if parallax_error/parallax > 0.2                                       |
| flags_ebv        | BOOLEAN  | False         | False           | E(B-V) uncertainty flag, True if E(B-V) uncertainty is greater than 20%                               |
| created_at       | DATETIME | False         | False           |                                                                                                       |
| updated_at       | DATETIME | False         | False           |                                                                                                       |

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
| is_cluster             | BOOLEAN  | False         | False           | True if it is a cluster of multiple targets.                                                          |
| created_at             | DATETIME | False         | False           |                                                                                                       |
| updated_at             | DATETIME | False         | False           |                                                                                                       |

## cluster

| name             | type     | primary_key   | autoincrement   | comment                                                     |
|:-----------------|:---------|:--------------|:----------------|:------------------------------------------------------------|
| cluster_id       | BIGINT   | True          | False           | Unique identifier of clusters found at duplication checking |
| target_id        | BIGINT   | True          | False           |                                                             |
| n_targets        | INTEGER  | False         | False           | Number of targets in the cluster                            |
| ra_cluster       | FLOAT    | False         | False           | Mean RA of targets in the cluster (ICRS, degree)            |
| dec_cluster      | FLOAT    | False         | False           | Mean Dec of targets in the cluster (ICRS, degree)           |
| d_ra             | FLOAT    | False         | False           | RA(target) - RA(cluster) (degree)                           |
| d_dec            | FLOAT    | False         | False           | Dec(target) - Dec(cluster) (degree)                         |
| input_catalog_id | INTEGER  | False         | False           | Input catalog ID from the input_catalog table               |
| created_at       | DATETIME | False         | False           | UTC                                                         |
| updated_at       | DATETIME | False         | False           | UTC                                                         |
