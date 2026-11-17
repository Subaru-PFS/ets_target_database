#!/usr/bin/env python3
"""
Check that two q3c versions agree on q3c_ang2ipix() and q3c_radial_query().

q3c_ang2ipix(ra, dec) backs the expression indexes on target, fluxstd and
sky. If a q3c upgrade changed its value for any input, those indexes would
silently disagree with the function and have to be rebuilt. This script
loads one seeded point set into two servers, compares the ipix of every row
and the result of q3c_radial_query() for a set of PFS-sized cones, and exits
non-zero on any difference.

The point set mixes uniform points on the sphere with the inputs most likely
to expose a numerical change: ra next to 0/360, dec at and next to the
poles, the cube-face boundaries, exact integer/half-integer coordinates and
their ulp neighbours, non-finite values, and dense samples at the edge of
each cone.

Radial-query results are also checked against the exact angular distance.
2.0.1 against 2.0.6 is expected to fail on the cones centred on a cube
vertex: 2.0.1 misses about 10% of the points there for radii near 0.7 deg,
fixed upstream in 2.0.6 (segasai/q3c@3533f250). The ipix values must match.

Usage, from tests/docker/ (amd64 to match production):

    for v in 2.0.1 2.0.6; do
        docker build --platform linux/amd64 --build-arg Q3C_VERSION=$v \\
            -t targetdb-q3c:$v .
    done
    docker run -d --rm --platform linux/amd64 -e POSTGRES_PASSWORD=postgres \\
        -p 15501:5432 targetdb-q3c:2.0.1
    docker run -d --rm --platform linux/amd64 -e POSTGRES_PASSWORD=postgres \\
        -p 15506:5432 targetdb-q3c:2.0.6
    uv run python compare_q3c_versions.py \\
        postgresql://postgres:postgres@localhost:15501/postgres \\
        postgresql://postgres:postgres@localhost:15506/postgres
"""

import argparse
import io
import sys

import numpy as np
import pandas as pd
import psycopg

TABLE = "q3c_cmp_points"
CONE_RADIUS_DEG = 0.7
# Points this close to a cone's rim are left out of the ground-truth check:
# below it, float64 rounding decides membership, not q3c.
RIM_TOLERANCE_DEG = 1e-9
# Fixed cones near the places q3c treats specially; random ones are added.
FIXED_CONES = [
    (0.0, 0.0),
    (0.3, 10.0),
    (359.8, -30.0),
    (0.0, 89.5),
    (180.0, 89.9),
    (10.0, 90.0),
    (0.0, -89.6),
    (270.0, -90.0),
    (45.0, 35.26),
    (225.0, -35.26438968275466),  # exactly a cube vertex
    (135.0, -40.0),
    (315.0, 44.8),
    (225.0, 0.0),
]
N_RANDOM_CONES = 20


def uniform_sphere(rng, n):
    ra = rng.uniform(0.0, 360.0, n)
    dec = np.degrees(np.arcsin(rng.uniform(-1.0, 1.0, n)))
    return ra, dec


def angular_distance(ra, dec, ra0, dec0):
    """Great-circle distance in degrees (haversine, accurate at small angles)."""
    ra, dec, ra0, dec0 = (np.radians(np.asarray(v)) for v in (ra, dec, ra0, dec0))
    h = (
        np.sin((dec - dec0) / 2) ** 2
        + np.cos(dec) * np.cos(dec0) * np.sin((ra - ra0) / 2) ** 2
    )
    return np.degrees(2 * np.arcsin(np.sqrt(np.clip(h, 0.0, 1.0))))


def tiny_offsets(rng, largest=1e-9):
    """Zero, the smallest subnormal, a log ladder up to `largest`, random ones."""
    ladder = np.logspace(-17, np.log10(largest), 60)
    return np.concatenate([[0.0, 5e-324], ladder, rng.uniform(0, largest, 200)])


def ulp_neighbours(x, steps=2):
    x = np.asarray(x, dtype=np.float64)
    out = [x]
    up = down = x
    for _ in range(steps):
        up = np.nextafter(up, np.inf)
        down = np.nextafter(down, -np.inf)
        out += [up, down]
    return np.concatenate(out)


