#!/usr/bin/env python3

import configparser
import tempfile
import time

import numpy as np
import pandas as pd
import psycopg2
import psycopg2.extras
from astropy import units as u
from astropy.table import Table
from astropy.time import Time
from targetdb import targetdb


def connect_subaru_gaiadb(conf=None):
    conn = psycopg2.connect(**dict(conf["gaiadb"]))
    return conn


def connect_targetdb(conf=None):
    db = targetdb.TargetDB(**dict(conf["targetdb"]))
    db.connect()
    return db


# def generate_query_simple_boxsearch(
#     ra1,
#     ra2,
#     dec1,
#     dec2,
#     tablename,
#     # good_fluxstd=False,
#     extra_where=None,
#     # mag_min=None,
#     # mag_max=None,
#     # mag_filter=None,
#     # min_prob_f_star=None,
# ):
#     # FIXME: I know this is too simple and stupid,
#     #        but should be enough for the commissioning.
#     #        In the future, more sophisticated method should be used (e.g., q3c).
#     query_target = f"""SELECT * FROM {tablename}
#     WHERE ra >= {ra1} AND ra < {ra2}
#     AND dec >= {dec1} AND dec < {dec2}
#     """
#     if extra_where is not None:
#         query_target += extra_where

#     query_target += ";"
#     return query_target


def generate_query_list(
    ra,
    dec,
    dw_ra,
    dw,
    tablename,
    good_fluxstd=False,
    flags_dist=False,
    flags_ebv=False,
    extra_where=None,
    mag_min=None,
    mag_max=None,
    mag_filter=None,
    min_prob_f_star=None,
):

    dec1, dec2 = dec - dw, dec + dw
    qlist = []

    if ra - dw_ra < 0.0:
        ra1 = [0.0, ra - dw_ra + 360.0]
        ra2 = [ra + dw_ra, 360.0]
    elif ra + dw_ra >= 360.0:
        ra1 = [0.0, ra - dw_ra]
        ra2 = [ra + dw_ra - 360.0, 360.0]
    else:
        ra1, ra2 = [ra - dw_ra], [ra + dw_ra]

    if tablename == "target":
        for i in range(len(ra1)):
            query_target = f"""SELECT * FROM {tablename}
    WHERE ra >= {ra1[i]} AND ra < {ra2[i]}
    AND dec >= {dec1} AND dec < {dec2}
    """
            if extra_where is not None:
                query_target += extra_where

            query_target += ";"

            qlist.append(query_target)

        return qlist

    if tablename == "fluxstd":
        for i in range(len(ra1)):
            query_target = f"""SELECT * FROM {tablename}
    WHERE ra >= {ra1[i]} AND ra < {ra2[i]}
    AND dec >= {dec1} AND dec < {dec2}
    """
            if extra_where is None:
                extra_where = ""
            if good_fluxstd:
                extra_where += f"""
                AND flags_dist IS FALSE
                AND flags_ebv IS FALSE
                AND prob_f_star > 0.5
                AND psf_mag_{mag_filter} BETWEEN {mag_min} AND {mag_max}
                """
            if not good_fluxstd:
                extra_where = f"""
                AND psf_mag_{mag_filter} BETWEEN {mag_min} AND {mag_max}
                AND prob_f_star > {min_prob_f_star}
                """
                if flags_dist:
                    extra_where += f"""
                    AND flags_dist IS FALSE
                    """
                if flags_ebv:
                    extra_where += f"""
                    AND flags_ebv IS FALSE
                    """
            query_target += extra_where

            query_target += ";"

            qlist.append(query_target)

        return qlist


