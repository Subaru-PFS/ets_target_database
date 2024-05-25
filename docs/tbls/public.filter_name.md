# public.filter_name

## Description

## Columns

| Name | Type | Default | Nullable | Children | Parents | Comment |
| ---- | ---- | ------- | -------- | -------- | ------- | ------- |
| filter_name | varchar |  | false | [public.fluxstd](public.fluxstd.md) [public.target](public.target.md) |  | Filter name (e.g., g_ps1) |
| filter_name_description | varchar |  | true |  |  | Description of the filter |
| created_at | timestamp without time zone | timezone('utc'::text, CURRENT_TIMESTAMP) | true |  |  | The date and time in UTC when the record was created |
| updated_at | timestamp without time zone |  | true |  |  | The date and time in UTC when the record was last updated |

## Constraints

| Name | Type | Definition |
| ---- | ---- | ---------- |
| filter_name_pkey | PRIMARY KEY | PRIMARY KEY (filter_name) |

## Indexes

| Name | Definition |
| ---- | ---------- |
| filter_name_pkey | CREATE UNIQUE INDEX filter_name_pkey ON public.filter_name USING btree (filter_name) |

## Relations

```mermaid
erDiagram

"public.fluxstd" }o--o| "public.filter_name" : "FOREIGN KEY (filter_g) REFERENCES filter_name(filter_name)"
"public.fluxstd" }o--o| "public.filter_name" : "FOREIGN KEY (filter_i) REFERENCES filter_name(filter_name)"
"public.fluxstd" }o--o| "public.filter_name" : "FOREIGN KEY (filter_j) REFERENCES filter_name(filter_name)"
"public.fluxstd" }o--o| "public.filter_name" : "FOREIGN KEY (filter_r) REFERENCES filter_name(filter_name)"
"public.fluxstd" }o--o| "public.filter_name" : "FOREIGN KEY (filter_y) REFERENCES filter_name(filter_name)"
"public.fluxstd" }o--o| "public.filter_name" : "FOREIGN KEY (filter_z) REFERENCES filter_name(filter_name)"
"public.target" }o--o| "public.filter_name" : "FOREIGN KEY (filter_g) REFERENCES filter_name(filter_name)"
"public.target" }o--o| "public.filter_name" : "FOREIGN KEY (filter_i) REFERENCES filter_name(filter_name)"
"public.target" }o--o| "public.filter_name" : "FOREIGN KEY (filter_j) REFERENCES filter_name(filter_name)"
"public.target" }o--o| "public.filter_name" : "FOREIGN KEY (filter_r) REFERENCES filter_name(filter_name)"
"public.target" }o--o| "public.filter_name" : "FOREIGN KEY (filter_y) REFERENCES filter_name(filter_name)"
"public.target" }o--o| "public.filter_name" : "FOREIGN KEY (filter_z) REFERENCES filter_name(filter_name)"

"public.filter_name" {
  varchar filter_name
  varchar filter_name_description
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
  double_precision single_exptime
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
