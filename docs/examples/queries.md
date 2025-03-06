# Useful Queries

## Targets

### Around a coordinate

```sql
/* Select 10 objects within r=1 deg from the center of
   the COSMOS region (RA=150, Dec=2) */
SELECT * FROM target
WHERE q3c_radial_query(ra, dec, 150.0, 2.0, 1.0)
LIMIT 10;
```

### For single proposal

```sql
/* Select all rows from the target table where the proposal_id is
   'S25A-058QN' */
SELECT *
FROM target
WHERE proposal_id = 'S25A-058QN';
```

### For multiple proposals

```sql
/* Select all rows from the target table where the proposal_id is
   'S25A-058QN' or 'S25A-028QN' */
SELECT *
FROM target
WHERE proposal_id IN ('S25A-058QN', 'S25A-028QN');
```

### For proposals with a semester prefix

```sql
/* Select all rows from the target table where the proposal_id starts
   with 'S25A' */
SELECT *
FROM target
WHERE proposal_id LIKE 'S25A%';
```

### For a semester with the `active` flag is `true`

```sql
/* Select all rows from the target table where the proposal_id starts
   with 'S25A' and the input catalog is active */
SELECT t.*
FROM target t
JOIN input_catalog ic ON t.input_catalog_id = ic.input_catalog_id
WHERE t.proposal_id LIKE 'S25A%'
AND ic.active = TRUE;
```

### With user-defined custom pointings

#### Select all user-defined custom pointings for classical proposals

```sql
/* Select all rows from the user_pointing table for proposals asking
    classical observation with user pointing */
SELECT up.*
FROM user_pointing up
JOIN input_catalog ic ON up.input_catalog_id = ic.input_catalog_id
WHERE ic.is_user_pointing = TRUE
AND ic.is_classical = TRUE;
```

#### Select targets for a classical proposal requesting user pointing

```sql
/* Select all targets for a classical proposal requesting user pointing */
SELECT t.target_id, t.obj_id, t.ra, t.dec, t.proposal_id, t.input_catalog_id
FROM target t
JOIN input_catalog ic ON t.input_catalog_id = ic.input_catalog_id
WHERE t.proposal_id = 'S25A-039'
AND ic.active = TRUE
AND ic.is_classical = TRUE
AND ic.is_user_pointing = TRUE;
```

#### Select custom pointing information for a classical proposal requesting user pointing

The query is useful to fetch data for a classical proposal requesting user pointing by using only the `proposal_id`.

```sql
/* Select all user pointing information for a classical proposal requesting user pointing */
SELECT up.user_pointing_id, up.ppc_code, up.ppc_ra, up.ppc_dec, up.ppc_pa,
       up.ppc_resolution, up.ppc_priority, up.input_catalog_id
FROM user_pointing up
JOIN input_catalog ic ON up.input_catalog_id = ic.input_catalog_id
WHERE ic.active = TRUE
AND ic.is_classical = TRUE
AND ic.is_user_pointing = TRUE
AND EXISTS (
    SELECT 1
    FROM target t
    WHERE t.input_catalog_id = ic.input_catalog_id
    AND t.proposal_id = 'S25A-039'
);
```
