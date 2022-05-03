# Script for commissioning runs 09/2021

# Necessary preparations for running:
#
# This script depends on several other modules from https://github.com/Subaru-PFS
# All of them were at the HEAD of the respective master branches, with the
# exception of "ets_fiber_assigner" (must be on branch "commissioning_demo").
#
# Also the "pulp" Python package (version 1.6!) is required to solve the fiber assignment
# problem.
#
# Also, the environment variable PFS_INSTDATA_DIR must be set correctly.

import argparse
import os
import tempfile
import time

import ets_fiber_assigner.netflow as nf
import matplotlib.path as mppath
import numpy as np
import pandas as pd
import pfs.datamodel
import psycopg2
import psycopg2.extras
import toml
from astropy import units as u
from astropy.table import Table
from astropy.time import Time
from ets_shuffle import query_utils
from ets_shuffle.convenience import flag_close_pairs
from ets_shuffle.convenience import guidecam_geometry
from ets_shuffle.convenience import update_coords_for_proper_motion
from ics.cobraOps.Bench import Bench
from ics.cobraOps.BlackDotsCalibrationProduct import BlackDotsCalibrationProduct
from ics.cobraOps.cobraConstants import NULL_TARGET_ID
from ics.cobraOps.cobraConstants import NULL_TARGET_POSITION
from ics.cobraOps.CollisionSimulator2 import CollisionSimulator2
from ics.cobraOps.TargetGroup import TargetGroup
from pfs.utils.coordinates.CoordTransp import CoordinateTransform as ctrans
from pfs.utils.coordinates.CoordTransp import ag_pfimm_to_pixel
from pfs.utils.pfsDesignUtils import makePfsDesign
from procedures.moduleTest.cobraCoach import CobraCoach
from targetdb import targetdb

import pointing_utils.dbutils as dbutils
import pointing_utils.designutils as designutils
import pointing_utils.nfutils as nfutils

# from pointing_utils import gen_list_from_gaiadb
# from pointing_utils import gen_list_from_targetdb


def get_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--ra",
        type=float,
        default=0.0,
        help="Telescope center RA [degrees] (default: 0.0)",
    )
    parser.add_argument(
        "--dec",
        type=float,
        default=0.0,
        help="Telescope center Dec [degrees] (default: 0.0)",
    )
    parser.add_argument(
        "--pa",
        type=float,
        default=0.0,
        help="Telescope position angle [degrees] (default: 0.0)",
    )
    parser.add_argument(
        "--observation_time",
        type=str,
        default="2022-05-20T15:00:00Z",
        help="planned time of observation in UTC (default: 2022-05-20T15:00:00Z)",
    )
    parser.add_argument(
        "--lim_target_mag",
        type=float,
        default="19.",
        help="magnitude of the faintest targets (obsolete) (default:19)",
    )

    parser.add_argument(
        "--design_dir",
        type=str,
        default=".",
        help="directory for storing pfsDesign files (default: .)",
    )

    parser.add_argument(
        "--guidestar_mag_max",
        type=float,
        default=19.0,
        help="maximum magnitude for guide star candidates (default: 19.)",
    )
    parser.add_argument(
        "--guidestar_neighbor_mag_min",
        type=float,
        default=21.0,
        help="minimum magnitude for objects in the vicinity of guide star candidates (default: 21.)",
    )
    parser.add_argument(
        "--guidestar_minsep_deg",
        type=float,
        default=1.0 / 3600,
        help="radius of guide star candidate vicinity (default: 1/3600)",
    )

    parser.add_argument(
        "--cobra_coach_dir",
        type=str,
        default=".",
        help="path for temporary cobraCoach files (default: .)",
    )

    parser.add_argument(
        "--cobra_coach_module_version",
        type=str,
        default="final_20210920_mm",
        help="version of the bench decription file (default: final_20210920_mm)",
    )

    parser.add_argument(
        "--conf",
        type=str,
        default="config.toml",
        help="Config file for the script to run. Must be a .toml file (default: config.toml)",
    )
    parser.add_argument(
        "--target_mag_max",
        type=float,
        default=19.0,
        help="Maximum (faintest) magnitude for stars in fibers (default: 19.)",
    )
    parser.add_argument(
        "--target_mag_min",
        type=float,
        default=0.0,
        help="Minimum (brightest) magnitude for stars in fibers (default: 0)",
    )
    parser.add_argument(
        "--target_mag_filter",
        type=str,
        default="g",
        help="Photometric band (grizyj of PS1) to apply magnitude cuts (default: g)",
    )
    parser.add_argument(
        "--fluxstd_min_prob_f_star",
        type=float,
        default=0.0,
        help="Minimum acceptable prob_f_star (default: 0)",
    )
    parser.add_argument(
        "--telescope_elevation",
        type=float,
        default=60.0,
        help="Telescope elevation in degree (default: 60)",
    )
    parser.add_argument(
        "--n_fluxstd",
        type=int,
        default=50,
        help="Number of FLUXSTD stars to be allocated. (default: 50)",
    )
    parser.add_argument(
        "--n_sky",
        type=int,
        default=0,
        help="Number of SKY fibers to be allocated. (default: 0)",
    )
    parser.add_argument(
        "--pfs_instdata_dir",
        type=str,
        default="/Users/monodera/Dropbox/NAOJ/PFS/Subaru-PFS/pfs_instdata/",
        help="Location of pfs_instdata (default: /Users/monodera/Dropbox/NAOJ/PFS/Subaru-PFS/pfs_instdata/)",
    )

    args = parser.parse_args()

    if args.observation_time.lower() == "now":
        print("converting to the current time")
        # NOTE: astropy.time.Time.now() uses datetime.utcnow()
        args.observation_time = Time.now().iso

    return args