def cross(ra_values, dec_values):
    ra, dec = np.meshgrid(ra_values, dec_values, indexing="ij")
    return ra.ravel(), dec.ravel()


def offset_points(ra0, dec0, dist, pa):
    """Points at angular distance `dist` and position angle `pa` (deg) from a centre."""
    ra0, dec0, dist, pa = (np.radians(v) for v in (ra0, dec0, dist, pa))
    sin_dec = np.sin(dec0) * np.cos(dist) + np.cos(dec0) * np.sin(dist) * np.cos(pa)
    dec = np.arcsin(np.clip(sin_dec, -1.0, 1.0))
    dra = np.arctan2(
        np.sin(pa) * np.sin(dist) * np.cos(dec0),
        np.cos(dist) - np.sin(dec0) * sin_dec,
    )
    return np.degrees(ra0 + dra) % 360.0, np.degrees(dec)


def make_cones(rng):
    ra, dec = uniform_sphere(rng, N_RANDOM_CONES)
    return FIXED_CONES + list(zip(ra.tolist(), dec.tolist(), strict=True))


def make_points(rng, n_uniform, cones):
    groups = {}
    groups["uniform"] = uniform_sphere(rng, n_uniform)

    d = tiny_offsets(rng)
    special_dec = [0.0, 35.26438968275466, -35.26438968275466, 45.0, -45.0]
    special_dec += [89.9999, -89.9999, 90.0, -90.0]
    groups["ra_wrap"] = cross(
        np.concatenate([d, -d, 360.0 - d, 360.0 + d, ulp_neighbours([0.0, 360.0])]),
        np.concatenate([special_dec, uniform_sphere(rng, 30)[1]]),
    )

    meridians = 45.0 + 90.0 * np.arange(4)
    groups["poles"] = cross(
        np.concatenate(
            [np.arange(0.0, 360.0, 15.0), meridians, rng.uniform(0.0, 360.0, 40)]
        ),
        np.concatenate(
            [
                90.0 - d,
                -90.0 + d,
                90.0 + d[1:],
                -90.0 - d[1:],
                ulp_neighbours([90.0, -90.0]),
            ]
        ),
    )

    n_band = 400_000
    k = rng.integers(0, 4, n_band)
    groups["face_band"] = (
        meridians[k] + rng.uniform(-0.5, 0.5, n_band),
        rng.choice([-1.0, 1.0], n_band) * rng.uniform(35.0, 46.0, n_band),
    )

    groups["face_meridian"] = cross(
        np.concatenate([meridians[:, None] + s * d[None, :] for s in (1, -1)]).ravel(),
        np.concatenate([np.arange(-90.0, 90.5, 1.0), uniform_sphere(rng, 60)[1]]),
    )

    # Polar/equatorial face edge: tan(dec) = cos(ra - 90 * face).
    n_edge = 200_000
    ra = rng.uniform(0.0, 360.0, n_edge)
    edge_dec = np.degrees(np.arctan(np.cos(np.radians((ra + 45.0) % 90.0 - 45.0))))
    sign = rng.choice([-1.0, 1.0], n_edge)
    off = rng.choice(np.concatenate([d, -d]), n_edge)
    edge_ra_ulp = rng.uniform(0.0, 360.0, 20_000)
    edge_dec_ulp = np.degrees(
        np.arctan(np.cos(np.radians((edge_ra_ulp + 45.0) % 90.0 - 45.0)))
    )
    groups["face_edge"] = (
        np.concatenate([ra, np.tile(edge_ra_ulp, 5)]),
        np.concatenate([sign * (edge_dec + off), ulp_neighbours(edge_dec_ulp)]),
    )

    int_grid = cross(np.arange(0.0, 361.0), np.arange(-90.0, 91.0))
    half_grid = cross(np.arange(0.5, 360.0), np.arange(-89.5, 90.0))
    ulp_int = cross(
        ulp_neighbours(np.arange(0.0, 361.0, 5.0)),
        ulp_neighbours(np.arange(-90.0, 91.0, 5.0)),
    )
    ulp_half = cross(
        ulp_neighbours(np.arange(2.5, 360.0, 5.0)),
        ulp_neighbours(np.arange(-87.5, 90.0, 5.0)),
    )
    groups["exact"] = tuple(
        np.concatenate(parts)
        for parts in zip(int_grid, half_grid, ulp_int, ulp_half, strict=True)
    )

    nonfinite = [0.0, 45.0, np.nan, np.inf, -np.inf]
    groups["nonfinite"] = cross(nonfinite, nonfinite)

    cone_ra, cone_dec = [], []
    edge = np.concatenate([-tiny_offsets(rng, 1e-6), tiny_offsets(rng, 1e-6)[1:]])
    for ra0, dec0 in cones:
        dist = np.degrees(
            np.arccos(
                1.0 - rng.uniform(0.0, 1.0, 20_000) * (1.0 - np.cos(np.radians(1.0)))
            )
        )
        rim = CONE_RADIUS_DEG + rng.choice(edge, 5_000)
        dist = np.concatenate([dist, rim])
        pa = rng.uniform(0.0, 360.0, dist.size)
        r, dc = offset_points(ra0, dec0, dist, pa)
        cone_ra.append(r)
        cone_dec.append(dc)
    groups["cones"] = (np.concatenate(cone_ra), np.concatenate(cone_dec))

    frames = [
        pd.DataFrame({"kind": kind, "ra": ra, "dec": dec})
        for kind, (ra, dec) in groups.items()
    ]
    points = pd.concat(frames, ignore_index=True)
    points.insert(0, "id", np.arange(len(points), dtype=np.int64))
    return points