def generate_targets_from_targetdb(
    ra,
    dec,
    conf=None,
    tablename="target",
    fp_radius_degree=260.0 * 10.2 / 3600,  # "Radius" of PFS FoV in degree (?)
    fp_fudge_factor=1.5,  # fudge factor for search widths
    width=None,
    height=None,
    extra_where=None,
    mag_min=None,
    mag_max=None,
    mag_filter=None,
):

    db = connect_targetdb(conf)

    dw = fp_radius_degree * fp_fudge_factor

    # consider the cosine term
    cos_term = 1.0 / np.cos(dec * u.deg)

    if width is None:
        dw_ra = dw * cos_term
    else:
        dw_ra = width * cos_term / 2.0

    if height is not None:
        dw = height / 2.0

    qlist = generate_query_list(
        ra,
        dec,
        dw_ra,
        dw,
        tablename,
        extra_where=extra_where,
        mag_min=mag_min,
        mag_max=mag_max,
        mag_filter=mag_filter,
    )

    df = pd.DataFrame()

    for q in qlist:
        print(q)
        t_begin = time.time()
        df_tmp = db.fetch_query(q)
        t_end = time.time()
        print("Time spent for querying: {:f}".format(t_end - t_begin))
        df = pd.concat([df, df_tmp], ignore_index=True)

    print(df)

    db.close()

    return df


def generate_fluxstds_from_targetdb(
    ra,
    dec,
    conf=None,
    tablename="fluxstd",
    fp_radius_degree=260.0 * 10.2 / 3600,  # "Radius" of PFS FoV in degree (?)
    fp_fudge_factor=1.5,  # fudge factor for search widths
    width=None,
    height=None,
    good_fluxstd=False,
    flags_dist=False,
    flags_ebv=False,
    mag_min=None,
    mag_max=None,
    mag_filter=None,
    min_prob_f_star=None,
    extra_where=None,
):

    db = connect_targetdb(conf)

    dw = fp_radius_degree * fp_fudge_factor

    # consider the cosine term
    cos_term = 1.0 / np.cos(dec * u.deg)

    if width is None:
        dw_ra = dw * cos_term
    else:
        dw_ra = width * cos_term / 2.0

    if height is not None:
        dw = height / 2.0

    qlist = generate_query_list(
        ra,
        dec,
        dw_ra,
        dw,
        tablename,
        good_fluxstd=good_fluxstd,
        flags_dist=flags_dist,
        flags_ebv=flags_ebv,
        extra_where=extra_where,
        mag_min=mag_min,
        mag_max=mag_max,
        mag_filter=mag_filter,
        min_prob_f_star=min_prob_f_star,
    )

    df = pd.DataFrame()

    for q in qlist:
        print(q)
        t_begin = time.time()
        df_tmp = db.fetch_query(q)
        t_end = time.time()
        print("Time spent for querying: {:f}".format(t_end - t_begin))
        df = pd.concat([df, df_tmp], ignore_index=True)

    print(df)

    db.close()

    return df


def gen_list_from_gaiadb(
    ra,
    dec,
    conf=None,
    fp_radius_degree=260.0 * 10.2 / 3600,  # "Radius" of PFS FoV in degree (?)
    fp_fudge_factor=1.5,  # fudge factor for search widths
    search_radius=None,
    band_select="phot_g_mean_mag",
    mag_min=0.0,
    mag_max=99.0,
):

    conn = connect_subaru_gaiadb(conf)
    cur = conn.cursor()

    if search_radius is None:
        search_radius = fp_radius_degree * fp_fudge_factor

    query_string = f"""SELECT source_id,ref_epoch,ra,dec,pmra,pmdec,phot_g_mean_mag,phot_bp_mean_mag,phot_rp_mean_mag
    FROM gaia
    WHERE q3c_radial_query(ra, dec, {ra}, {dec}, {search_radius})
    AND {band_select} BETWEEN {mag_min} AND {mag_max};
    """

    cur.execute(query_string)

    df_res = pd.DataFrame(
        cur.fetchall(),
        columns=[
            "source_id",
            "ref_epoch",
            "ra",
            "dec",
            "pmra",
            "pmdec",
            "phot_g_mean_mag",
            "phot_bp_mean_mag",
            "phot_rp_mean_mag",
        ],
    )

    cur.close()
    conn.close()

    print(df_res)

    return df_res
