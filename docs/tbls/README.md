# PFS Target Database

## Tables

| Name | Columns | Comment | Type |
| ---- | ------- | ------- | ---- |
| [public.filter_name](public.filter_name.md) | 4 |  | BASE TABLE |
| [public.proposal_category](public.proposal_category.md) | 5 |  | BASE TABLE |
| [public.input_catalog](public.input_catalog.md) | 6 |  | BASE TABLE |
| [public.target_type](public.target_type.md) | 5 |  | BASE TABLE |
| [public.proposal](public.proposal.md) | 13 |  | BASE TABLE |
| [public.sky](public.sky.md) | 14 |  | BASE TABLE |
| [public.fluxstd](public.fluxstd.md) | 61 |  | BASE TABLE |
| [public.target](public.target.md) | 59 |  | BASE TABLE |
| [public.cluster](public.cluster.md) | 10 |  | BASE TABLE |

## Stored procedures and functions

| Name | ReturnType | Arguments | Type |
| ---- | ------- | ------- | ---- |
| public.q3c_seloper | bool | double precision, q3c_type | FUNCTION |
| public.q3c_sel | float8 | internal, oid, internal, integer | FUNCTION |
| public.q3c_seljoin | float8 | internal, oid, internal, smallint, internal | FUNCTION |
| public.q3c_version | cstring |  | FUNCTION |
| public.q3c_ang2ipix | int8 | double precision, double precision | FUNCTION |
| public.q3c_ang2ipix | int8 | ra real, decl real | FUNCTION |
| public.q3c_ipix2ang | _float8 | ipix bigint | FUNCTION |
| public.q3c_pixarea | float8 | ipix bigint, depth integer | FUNCTION |
| public.q3c_ipixcenter | int8 | ra double precision, decl double precision, integer | FUNCTION |
| public.q3c_dist | float8 | ra1 double precision, dec1 double precision, ra2 double precision, dec2 double precision | FUNCTION |
| public.q3c_sindist | float8 | double precision, double precision, double precision, double precision | FUNCTION |
| public.q3c_sindist_pm | float8 | ra1 double precision, dec1 double precision, pmra1 double precision, pmdec1 double precision, cosdec_flag integer, epoch1 double precision, ra2 double precision, dec2 double precision, epoch2 double precision | FUNCTION |
| public.q3c_dist_pm | float8 | ra1 double precision, dec1 double precision, pmra1 double precision, pmdec1 double precision, cosdec_flag integer, epoch1 double precision, ra2 double precision, dec2 double precision, epoch2 double precision | FUNCTION |
| public.q3c_nearby_it | int8 | double precision, double precision, double precision, integer | FUNCTION |
| public.q3c_nearby_pm_it | int8 | ra1 double precision, dec1 double precision, pmra1 double precision, pmdec1 double precision, cosdec_flag integer, maxepoch_delta double precision, rad double precision, flag integer | FUNCTION |
| public.q3c_ellipse_nearby_it | int8 | double precision, double precision, double precision, double precision, double precision, integer | FUNCTION |
| public.q3c_in_ellipse | bool | ra0 double precision, dec0 double precision, ra_ell double precision, dec_ell double precision, semimaj_ax double precision, axis_ratio double precision, pa double precision | FUNCTION |
| public.q3c_radial_query_it | int8 | double precision, double precision, double precision, integer, integer | FUNCTION |
| public.q3c_ellipse_query_it | int8 | ra_ell double precision, dec_ell double precision, semimajax double precision, axis_ratio double precision, pa double precision, iteration integer, full_flag integer | FUNCTION |
| public.q3c_poly_query_it | int8 | double precision[], integer, integer | FUNCTION |
| public.q3c_poly_query_it | int8 | polygon, integer, integer | FUNCTION |
| public.q3c_in_poly | bool | double precision, double precision, double precision[] | FUNCTION |
| public.q3c_in_poly | bool | double precision, double precision, polygon | FUNCTION |
| public.q3c_join | bool | leftra double precision, leftdec double precision, rightra double precision, rightdec double precision, radius double precision | FUNCTION |
| public.q3c_join | bool | leftra double precision, leftdec double precision, rightra real, rightdec real, radius double precision | FUNCTION |
| public.q3c_join_pm | bool | left_ra double precision, left_dec double precision, left_pmra double precision, left_pmdec double precision, cosdec_flag integer, left_epoch double precision, right_ra double precision, right_dec double precision, right_epoch double precision, max_epoch_delta double precision, radius double precision | FUNCTION |
| public.q3c_ellipse_join | bool | leftra double precision, leftdec double precision, rightra double precision, rightdec double precision, semimajoraxis double precision, axisratio double precision, pa double precision | FUNCTION |
| public.q3c_radial_query | bool | real, real, double precision, double precision, double precision | FUNCTION |
| public.q3c_radial_query | bool | double precision, double precision, double precision, double precision, double precision | FUNCTION |
| public.q3c_ellipse_query | bool | ra_col double precision, dec_col double precision, ra_ell double precision, dec_ell double precision, semimajax double precision, axis_ratio double precision, pa double precision | FUNCTION |
| public.q3c_poly_query | bool | double precision, double precision, double precision[] | FUNCTION |
| public.q3c_poly_query | bool | real, real, double precision[] | FUNCTION |
| public.q3c_poly_query | bool | double precision, double precision, polygon | FUNCTION |
| public.q3c_poly_query | bool | real, real, polygon | FUNCTION |

