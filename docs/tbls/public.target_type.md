# public.target_type

## Description

## Columns

| Name | Type | Default | Nullable | Children | Parents | Comment |
| ---- | ---- | ------- | -------- | -------- | ------- | ------- |
| target_type_id | integer |  | false | [public.sky](public.sky.md) [public.fluxstd](public.fluxstd.md) [public.target](public.target.md) |  | Unique identifier for target types |
| target_type_name | varchar |  | false |  |  | Name for the target type. |
| target_type_description | varchar |  | true |  |  | Description of the target type |
| created_at | timestamp without time zone |  | true |  |  | The date and time in UTC when the record was created |
| updated_at | timestamp without time zone |  | true |  |  | The date and time in UTC when the record was last updated |

## Constraints

| Name | Type | Definition |
| ---- | ---- | ---------- |
| target_type_pkey | PRIMARY KEY | PRIMARY KEY (target_type_id) |

## Indexes

| Name | Definition |
| ---- | ---------- |
| target_type_pkey | CREATE UNIQUE INDEX target_type_pkey ON public.target_type USING btree (target_type_id) |

## Relations

```mermaid
erDiagram

"public.sky" }o--o| "public.target_type" : "FOREIGN KEY (target_type_id) REFERENCES target_type(target_type_id)"
"public.fluxstd" }o--o| "public.target_type" : "FOREIGN KEY (target_type_id) REFERENCES target_type(target_type_id)"
"public.target" }o--o| "public.target_type" : "FOREIGN KEY (target_type_id) REFERENCES target_type(target_type_id)"

"public.target_type" {
  integer target_type_id
  varchar target_type_name
  varchar target_type_description
  timestamp_without_time_zone created_at
  timestamp_without_time_zone updated_at
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
  double_precision psf_mag_error_g
  double_precision psf_mag_error_r
  double_precision psf_mag_error_i
  double_precision psf_mag_error_z
  double_precision psf_mag_error_y
  double_precision psf_mag_error_j
  double_precision psf_flux_g
  double_precision psf_flux_r
  double_precision psf_flux_i
  double_precision psf_flux_z
  double_precision psf_flux_y
  double_precision psf_flux_j
  double_precision psf_flux_error_g
  double_precision psf_flux_error_r
  double_precision psf_flux_error_i
  double_precision psf_flux_error_z
  double_precision psf_flux_error_y
  double_precision psf_flux_error_j
  varchar filter_g FK
  varchar filter_r FK
  varchar filter_i FK
  varchar filter_z FK
  varchar filter_y FK
  varchar filter_j FK
  double_precision prob_f_star
  boolean flags_dist
  boolean flags_ebv
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
  varchar version
  timestamp_without_time_zone created_at
  timestamp_without_time_zone updated_at
}
"public.target" {
  bigint target_id
  varchar proposal_id FK
  varchar ob_code
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
  double_precision psf_mag_error_g
  double_precision psf_mag_error_r
  double_precision psf_mag_error_i
  double_precision psf_mag_error_z
  double_precision psf_mag_error_y
  double_precision psf_mag_error_j
  double_precision psf_flux_g
  double_precision psf_flux_r
  double_precision psf_flux_i
  double_precision psf_flux_z
  double_precision psf_flux_y
  double_precision psf_flux_j
  double_precision psf_flux_error_g
  double_precision psf_flux_error_r
  double_precision psf_flux_error_i
  double_precision psf_flux_error_z
  double_precision psf_flux_error_y
  double_precision psf_flux_error_j
  varchar filter_g FK
  varchar filter_r FK
  varchar filter_i FK
  varchar filter_z FK
  varchar filter_y FK
  varchar filter_j FK
  double_precision priority
  double_precision effective_exptime
  boolean is_medium_resolution
  double_precision qa_relative_throughput
  double_precision qa_relative_noise
  double_precision qa_reference_lambda
  boolean is_cluster
  timestamp_without_time_zone created_at
  timestamp_without_time_zone updated_at
}
```

---

> Generated by [tbls](https://github.com/k1LoW/tbls)
