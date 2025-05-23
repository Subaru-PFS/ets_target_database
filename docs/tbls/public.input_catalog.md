# public.input_catalog

## Description

## Columns

| Name | Type | Default | Nullable | Children | Parents | Comment |
| ---- | ---- | ------- | -------- | -------- | ------- | ------- |
| input_catalog_name | varchar |  | false |  |  | Name of the input catalog (e.g., Gaia DR2, HSC-SSP PDR3, etc.) |
| input_catalog_description | varchar |  | true |  |  | Description of the input catalog |
| created_at | timestamp without time zone | timezone('utc'::text, CURRENT_TIMESTAMP) | true |  |  | The date and time in UTC when the record was created |
| updated_at | timestamp without time zone |  | true |  |  | The date and time in UTC when the record was last updated |
| upload_id | varchar(16) |  | true |  |  | A 8-bit hex string (16 characters) assigned at the submission of the target list (default: empty string) |
| input_catalog_id | integer |  | false | [public.cluster](public.cluster.md) [public.fluxstd](public.fluxstd.md) [public.sky](public.sky.md) [public.target](public.target.md) [public.user_pointing](public.user_pointing.md) |  | Unique identifier for input catalogs |
| active | boolean |  | true |  |  | Flag to indicate if the input catalog is active (default: True) |
| is_classical | boolean |  | true |  |  | True if the classical mode is requested |
| is_user_pointing | boolean |  | true |  |  | True if user-defined pointings are provided |

## Constraints

| Name | Type | Definition |
| ---- | ---- | ---------- |
| input_catalog_input_catalog_id_key | UNIQUE | UNIQUE (input_catalog_id) |
| input_catalog_pkey | PRIMARY KEY | PRIMARY KEY (input_catalog_id) |

## Indexes

| Name | Definition |
| ---- | ---------- |
| input_catalog_input_catalog_id_key | CREATE UNIQUE INDEX input_catalog_input_catalog_id_key ON public.input_catalog USING btree (input_catalog_id) |
| input_catalog_pkey | CREATE UNIQUE INDEX input_catalog_pkey ON public.input_catalog USING btree (input_catalog_id) |

## Relations

