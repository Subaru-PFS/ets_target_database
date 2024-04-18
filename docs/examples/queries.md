# Useful Queries

## Cone search around a coordinate

You can search for targets within a certain radius from a give coordinate by using Q3C.

```sql
/* Select 10 objects within 1deg radius from the center of the COSMOS region (RA=150, Dec=2) */
SELECT * FROM target WHERE q3c_radial_query(ra, dec, 150.0, 2.0, 1.0) LIMIT 10;
```