## Relations

```mermaid
erDiagram

"public.proposal" }o--o| "public.proposal_category" : "FOREIGN KEY (proposal_category_id) REFERENCES proposal_category(proposal_category_id)"
"public.sky" }o--|| "public.input_catalog" : "FOREIGN KEY (input_catalog_id) REFERENCES input_catalog(input_catalog_id)"
"public.sky" }o--o| "public.target_type" : "FOREIGN KEY (target_type_id) REFERENCES target_type(target_type_id)"
"public.fluxstd" }o--o| "public.filter_name" : "FOREIGN KEY (filter_g) REFERENCES filter_name(filter_name)"
"public.fluxstd" }o--o| "public.filter_name" : "FOREIGN KEY (filter_i) REFERENCES filter_name(filter_name)"
"public.fluxstd" }o--o| "public.filter_name" : "FOREIGN KEY (filter_j) REFERENCES filter_name(filter_name)"
"public.fluxstd" }o--o| "public.filter_name" : "FOREIGN KEY (filter_r) REFERENCES filter_name(filter_name)"
"public.fluxstd" }o--o| "public.filter_name" : "FOREIGN KEY (filter_y) REFERENCES filter_name(filter_name)"
"public.fluxstd" }o--o| "public.filter_name" : "FOREIGN KEY (filter_z) REFERENCES filter_name(filter_name)"
"public.fluxstd" }o--|| "public.input_catalog" : "FOREIGN KEY (input_catalog_id) REFERENCES input_catalog(input_catalog_id)"
"public.fluxstd" }o--o| "public.target_type" : "FOREIGN KEY (target_type_id) REFERENCES target_type(target_type_id)"
"public.target" }o--o| "public.filter_name" : "FOREIGN KEY (filter_g) REFERENCES filter_name(filter_name)"
"public.target" }o--o| "public.filter_name" : "FOREIGN KEY (filter_i) REFERENCES filter_name(filter_name)"
"public.target" }o--o| "public.filter_name" : "FOREIGN KEY (filter_j) REFERENCES filter_name(filter_name)"
"public.target" }o--o| "public.filter_name" : "FOREIGN KEY (filter_r) REFERENCES filter_name(filter_name)"
"public.target" }o--o| "public.filter_name" : "FOREIGN KEY (filter_y) REFERENCES filter_name(filter_name)"
"public.target" }o--o| "public.filter_name" : "FOREIGN KEY (filter_z) REFERENCES filter_name(filter_name)"
"public.target" }o--|| "public.input_catalog" : "FOREIGN KEY (input_catalog_id) REFERENCES input_catalog(input_catalog_id)"
"public.target" }o--o| "public.target_type" : "FOREIGN KEY (target_type_id) REFERENCES target_type(target_type_id)"
"public.target" }o--o| "public.proposal" : "FOREIGN KEY (proposal_id) REFERENCES proposal(proposal_id)"
"public.cluster" }o--o| "public.input_catalog" : "FOREIGN KEY (input_catalog_id) REFERENCES input_catalog(input_catalog_id)"
"public.cluster" }o--|| "public.target" : "FOREIGN KEY (target_id) REFERENCES target(target_id)"

"public.filter_name" {
  varchar filter_name
  varchar filter_name_description
  timestamp_without_time_zone created_at
  timestamp_without_time_zone updated_at
}
"public.proposal_category" {
  integer proposal_category_id
  varchar proposal_category_name
  varchar proposal_category_description
  timestamp_without_time_zone created_at
  timestamp_without_time_zone updated_at
}
"public.input_catalog" {
  integer input_catalog_id
  varchar input_catalog_name
  varchar input_catalog_description
  varchar_16_ upload_id
  timestamp_without_time_zone created_at
  timestamp_without_time_zone updated_at
}
"public.target_type" {
  integer target_type_id
  varchar target_type_name
  varchar target_type_description
  timestamp_without_time_zone created_at
  timestamp_without_time_zone updated_at
}
"public.proposal" {
  varchar proposal_id
  varchar group_id
  varchar pi_first_name
  varchar pi_last_name
  varchar pi_middle_name
  double_precision rank
  varchar grade
  double_precision allocated_time_total
  double_precision allocated_time_lr
  double_precision allocated_time_mr
  integer proposal_category_id FK
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
```

---

> Generated by [tbls](https://github.com/k1LoW/tbls)
