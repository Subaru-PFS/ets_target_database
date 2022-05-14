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

# import astropy
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
from logzero import logger
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


# astropy.utils.iers.conf.iers_degraded_accuracy = "warn"


def get_arguments():
    parser = argparse.ArgumentParser()

    # telescope configurations
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
        default=-90.0,
        help="Telescope position angle [degrees] (default: -90.0)",
    )
    parser.add_argument(
        "--observation_time",
        type=str,
        default="2022-05-20T15:00:00Z",
        help="planned time of observation in UTC (default: 2022-05-20T15:00:00Z)",
    )
    parser.add_argument(
        "--telescope_elevation",
        type=float,
        default=None,
        help="Telescope elevation in degree (default: None to set automatically from (ra, dec, observation_time))",
    )
    parser.add_argument(
        "--arms",
        type=str,
        default="br",
        help="Spectrograph arms to expose, such as 'brn' and 'bmn' (default: 'br')",
    )

    # configuration file
    parser.add_argument(
        "--conf",
        type=str,
        default="config.toml",
        help="Config file for the script to run. Must be a .toml file (default: config.toml)",
    )

    # output directories
    parser.add_argument(
        "--design_dir",
        type=str,
        default=".",
        help="directory for storing pfsDesign files (default: .)",
    )
    parser.add_argument(
        "--cobra_coach_dir",
        type=str,
        default=".",
        help="path for temporary cobraCoach files (default: .)",
    )

    # guide stars
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

    # science targets
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

    # flux standards
    parser.add_argument(
        "--fluxstd_mag_max",
        type=float,
        default=19.0,
        help="Maximum (faintest) magnitude for stars in fibers (default: 19.)",
    )
    parser.add_argument(
        "--fluxstd_mag_min",
        type=float,
        default=14.0,
        help="Minimum (brightest) magnitude for stars in fibers (default: 14.0)",
    )
    parser.add_argument(
        "--fluxstd_mag_filter",
        type=str,
        default="g",
        help="Photometric band (grizyj of PS1) to apply magnitude cuts (default: g)",
    )
    parser.add_argument(
        "--good_fluxstd",
        action="store_true",
        help="Select fluxstd stars with prob_f_star>0.5, flags_dist=False, and flags_ebv=False (default: False)",
    )
    parser.add_argument(
        "--fluxstd_min_prob_f_star",
        type=float,
        default=0.5,
        help="Minimum acceptable prob_f_star (default: 0.5)",
    )
    parser.add_argument(
        "--fluxstd_flags_dist",
        action="store_true",
        help="Select fluxstd stars with flags_dist=False (default: False)",
    )
    parser.add_argument(
        "--fluxstd_flags_ebv",
        action="store_true",
        help="Select fluxstd stars with flags_ebv=False (default: False)",
    )
    parser.add_argument(
        "--n_fluxstd",
        type=int,
        default=50,
        help="Number of FLUXSTD stars to be allocated. (default: 50)",
    )

    # sky fibers
    parser.add_argument(
        "--n_sky",
        type=int,
        default=0,
        help="Number of SKY fibers to be allocated. (default: 0)",
    )

    # instrument parameter files
    parser.add_argument(
        "--pfs_instdata_dir",
        type=str,
        default="/Users/monodera/Dropbox/NAOJ/PFS/Subaru-PFS/pfs_instdata/",
        help="Location of pfs_instdata (default: /Users/monodera/Dropbox/NAOJ/PFS/Subaru-PFS/pfs_instdata/)",
    )
    parser.add_argument(
        "--cobra_coach_module_version",
        type=str,
        default=None,
        help="version of the bench description file (default: None)",
    )

    args = parser.parse_args()

    # NOTE: astropy.time.Time.now() uses datetime.utcnow()
    if args.observation_time.lower() == "now":
        logger.info("Observation time is set to the current time.")
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

    df_targets = dbutils.generate_targets_from_targetdb(
        args.ra, args.dec, conf=conf, arms=args.arms
    )
    df_fluxstds = dbutils.generate_fluxstds_from_targetdb(
        args.ra,
        args.dec,
        conf=conf,
        good_fluxstd=args.good_fluxstd,
        flags_dist=args.fluxstd_flags_dist,
        flags_ebv=args.fluxstd_flags_ebv,
        mag_min=args.fluxstd_mag_min,
        mag_max=args.fluxstd_mag_max,
        mag_filter=args.fluxstd_mag_filter,
        min_prob_f_star=args.fluxstd_min_prob_f_star,
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
    vis, tp, tel, tgt, tgt_class_dict = nfutils.fiber_allocation(
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
        arms=args.arms,
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

    logger.info(
        f"pfsDesign file {design.filename} is created in the {args.design_dir} directory."
    )
    logger.info(
        "Number of SCIENCE fibers: {:}".format(len(np.where(design.targetType == 1)[0]))
    )
    logger.info(
        "Number of FLUXSTD fibers: {:}".format(len(np.where(design.targetType == 3)[0]))
    )
    logger.info(
        "Number of SKY fibers: {:}".format(len(np.where(design.targetType == 2)[0]))
    )
    logger.info("Number of AG stars: {:}".format(len(guidestars.objId)))


if __name__ == "__main__":
    main()