def read_conf(conf):
    config = toml.load(conf)
    return config


def main():

    args = get_arguments()

    print(args)
    # exit()

    conf = read_conf(args.conf)

    print(dict(conf["gurobi"]))

    for d in [args.design_dir, args.cobra_coach_dir]:
        try:
            os.makedirs(d, exist_ok=False)
        except:
            pass

    df_targets = dbutils.gen_list_from_targetdb(
        args.ra, args.dec, conf=conf, tablename="target"
    )
    df_fluxstds = dbutils.gen_list_from_targetdb(
        args.ra, args.dec, conf=conf, tablename="fluxstd", good_fluxstd=True
    )
    df_sky = pd.DataFrame()

    # no need for the 2022 May commissioing (hopefully)
    # listname_gaia_targets, tbl_gaia_targets = gen_list_from_gaiadb(
    #     args.ra,
    #     args.dec,
    #     dbconf=args.gaiadb_conf,
    #     mag_min=args.target_mag_min,
    #     mag_max=args.target_mag_max,
    # )

    # vis, tp, tel, tgt, classdict = gen_assignment(args, df_targets, df_fluxstds)
    vis, tp, tel, tgt, tgt_class_dict = nfutils.gen_assignment(
        df_targets,
        df_fluxstds,
        df_sky,
        args.ra,
        args.dec,
        args.pa,
        args.n_fluxstd,
        args.n_sky,
        args.observation_time,
        conf,
        args.pfs_instdata_dir,
        args.cobra_coach_dir,
        args.cobra_coach_module_version,
    )
    # print(vis, tp, tel, tgt, tgt_classdict)

    design = designutils.generate_pfs_design(
        df_targets,
        df_fluxstds,
        df_sky,
        vis,
        tp,
        tel,
        tgt,
        tgt_class_dict,
        # tbl_targets,
        # tbl_fluxstds,
    )
    guidestars = designutils.generate_guidestars_from_gaiadb(
        args.ra,
        args.dec,
        args.pa,
        args.observation_time,
        args.telescope_elevation,
        conf=conf,
        guidestar_mag_max=args.guidestar_mag_max,
        guidestar_neighbor_mag_min=args.guidestar_neighbor_mag_min,
        guidestar_minsep_deg=args.guidestar_minsep_deg,
        # gaiadb_epoch=2015.0,
        # gaiadb_input_catalog_id=2,
    )

    design.guideStars = guidestars

    design.write(dirName=args.design_dir, fileName=design.filename)

    print(
        f"pfsDesign file {design.filename} is created in the {args.design_dir} directory."
    )


if __name__ == "__main__":
    main()
