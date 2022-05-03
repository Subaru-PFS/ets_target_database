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


def generate_query_simple_boxsearch(
    ra1, ra2, dec1, dec2, tablename, good_fluxstd=True, extra_where=None
):
    # FIXME: I know this is too simple and stupid,
    #        but should be enough for the commissioning.
    #        In the future, more sophisticated method should be used (e.g., q3c).
    query_target = f"""SELECT * FROM {tablename}
    WHERE ra >= {ra1} AND ra < {ra2}
    AND dec >= {dec1} AND dec < {dec2}
    """
    if extra_where is not None:
        query_target += extra_where

    if tablename == "fluxstd" and good_fluxstd:
        query_target += f"""
        AND flags_dist IS FALSE
        AND flags_ebv IS FALSE
        AND prob_f_star > 0.5
        """
    query_target += ";"
    return query_target


def generate_query_list(
    ra,
    dec,
    dw_ra,
    dw,
    tablename,
    good_fluxstd=True,
    extra_where=None,
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

    for i in range(len(ra1)):
        q_tmp = generate_query_simple_boxsearch(
            ra1[i],
            ra2[i],
            dec1,
            dec2,
            tablename,
            good_fluxstd=good_fluxstd,
            extra_where=extra_where,
        )
        qlist.append(q_tmp)

    return qlist


def gen_list_from_targetdb(
    ra,
    dec,
    conf=None,
    tablename="target",
    fp_radius_degree=260.0 * 10.2 / 3600,  # "Radius" of PFS FoV in degree (?)
    fp_fudge_factor=1.5,  # fudge factor for search widths
    width=None,
    height=None,
    good_fluxstd=True,
    extra_where=None,
    # exptime=900.0,
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
        extra_where=extra_where,
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

    # tbl_tmp = Table.from_pandas(df)

    # tbl = Table()
    # tbl["ID"] = np.array(tbl_tmp["obj_id"], dtype=np.int64)
    # tbl["R.A."] = tbl_tmp["ra"]
    # tbl["Dec."] = tbl_tmp["dec"]
    # tbl["Epoch"] = tbl_tmp["epoch"]

    # if "effective_exptime" in tbl_tmp.colnames:
    #     tbl["Exposure Time"] = tbl_tmp["effective_exptime"]
    # else:
    #     tbl["Exposure Time"] = [exptime] * len(tbl["ID"])

    # if "priority" in tbl_tmp.colnames:
    #     tbl["Priority"] = np.array(tbl_tmp["priority"], dtype=int)

    # # FIXME: I think it is worth putting the table file in a non-tmp directory
    # with tempfile.NamedTemporaryFile(dir="/tmp", delete=False) as tmpfile:
    #     outfile = tmpfile.name
    # tbl.write(outfile, format="ascii.ecsv", overwrite=True)

    # if tablename == "fluxstd":
    #     tbl["psfFlux"] = [
    #         np.array(
    #             [
    #                 tbl_tmp["psf_flux_g"][i],
    #                 tbl_tmp["psf_flux_r"][i],
    #                 tbl_tmp["psf_flux_i"][i],
    #                 tbl_tmp["psf_flux_z"][i],
    #                 tbl_tmp["psf_flux_y"][i],
    #             ]
    #         )
    #         for i in range(len(tbl["ID"]))
    #     ]
    #     tbl["filterNames"] = [["g_ps1", "r_ps1", "i_ps1", "z_ps1", "y_ps1"]] * len(
    #         tbl["ID"]
    #     )
    # elif tablename == "target":
    #     tbl["psfFlux"] = [
    #         np.array(
    #             [
    #                 tbl_tmp["psf_flux_g"][i],
    #                 tbl_tmp["psf_flux_r"][i],
    #                 tbl_tmp["psf_flux_i"][i],
    #             ]
    #         )
    #         for i in range(len(tbl["ID"]))
    #     ]
    #     tbl["filterNames"] = [["g_hsc", "r_hsc", "i_hsc"]] * len(tbl["ID"])
    # tbl["target_type_id"] = tbl_tmp["target_type_id"]
    # tbl["input_catalog_id"] = tbl_tmp["input_catalog_id"]

    # print(tbl)

    # db.close()

    # return outfile, tbl


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

    # tbl_tmp = Table.from_pandas(df_res)

    # # ZPs are taken from Weiler (2018, A&A, 617, A138)
    # tbl_tmp["g_mag_ab"] = (tbl_tmp["phot_g_mean_mag"] + (25.7455 - 25.6409)) * u.ABmag
    # tbl_tmp["bp_mag_ab"] = (tbl_tmp["phot_bp_mean_mag"] + (25.3603 - 25.3423)) * u.ABmag
    # tbl_tmp["rp_mag_ab"] = (tbl_tmp["phot_rp_mean_mag"] + (25.1185 - 24.7600)) * u.ABmag

    # tbl_tmp["g_flux_njy"] = tbl_tmp["g_mag_ab"].to("nJy")
    # tbl_tmp["bp_flux_njy"] = tbl_tmp["bp_mag_ab"].to("nJy")
    # tbl_tmp["rp_flux_njy"] = tbl_tmp["rp_mag_ab"].to("nJy")

    # n_obj = tbl_tmp["source_id"].size

    # tbl = Table()
    # tbl["ID"] = tbl_tmp["source_id"]
    # tbl["R.A."] = tbl_tmp["ra"]
    # tbl["Dec."] = tbl_tmp["dec"]
    # tbl["Epoch"] = tbl_tmp["ref_epoch"]
    # tbl["Exposure Time"] = np.full(n_obj, 900.0)
    # tbl["Priority"] = np.full(n_obj, 1, dtype=int)

    # filternames = [["g_gaia", "bp_gaia", "rp_gaia"]] * n_obj
    # totalfluxes = np.empty(n_obj, dtype=object)

    # for i in range(n_obj):
    #     totalfluxes[i] = np.array(
    #         [
    #             tbl_tmp["g_flux_njy"][i],
    #             tbl_tmp["bp_flux_njy"][i],
    #             tbl_tmp["rp_flux_njy"][i],
    #         ]
    #     )

    # # FIXME: I think it is worth putting the table file in a non-tmp directory
    # with tempfile.NamedTemporaryFile(dir="/tmp", delete=False) as tmpfile:
    #     outfile = tmpfile.name
    # tbl.write(outfile, format="ascii.ecsv", overwrite=True)

    # tbl["totalFlux"] = totalfluxes
    # tbl["filterNames"] = filternames
    # tbl["target_type_id"] = np.full(n_obj, 1)  # 1: SCIENCE
    # tbl["input_catalog_id"] = np.full(n_obj, 2)  # 2: gaia_dr2

    # return outfile, tbl