def load_points(conn, points):
    with conn.cursor() as cur:
        cur.execute(f"DROP TABLE IF EXISTS {TABLE}")
        cur.execute(
            f"CREATE TABLE {TABLE} "
            "(id bigint PRIMARY KEY, ra double precision, dec double precision)"
        )
        buf = io.StringIO()
        points[["id", "ra", "dec"]].to_csv(
            buf, header=False, index=False, float_format="%.17g", na_rep="NaN"
        )
        with cur.copy(f"COPY {TABLE} (id, ra, dec) FROM STDIN (FORMAT csv)") as copy:
            copy.write(buf.getvalue())
        cur.execute(f"CREATE INDEX ON {TABLE} (q3c_ang2ipix(ra, dec))")
        cur.execute(f"ANALYZE {TABLE}")
    conn.commit()


def fetch_ipix(conn):
    buf = io.BytesIO()
    with conn.cursor() as cur:
        query = (
            f"COPY (SELECT id, ra, dec, q3c_ang2ipix(ra, dec) FROM {TABLE} "
            "ORDER BY id) TO STDOUT (FORMAT csv)"
        )
        with cur.copy(query) as copy:
            for chunk in copy:
                buf.write(chunk)
    buf.seek(0)
    return pd.read_csv(
        buf,
        names=["id", "ra", "dec", "ipix"],
        dtype={"id": "int64", "ipix": "Int64"},
        float_precision="round_trip",
    )


def same_floats(a, b):
    a, b = np.asarray(a), np.asarray(b)
    return (
        a.shape == b.shape
        and np.array_equal(a, b, equal_nan=True)
        and np.array_equal(np.signbit(a), np.signbit(b))
    )


def radial_ids(conn, ra0, dec0):
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT id FROM {TABLE} "
            "WHERE q3c_radial_query(ra, dec, %s, %s, %s) ORDER BY id",
            (ra0, dec0, CONE_RADIUS_DEG),
        )
        return np.array([row[0] for row in cur], dtype=np.int64)


def radial_plan(conn, ra0, dec0):
    with conn.cursor() as cur:
        cur.execute(
            f"EXPLAIN SELECT id FROM {TABLE} "
            "WHERE q3c_radial_query(ra, dec, %s, %s, %s)",
            (ra0, dec0, CONE_RADIUS_DEG),
        )
        return "\n".join(row[0] for row in cur)


def server_info(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT q3c_version(), version(), "
            "(SELECT extversion FROM pg_extension WHERE extname = 'q3c')"
        )
        return cur.fetchone()


