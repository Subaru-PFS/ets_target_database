# public.cluster

## Description

## Columns

| Name | Type | Default | Nullable | Children | Parents | Comment |
| ---- | ---- | ------- | -------- | -------- | ------- | ------- |
| cluster_id | bigint |  | false |  |  | Unique identifier of clusters found at duplication checking |
| target_id | bigint |  | false |  | [public.target](public.target.md) |  |
| n_targets | integer |  | true |  |  | Number of targets in the cluster |
| ra_cluster | double precision |  | true |  |  | Mean RA of targets in the cluster (ICRS, degree) |
| dec_cluster | double precision |  | true |  |  | Mean Dec of targets in the cluster (ICRS, degree) |
| d_ra | double precision |  | true |  |  | RA(target) - RA(cluster) (degree) |
| d_dec | double precision |  | true |  |  | Dec(target) - Dec(cluster) (degree) |
| input_catalog_id | integer |  | true |  | [public.input_catalog](public.input_catalog.md) | Input catalog ID from the input_catalog table |
| created_at | timestamp without time zone |  | true |  |  | UTC |
| updated_at | timestamp without time zone |  | true |  |  | UTC |

## Constraints

| Name | Type | Definition |
| ---- | ---- | ---------- |
| cluster_input_catalog_id_fkey | FOREIGN KEY | FOREIGN KEY (input_catalog_id) REFERENCES input_catalog(input_catalog_id) |
| cluster_target_id_fkey | FOREIGN KEY | FOREIGN KEY (target_id) REFERENCES target(target_id) |
| cluster_pkey | PRIMARY KEY | PRIMARY KEY (cluster_id, target_id) |

## Indexes

| Name | Definition |
| ---- | ---------- |
| cluster_pkey | CREATE UNIQUE INDEX cluster_pkey ON public.cluster USING btree (cluster_id, target_id) |

## Relations

```mermaid
erDiagram

"public.cluster" }o--|| "public.target" : "FOREIGN KEY (target_id) REFERENCES target(target_id)"
"public.cluster" }o--o| "public.input_catalog" : "FOREIGN KEY (input_catalog_id) REFERENCES input_catalog(input_catalog_id)"

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
"public.input_catalog" {
  integer input_catalog_id
  varchar input_catalog_name
  varchar input_catalog_description
  varchar_16_ upload_id
  timestamp_without_time_zone created_at
  timestamp_without_time_zone updated_at
}
```

---

> Generated by [tbls](https://github.com/k1LoW/tbls)