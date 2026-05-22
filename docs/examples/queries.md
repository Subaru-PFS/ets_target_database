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

---

## PostgreSQL Troubleshooting

### Running Processes

#### Show all active processes

```sql
/* Show all currently connected processes */
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    state,
    wait_event_type,
    wait_event,
    query_start,
    now() - query_start AS duration,
    query
FROM pg_stat_activity
WHERE pid <> pg_backend_pid()
ORDER BY query_start;
```

#### Show processes for a specific database

```sql
/* Show processes for a specific database */
SELECT
    pid,
    usename,
    state,
    wait_event_type,
    wait_event,
    now() - query_start AS duration,
    query
FROM pg_stat_activity
WHERE datname = 'your_database_name'
  AND pid <> pg_backend_pid()
ORDER BY query_start;
```

#### Show only active queries

```sql
/* Show only currently running queries */
SELECT pid, usename, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active'
  AND pid <> pg_backend_pid()
ORDER BY duration DESC;
```

#### Show long-running queries

```sql
/* Show queries that have been running for more than 5 minutes */
SELECT pid, usename, state, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE now() - query_start > interval '5 minutes'
  AND state <> 'idle'
  AND pid <> pg_backend_pid()
ORDER BY duration DESC;
```

#### Show idle-in-transaction processes

```sql
/* Show processes in 'idle in transaction' state (common cause of locks) */
SELECT pid, usename, state, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state IN ('idle in transaction', 'idle in transaction (aborted)')
ORDER BY duration DESC;
```

#### Count connections by user and state

```sql
/* Count connections grouped by user and state */
SELECT count(*) AS cnt, usename, state
FROM pg_stat_activity
GROUP BY usename, state
ORDER BY cnt DESC;
```

---

### Locks

#### Show lock-waiting processes

```sql
/* Show processes waiting on locks and the processes blocking them */
SELECT
    blocking.pid AS blocking_pid,
    blocking.state AS blocking_state,
    left(blocking.query, 80) AS blocking_query,
    blocked.pid AS blocked_pid,
    blocked.state AS blocked_state,
    blocked.wait_event,
    left(blocked.query, 80) AS blocked_query
FROM pg_stat_activity blocked
JOIN pg_stat_activity blocking
    ON blocking.pid = ANY(pg_blocking_pids(blocked.pid))
ORDER BY blocking.pid;
```

#### Show blockers for a specific query

```sql
/* Show processes blocking a specific query (e.g., ALTER TABLE) */
SELECT
    blocking.pid AS blocking_pid,
    blocking.state AS blocking_state,
    left(blocking.query, 80) AS blocking_query,
    blocked.pid AS blocked_pid,
    blocked.state AS blocked_state,
    blocked.wait_event
FROM pg_stat_activity blocked
JOIN pg_stat_activity blocking
    ON blocking.pid = ANY(pg_blocking_pids(blocked.pid))
WHERE blocked.query LIKE 'ALTER TABLE%';
```

---

### Terminating Processes

#### Cancel a query (keep connection)

```sql
/* Cancel the query only; the connection is preserved */
SELECT pg_cancel_backend(<pid>);
```

#### Force-terminate a process

```sql
/* Terminate the connection entirely; use when pg_cancel_backend has no effect */
SELECT pg_terminate_backend(<pid>);
```

#### Bulk-terminate idle-in-transaction processes

```sql
/* Terminate all idle-in-transaction processes older than 1 hour */
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state IN ('idle in transaction', 'idle in transaction (aborted)')
  AND now() - query_start > interval '1 hour'
  AND pid <> pg_backend_pid();
```

#### Bulk-terminate stale idle connections

```sql
/* Terminate all idle connections older than 1 day */
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND now() - state_change > interval '1 day'
  AND pid <> pg_backend_pid();
```

---

### Table and Index Information

#### Check table sizes

```sql
/* Check the size of specific tables (including indexes) */
SELECT
    pg_size_pretty(pg_total_relation_size('target')) AS target_size,
    pg_size_pretty(pg_total_relation_size('fluxstd')) AS fluxstd_size;
```

#### List largest tables in the database

```sql
/* List tables ordered by total size */
SELECT
    relname AS table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 20;
```

---

### DDL Operations on Large Tables

#### Safely add a FOREIGN KEY constraint

```sql
/* Split into NOT VALID + VALIDATE to minimise lock duration */

-- Step 1: Add the constraint without validation (short lock)
ALTER TABLE target
    ADD CONSTRAINT target_filter_u_fkey
    FOREIGN KEY (filter_u) REFERENCES filter_name(filter_name)
    NOT VALID;

-- Step 2: Validate the constraint (uses ShareUpdateExclusiveLock; does not block reads/writes)
ALTER TABLE target VALIDATE CONSTRAINT target_filter_u_fkey;
```

#### Safely create or drop an index

```sql
/* Use CONCURRENTLY to avoid blocking other queries */

-- Create
CREATE INDEX CONCURRENTLY idx_target_ra ON target(ra);

-- Drop
DROP INDEX CONCURRENTLY idx_target_ra;
```

#### Set timeouts during migrations

```sql
/* Prevent migrations from hanging indefinitely on lock acquisition */
SET lock_timeout = '5s';      -- Fail immediately if the lock cannot be acquired within 5 s
SET statement_timeout = '0';  -- No time limit on the statement itself
```