def compare(dsn_a, dsn_b, seed, n_uniform):
    rng = np.random.default_rng(seed)
    cones = make_cones(rng)
    points = make_points(rng, n_uniform, cones)
    print(f"seed={seed}, {len(points):,} points:")
    print(points["kind"].value_counts().to_string())

    results = {}
    failed = False
    for label, dsn in (("A", dsn_a), ("B", dsn_b)):
        with psycopg.connect(dsn) as conn:
            conn.execute("CREATE EXTENSION IF NOT EXISTS q3c")
            conn.commit()
            q3c_version, pg_version, ext_version = server_info(conn)
            print(f"\n[{label}] q3c {q3c_version} (extension {ext_version})")
            print(f"[{label}] {pg_version}")
            load_points(conn, points)
            ipix = fetch_ipix(conn)
            plan = radial_plan(conn, *cones[0])
            if "Index" not in plan:
                print(f"[{label}] radial query does not use the q3c index:\n{plan}")
                failed = True
            cone_ids = [radial_ids(conn, ra0, dec0) for ra0, dec0 in cones]
            conn.execute(f"DROP TABLE {TABLE}")
            conn.commit()
        if not (
            np.array_equal(ipix["id"], points["id"])
            and same_floats(ipix["ra"], points["ra"])
            and same_floats(ipix["dec"], points["dec"])
        ):
            print(f"[{label}] points did not round-trip bit-exactly")
            failed = True
        results[label] = (ipix, cone_ids)

    ipix_a, cones_a = results["A"]
    ipix_b, cones_b = results["B"]
    differs = ~(
        (ipix_a["ipix"] == ipix_b["ipix"]).fillna(False)
        | (ipix_a["ipix"].isna() & ipix_b["ipix"].isna())
    )
    n_mismatch = int(differs.sum())
    print(f"\nq3c_ang2ipix: {n_mismatch:,} mismatches out of {len(points):,} rows")
    print(
        f"  NULL ipix: A={int(ipix_a['ipix'].isna().sum())}, B={int(ipix_b['ipix'].isna().sum())}"
    )
    if n_mismatch:
        failed = True
        examples = points.loc[differs, ["id", "kind", "ra", "dec"]].copy()
        examples["ipix_a"] = ipix_a.loc[differs, "ipix"]
        examples["ipix_b"] = ipix_b.loc[differs, "ipix"]
        print(examples.groupby("kind").size().to_string())
        with pd.option_context("display.precision", 17, "display.width", 200):
            print(examples.head(20).to_string(index=False))

    print(
        f"\nq3c_radial_query, radius {CONE_RADIUS_DEG} deg. 'missed' and 'extra' "
        "are against the exact angular distance, ignoring points within "
        f"{RIM_TOLERANCE_DEG:g} deg of the rim:"
    )
    for (ra0, dec0), ids_a, ids_b in zip(cones, cones_a, cones_b, strict=True):
        same = np.array_equal(ids_a, ids_b)
        failed |= not same
        with np.errstate(invalid="ignore"):  # the non-finite rows
            dist = angular_distance(points["ra"], points["dec"], ra0, dec0)
        inside = dist < CONE_RADIUS_DEG - RIM_TOLERANCE_DEG
        outside = ~(dist <= CONE_RADIUS_DEG + RIM_TOLERANCE_DEG)
        line = f"  ({ra0:10.5f}, {dec0:+9.5f}):"
        for label, ids in (("A", ids_a), ("B", ids_b)):
            returned = np.zeros(len(points), dtype=bool)
            returned[ids] = True
            missed = int((inside & ~returned).sum())
            extra = int((outside & returned).sum())
            line += f" {label}={ids.size:6d} (missed {missed:5d}, extra {extra:3d})"
        print(f"{line} {'same' if same else 'DIFFERENT'}")
        if not same:
            only_a = np.setdiff1d(ids_a, ids_b)
            only_b = np.setdiff1d(ids_b, ids_a)
            print(f"    only in A: {only_a.size}, e.g. {only_a[:5].tolist()}")
            print(f"    only in B: {only_b.size}, e.g. {only_b[:5].tolist()}")
    return not failed


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("dsn_a", help="libpq URI of the first server")
    parser.add_argument("dsn_b", help="libpq URI of the second server")
    parser.add_argument("--seed", type=int, default=20261117)
    parser.add_argument("--n-uniform", type=int, default=5_000_000)
    args = parser.parse_args()
    ok = compare(args.dsn_a, args.dsn_b, args.seed, args.n_uniform)
    print("\nOK: identical" if ok else "\nFAIL: the two servers differ")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