```mermaid
erDiagram

"public.cluster" }o--o| "public.input_catalog" : "FOREIGN KEY (input_catalog_id) REFERENCES input_catalog(input_catalog_id)"
"public.fluxstd" }o--|| "public.input_catalog" : "FOREIGN KEY (input_catalog_id) REFERENCES input_catalog(input_catalog_id)"
"public.sky" }o--|| "public.input_catalog" : "FOREIGN KEY (input_catalog_id) REFERENCES input_catalog(input_catalog_id)"
"public.target" }o--|| "public.input_catalog" : "FOREIGN KEY (input_catalog_id) REFERENCES input_catalog(input_catalog_id)"
"public.user_pointing" }o--|| "public.input_catalog" : "FOREIGN KEY (input_catalog_id) REFERENCES input_catalog(input_catalog_id)"

"public.input_catalog" {
  varchar input_catalog_name
  varchar input_catalog_description
  timestamp_without_time_zone created_at
  timestamp_without_time_zone updated_at
  varchar_16_ upload_id
  integer input_catalog_id
  boolean active
  boolean is_classical
  boolean is_user_pointing
}
"public.cluster" {
  bigint cluster_id
  bigint target_id FK
  integer n_targets
  double_precision ra_cluster
  double_precision dec_cluster
  double_precision d_ra
  double_precision d_dec
  integer input_catalog_id FK
  timestamp_without_time_zone created_at
  timestamp_without_time_zone updated_at
}
"public.fluxstd" {
  bigint fluxstd_id
  bigint obj_id
  double_precision ra
  double_precision dec
  varchar epoch
  double_precision parallax
  double_precision parallax_error
  double_precision pmra
  double_precision pmra_error
  double_precision pmdec
  double_precision pmdec_error
  integer tract
  integer patch
  integer target_type_id FK
  integer input_catalog_id FK
  double_precision psf_mag_g
  double_precision psf_mag_r
  double_precision psf_mag_i
  double_precision psf_mag_z
  double_precision psf_mag_y
  double_precision psf_mag_j
  double_precision psf_flux_g
  double_precision psf_flux_r
  double_precision psf_flux_i
  double_precision psf_flux_z
  double_precision psf_flux_y
  double_precision psf_flux_j
  double_precision prob_f_star
  boolean flags_dist
  boolean flags_ebv
  varchar version
  timestamp_without_time_zone created_at
  timestamp_without_time_zone updated_at
  varchar filter_g FK
  varchar filter_r FK
  varchar filter_i FK
  varchar filter_z FK
  varchar filter_y FK
  varchar filter_j FK
  double_precision psf_mag_error_g
  double_precision psf_mag_error_r
  double_precision psf_mag_error_i
  double_precision psf_mag_error_z
  double_precision psf_mag_error_y
  double_precision psf_mag_error_j
  double_precision psf_flux_error_g
  double_precision psf_flux_error_r
  double_precision psf_flux_error_i
  double_precision psf_flux_error_z
  double_precision psf_flux_error_y
  double_precision psf_flux_error_j
  double_precision teff_brutus
  double_precision teff_brutus_low
  double_precision teff_brutus_high
  double_precision logg_brutus
  double_precision logg_brutus_low
  double_precision logg_brutus_high
  double_precision teff_gspphot
  double_precision teff_gspphot_lower
  double_precision teff_gspphot_upper
  boolean is_fstar_gaia
}
"public.sky" {
  bigint sky_id
  bigint obj_id
  varchar obj_id_orig
  double_precision ra
  double_precision dec
  varchar epoch
  integer tract
  integer patch
  integer target_type_id FK
  integer input_catalog_id FK
  double_precision mag_thresh
  varchar version
  timestamp_without_time_zone created_at
  timestamp_without_time_zone updated_at
}
"public.target" {
  bigint target_id
  varchar proposal_id FK
  bigint obj_id
  double_precision ra
  double_precision dec
  varchar epoch
  double_precision parallax
  double_precision pmra
  double_precision pmdec
  integer tract
  integer patch
  integer target_type_id FK
  integer input_catalog_id FK
  double_precision fiber_mag_g
  double_precision fiber_mag_r
  double_precision fiber_mag_i
  double_precision fiber_mag_z
  double_precision fiber_mag_y
  double_precision fiber_mag_j
  double_precision psf_mag_g
  double_precision psf_mag_r
  double_precision psf_mag_i
  double_precision psf_mag_z
  double_precision psf_mag_y
  double_precision psf_mag_j
  double_precision psf_flux_g
  double_precision psf_flux_r
  double_precision psf_flux_i
  double_precision psf_flux_z
  double_precision psf_flux_y
  double_precision psf_flux_j
  double_precision priority
  double_precision effective_exptime
  boolean is_medium_resolution
  double_precision qa_relative_throughput
  double_precision qa_relative_noise
  double_precision qa_reference_lambda
  boolean is_cluster
  timestamp_without_time_zone created_at
  timestamp_without_time_zone updated_at
  varchar filter_g FK
  varchar filter_r FK
  varchar filter_i FK
  varchar filter_z FK
  varchar filter_y FK
  varchar filter_j FK
  double_precision psf_mag_error_g
  double_precision psf_mag_error_r
  double_precision psf_mag_error_i
  double_precision psf_mag_error_z
  double_precision psf_mag_error_y
  double_precision psf_mag_error_j
  double_precision psf_flux_error_g
  double_precision psf_flux_error_r
  double_precision psf_flux_error_i
  double_precision psf_flux_error_z
  double_precision psf_flux_error_y
  double_precision psf_flux_error_j
  varchar ob_code
  double_precision single_exptime
  varchar qa_reference_arm FK
  double_precision total_flux_g
  double_precision total_flux_r
  double_precision total_flux_i
  double_precision total_flux_z
  double_precision total_flux_y
  double_precision total_flux_j
  double_precision total_flux_error_g
  double_precision total_flux_error_r
  double_precision total_flux_error_i
  double_precision total_flux_error_z
  double_precision total_flux_error_y
  double_precision total_flux_error_j
}
"public.user_pointing" {
  bigint user_pointing_id
  varchar ppc_code
  double_precision ppc_ra
  double_precision ppc_dec
  double_precision ppc_pa
  resolutionmode ppc_resolution
  double_precision ppc_priority
  integer input_catalog_id FK
  timestamp_without_time_zone created_at
  timestamp_without_time_zone updated_at
}
```

---

> Generated by [tbls](https://github.com/k1LoW/tbls)
