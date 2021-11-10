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

# import argparse

import time

import numpy as np


# This was needed for fixing some issues with the XML files.
# Can probably be simplified. Javier?
def getBench(args):
    import os

    from ics.cobraOps.Bench import Bench
    from ics.cobraOps.BlackDotsCalibrationProduct import BlackDotsCalibrationProduct
    from procedures.moduleTest.cobraCoach import CobraCoach

    # os.environ["PFS_INSTDATA_DIR"] = "/home/martin/codes/pfs_instdata"
    os.environ[
        "PFS_INSTDATA_DIR"
    ] = "/Users/monodera/Dropbox/NAOJ/PFS/Subaru-PFS/pfs_instdata/"
    cobraCoach = CobraCoach(
        "fpga", loadModel=False, trajectoryMode=True, rootDir=args.cobra_coach_dir
    )
    cobraCoach.loadModel(version="ALL", moduleVersion=args.cobra_coach_module_version)

    # Get the calibration product
    calibrationProduct = cobraCoach.calibModel

    # Set some dummy center positions and phi angles for those cobras that have
    # zero centers
    zeroCenters = calibrationProduct.centers == 0
    calibrationProduct.centers[zeroCenters] = np.arange(np.sum(zeroCenters)) * 300j
    calibrationProduct.phiIn[zeroCenters] = -np.pi
    calibrationProduct.phiOut[zeroCenters] = 0
    print("Cobras with zero centers: %i" % np.sum(zeroCenters))

    # Use the median value link lengths in those cobras with zero link lengths
    zeroLinkLengths = np.logical_or(
        calibrationProduct.L1 == 0, calibrationProduct.L2 == 0
    )
    calibrationProduct.L1[zeroLinkLengths] = np.median(
        calibrationProduct.L1[~zeroLinkLengths]
    )
    calibrationProduct.L2[zeroLinkLengths] = np.median(
        calibrationProduct.L2[~zeroLinkLengths]
    )
    print("Cobras with zero link lenghts: %i" % np.sum(zeroLinkLengths))

    # Use the median value link lengths in those cobras with too long link lengths
    tooLongLinkLengths = np.logical_or(
        calibrationProduct.L1 > 100, calibrationProduct.L2 > 100
    )
    calibrationProduct.L1[tooLongLinkLengths] = np.median(
        calibrationProduct.L1[~tooLongLinkLengths]
    )
    calibrationProduct.L2[tooLongLinkLengths] = np.median(
        calibrationProduct.L2[~tooLongLinkLengths]
    )
    print("Cobras with too long link lenghts: %i" % np.sum(tooLongLinkLengths))

    calibrationFileName = os.path.join(
        os.environ["PFS_INSTDATA_DIR"], "data/pfi/dot", "black_dots_mm.csv"
    )
    blackDotsCalibrationProduct = BlackDotsCalibrationProduct(calibrationFileName)

    # Create the bench instance
    bench = Bench(
        layout="calibration",
        calibrationProduct=calibrationProduct,
        blackDotsCalibrationProduct=blackDotsCalibrationProduct,
    )
    print("Number of cobras:", bench.cobras.nCobras)

    return cobraCoach, bench


def get_arguments():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ra", type=float, default=0.0, help="Telescope center RA [degrees]"
    )
    parser.add_argument(
        "--dec", type=float, default=0.0, help="Telescope center Dec [degrees]"
    )
    parser.add_argument(
        "--pa", type=float, default=0.0, help="Telescope position angle [degrees]"
    )
    parser.add_argument(
        "--observation_time",
        type=str,
        default="2020-01-01 15:00:00",
        help="planned time of observation",
    )
    parser.add_argument(
        "--run_id", type=int, default=42, help="numerical identifier for this run"
    )

    parser.add_argument(
        "--lim_target_mag",
        type=float,
        default="19.",
        help="magnitude of the faintest targets",
    )

    parser.add_argument(
        "--design_dir", type=str, default=".", help="directory for storing PFS designs"
    )

    parser.add_argument(
        "--guidestar_mag_max",
        type=float,
        default=19.0,
        help="maximum magnitude for guide star candidates",
    )
    parser.add_argument(
        "--guidestar_neighbor_mag_min",
        type=float,
        default=21.0,
        help="minimum magnitude for objects in the vicinity of guide star candidates",
    )
    parser.add_argument(
        "--guidestar_minsep_deg",
        type=float,
        default=1.0 / 3600,
        help="radius of guide star candidate vicinity",
    )

    parser.add_argument(
        "--use_gurobi",
        # type=bool,
        # default=False,
        action="store_true",
        help="use Gurobi solver instead of PuLP",
    )
    parser.add_argument(
        "--cobra_coach_dir",
        type=str,
        default=".",
        help="path for temporary cobraCoach files",
    )

    parser.add_argument(
        "--cobra_coach_module_version",
        type=str,
        default="final_20210920_mm",
        help="version of the bench decription file",
    )

    parser.add_argument(
        "--targetdb_conf",
        type=str,
        default="../../../database_configs/targetdb_config.ini",
        help="Config file for targetDB",
    )

    parser.add_argument(
        "--gaiadb_conf",
        type=str,
        default="../../../database_configs/gaiadb_config_hilo.ini",
        help="Config file for Subaru's Gaia DB",
    )

    args = parser.parse_args()
    return args


def gen_target_list_from_targetdb(args):

    import configparser

    import pandas as pd
    from astropy import units as u
    from astropy.table import Table
    from targetdb import targetdb

    # from ets_shuffle import query_utils
    # from targetdb import models

    def connect_db(conf=None):

        config = configparser.ConfigParser()
        config.read(conf)
        # print(dict(config["dbinfo"]))
        db = targetdb.TargetDB(**dict(config["dbinfo"]))
        db.connect()
        return db

    def generate_query_simple_boxsearch(ra1, ra2, dec1, dec2):
        # FIXME: I know this is too simple and stupid,
        #        but should be enough for the November 2021 commissioning run.
        query_target = """SELECT
    obj_id,
    ra,
    dec,
    priority,
    effective_exptime
    FROM target
    WHERE ra >= {:f} AND ra < {:f}
    AND dec >= {:f} AND dec < {:f}
    AND prob_f_star > 0.;
    """.format(
            ra1, ra2, dec1, dec2
        )
        return query_target

    db = connect_db(args.targetdb_conf)

    fp_rad_deg = 260.0 * 10.2 / 3600
    fp_fudge_factor = 1.5

    dw = fp_rad_deg * fp_fudge_factor

    cos_term = 1.0 / np.cos(args.dec * u.deg)

    dw_ra = dw * cos_term

    dec1, dec2 = args.dec - dw, args.dec + dw

    if args.ra - dw_ra < 0.0:
        ra1, ra2 = 0.0, args.ra + dw_ra
        q1 = generate_query_simple_boxsearch(ra1, ra2, dec1, dec2)
        ra1, ra2 = args.ra - dw_ra + 360.0, 360.0
        q2 = generate_query_simple_boxsearch(ra1, ra2, dec1, dec2)
        qlist = [q1, q2]
    elif args.ra + dw_ra >= 360.0:
        ra1, ra2 = 0.0, args.ra + dw_ra - 360.0
        q1 = generate_query_simple_boxsearch(ra1, ra2, dec1, dec2)
        ra1, ra2 = args.ra - dw_ra, 360.0
        q2 = generate_query_simple_boxsearch(ra1, ra2, dec1, dec2)
        qlist = [q1, q2]
    else:
        ra1, ra2 = args.ra - dw_ra, args.ra + dw_ra
        q1 = generate_query_simple_boxsearch(ra1, ra2, dec1, dec2)
        qlist = [q1]

    # print(qlist)

    df = pd.DataFrame(columns=["obj_id", "ra", "dec", "priority", "effective_exptime"])

    for q in qlist:
        t_begin = time.time()
        df_tmp = db.fetch_query(q)
        t_end = time.time()
        print("Time spent for querying: {:f}".format(t_end - t_begin))
        # print(df_tmp)
        df = df.append(df_tmp, ignore_index=True)

    print(df)

    tbl_tmp = Table.from_pandas(df)

    tbl = Table()
    tbl["ID"] = tbl_tmp["obj_id"]
    tbl["R.A."] = tbl_tmp["ra"]
    tbl["Dec."] = tbl_tmp["dec"]
    tbl["Exposure Time"] = tbl_tmp["effective_exptime"]
    tbl["Priority"] = np.array(tbl_tmp["priority"], dtype=int)
    tbl.write(
        "{:s}_targets.txt".format(str(args.run_id)),
        format="ascii.ecsv",
        overwrite=True,
    )

    db.close()


def gen_target_list(args):
    from astropy.table import Table
    from ets_shuffle import query_utils

    fp_rad_deg = 260.0 * 10.2 / 3600
    conn, table, coldict = query_utils.openGAIA2connection()
    racol, deccol = coldict["ra"], coldict["dec"]
    req_columns = [coldict["id"], racol, deccol, "phot_g_mean_mag"]
    constraints = [
        query_utils.build_circle_query(args.ra, args.dec, fp_rad_deg * 1.2, coldict),
        query_utils.build_mag_query(args.lim_target_mag, 0, "phot_g_mean_mag"),
    ]
    res = query_utils.run_query(conn, table, req_columns, constraints)
    tbl = Table()
    tbl["ID"] = res[coldict["id"]]
    tbl["R.A."] = res[racol]
    tbl["Dec."] = res[deccol]
    tbl["Exposure Time"] = np.full(res[deccol].shape, 900.0, dtype=np.float64)
    tbl["Priority"] = np.full(res[deccol].shape, 1, dtype=np.int64)
    tbl.write(str(args.run_id) + "_targets.txt", format="ascii.ecsv", overwrite=True)
    # tbl.write(str(args.run_id) + "_targets.fits", overwrite=True)


def gen_assignment(args):
    import ets_fiber_assigner.netflow as nf
    from ics.cobraOps.cobraConstants import NULL_TARGET_ID
    from ics.cobraOps.cobraConstants import NULL_TARGET_POSITION
    from ics.cobraOps.CollisionSimulator2 import CollisionSimulator2
    from ics.cobraOps.TargetGroup import TargetGroup

    tgt = nf.readScientificFromFile(str(args.run_id) + "_targets.txt", "sci")
    cobraCoach, bench = getBench(args)
    telescopes = [nf.Telescope(args.ra, args.dec, args.pa, args.observation_time)]

    # get focal plane positions for all targets and all visits
    tpos = [tele.get_fp_positions(tgt) for tele in telescopes]

    # create the dictionary containing the costs and constraints for all classes
    # of targets
    # For the purpose of this demonstration we assume that all targets are
    # scientific targets with priority 1.
    classdict = {}
    classdict["sci_P1"] = {
        "nonObservationCost": 100,
        "partialObservationCost": 1000,
        "calib": False,
    }
    tclassdict = {"sci_P1": 1}

    t_obs = 900.0

    alreadyObserved = {}
    forbiddenPairs = []
    for i in range(1):
        forbiddenPairs.append([])

    # We penalize targets near the edge of a patrol region slightly to reduce
    # the chance of endpoint collisions with unllocated Cobras
    # (see note below).
    def cobraMoveCost(dist):
        return 0.1 * dist

    gurobiOptions = dict(
        seed=0,
        presolve=1,
        method=4,
        degenmoves=0,
        heuristics=0.8,
        mipfocus=0,
        mipgap=1.0e-04,
    )

    done = False
    while not done:
        # compute observation strategy
        prob = nf.buildProblem(
            bench,
            tgt,
            tpos,
            classdict,
            t_obs,
            None,
            cobraMoveCost=cobraMoveCost,
            collision_distance=2.0,
            elbow_collisions=True,
            gurobi=args.use_gurobi,
            gurobiOptions=gurobiOptions if args.use_gurobi else None,
            alreadyObserved=alreadyObserved,
            forbiddenPairs=forbiddenPairs,
        )

        print("solving the problem")
        prob.solve()

        # extract solution
        res = [{} for _ in range(1)]
        for k1, v1 in prob._vardict.items():
            if k1.startswith("Tv_Cv_"):
                visited = prob.value(v1) > 0
                if visited:
                    _, _, tidx, cidx, ivis = k1.split("_")
                    res[int(ivis)][int(tidx)] = int(cidx)

        # NOTE: the following block would normally be used to "fix" the trajectory
        # collisions detected by the collision simulator.
        # However, this does not work currently, since the current version of
        # cobraCharmer does not actively move unassigned Cobras out of the way of
        # assigned ones, which can result in endpoint collisions which the fiber
        # assigner itself cannot avoid (since it does not know anything about the
        # positioning of unassigned Cobras).
        # So we skip this for now, hoping that it will become possible again with future
        # releases of cobraCharmer.

        print("Checking for trajectory collisions")
        ncoll = 0
        for ivis, (vis, tp) in enumerate(zip(res, tpos)):
            selectedTargets = np.full(len(bench.cobras.centers), NULL_TARGET_POSITION)
            ids = np.full(len(bench.cobras.centers), NULL_TARGET_ID)
            for tidx, cidx in vis.items():
                selectedTargets[cidx] = tp[tidx]
                ids[cidx] = ""
            for i in range(selectedTargets.size):
                if selectedTargets[i] != NULL_TARGET_POSITION:
                    dist = np.abs(selectedTargets[i] - bench.cobras.centers[i])

            simulator = CollisionSimulator2(
                bench, cobraCoach, TargetGroup(selectedTargets, ids)
            )
            simulator.run()
            # If you want to see the result of the collision simulator, uncomment the next three lines
            #            from ics.cobraOps import plotUtils
            #            simulator.plotResults(paintFootprints=False)
            #            plotUtils.pauseExecution()

            #            if np.any(simulator.endPointCollisions):
            #                print("ERROR: detected end point collision, which should be impossible")
            #                raise RuntimeError()
            coll_tidx = []
            for tidx, cidx in vis.items():
                if simulator.collisions[cidx]:
                    coll_tidx.append(tidx)
            ncoll += len(coll_tidx)
            for i1 in range(0, len(coll_tidx)):
                found = False
                for i2 in range(i1 + 1, len(coll_tidx)):
                    if np.abs(tp[coll_tidx[i1]] - tp[coll_tidx[i2]]) < 10:
                        forbiddenPairs[ivis].append((coll_tidx[i1], coll_tidx[i2]))
                        found = True
                if not found:  # not a collision between two active Cobras
                    forbiddenPairs[ivis].append((coll_tidx[i1],))

        print("trajectory collisions found:", ncoll)
        done = ncoll == 0

    # assignment done; write pfsDesign.
    import ets_fiber_assigner.io_helpers

    ets_fiber_assigner.io_helpers.writePfsDesign(
        pfsDesignId=args.run_id,
        pfsDesignDirectory=args.design_dir,
        vis=res[0],
        tp=tpos[0],
        tel=telescopes[0],
        tgt=tgt,
        classdict=tclassdict,
    )


def add_guidestars_from_gaiadb(args):
    import configparser

    import matplotlib.path as mppath
    import pandas as pd
    import pfs.datamodel
    import psycopg2
    import psycopg2.extras
    from astropy import units as u
    from astropy.table import Table
    from astropy.time import Time
    from ets_shuffle import query_utils
    from ets_shuffle.convenience import flag_close_pairs
    from ets_shuffle.convenience import guidecam_geometry
    from ets_shuffle.convenience import plot_focal_plane
    from ets_shuffle.convenience import update_coords_for_proper_motion
    from pfs.utils.coordinates.CoordTransp import CoordinateTransform as ctrans
    from pfs.utils.coordinates.CoordTransp import ag_pfimm_to_pixel
    from targetdb import targetdb

    # from ets_shuffle import query_utils
    # from targetdb import models

    def connect_gaiadb(conf=None):

        config = configparser.ConfigParser()
        config.read(conf)
        # print(dict(config["dbinfo"]))

        conn = psycopg2.connect(**dict(config["dbinfo"]))
        # db = targetdb.TargetDB(**dict(config["dbinfo"]))
        # db.connect()
        return conn

    input_design = pfs.datamodel.PfsDesign.read(args.run_id, args.design_dir)
    raTel_deg, decTel_deg, pa_deg = (
        input_design.raBoresight,
        input_design.decBoresight,
        input_design.posAng,
    )

    # this should come from the pfsDesign as well, but is not yet in there
    # (DAMD-101)
    obs_time = args.observation_time

    guidestar_mag_max = args.guidestar_mag_max
    guidestar_neighbor_mag_min = args.guidestar_neighbor_mag_min
    guidestar_minsep_deg = args.guidestar_minsep_deg

    # guide star cam geometries
    agcoord = guidecam_geometry()

    # internal, technical parameters
    # set focal plane radius
    fp_rad_deg = 260.0 * 10.2 / 3600
    fp_fudge_factor = 1.2

    # Find guide star candidates

    conn = connect_gaiadb(args.gaiadb_conf)
    # cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur = conn.cursor()

    coldict = {
        "ra": "ra",
        "dec": "dec",
        "pmra": "pmra",
        "pmdec": "pmdec",
        "id": "source_id",
    }
    racol, deccol = coldict["ra"], coldict["dec"]
    req_columns = [
        coldict["id"],
        racol,
        deccol,
        coldict["pmra"],
        coldict["pmdec"],
        "phot_g_mean_mag",
    ]

    query_string = """SELECT source_id,ra,dec,pmra,pmdec,phot_g_mean_mag
    FROM gaia
    WHERE q3c_radial_query(ra, dec, {:}, {:}, {:})
    AND {:s} IS NOT NULL AND {:s} IS NOT NULL
    AND {:s} BETWEEN {:} AND {:}
    ;
    """.format(
        raTel_deg,
        decTel_deg,
        fp_rad_deg * fp_fudge_factor,
        coldict["pmra"],
        coldict["pmdec"],
        "phot_g_mean_mag",
        0.0,
        guidestar_neighbor_mag_min,
    )

    # print(query_string)

    cur.execute(query_string)
    df_res = pd.DataFrame(
        cur.fetchall(),
        columns=["source_id", "ra", "dec", "pmra", "pmdec", "phot_g_mean_mag"],
    )

    # print(df_res)

    res = {}
    for col in df_res.columns:
        res[col] = df_res[col].to_numpy()

    # print(res)

    cur.close()
    conn.close()

    # # FIXME: run similar query, but without the PM requirement, to get a list of
    # # potentially too-bright neighbours

    # adjust for proper motion
    epoch = Time(args.observation_time).jyear
    res[racol], res[deccol] = update_coords_for_proper_motion(
        res[racol],
        res[deccol],
        res[coldict["pmra"]],
        res[coldict["pmdec"]],
        2015.5,
        epoch,
    )

    # compute PFI coordinates
    tmp = np.array([res[racol], res[deccol]])
    tmp = ctrans(
        xyin=tmp,
        za=0.0,
        mode="sky_pfi",
        inr=0.0,
        pa=pa_deg,
        cent=np.array([raTel_deg, decTel_deg]),
        time=obs_time,
    )

    res["xypos"] = np.array([tmp[0, :], tmp[1, :]]).T

    # determine the subset of sources falling within the guide cam FOVs
    # For the moment I'm using matplotlib's path functionality for this task
    # Once the "pfi_sky" transformation direction is available in
    # pfs_utils.coordinates, we can do a direct polygon query for every camera,
    # which should be more efficient.
    targets = {}
    tgtcam = []

    for i in range(agcoord.shape[0]):

        p = mppath.Path(agcoord[i])

        # find all targets in the slighty enlarged FOV
        tmp = p.contains_points(res["xypos"], radius=1.0)  # 1mm more
        tdict = {}

        for key, val in res.items():
            tdict[key] = val[tmp]

        # eliminate close neighbors
        flags = flag_close_pairs(tdict[racol], tdict[deccol], guidestar_minsep_deg)

        for key, val in tdict.items():
            tdict[key] = val[np.invert(flags)]

        # eliminate all targets which are not bright enough to be guide stars
        flags = tdict["phot_g_mean_mag"] < guidestar_mag_max

        for key, val in tdict.items():
            tdict[key] = val[flags]

        # eliminate all targets which are not really in the camera's FOV
        flags = p.contains_points(tdict["xypos"])  # 1mm more

        for key, val in tdict.items():
            tdict[key] = val[flags]

        # add AG camera ID
        tdict["agid"] = [i] * len(tdict[coldict["id"]])

        # compute and add pixel coordinates
        tmp = []
        for pos in tdict["xypos"]:
            tmp.append(ag_pfimm_to_pixel(i, pos[0], pos[1]))
        tdict["agpix_x"] = np.array([x[0] for x in tmp])
        tdict["agpix_y"] = np.array([x[1] for x in tmp])

        # append the results for this camera to the full list
        tgtcam.append(tdict)
        for key, val in tdict.items():
            if key not in targets:
                targets[key] = val
            else:
                targets[key] = np.concatenate((targets[key], val))

    # Write the results to a new pfsDesign file. Data fields are according to
    # DAMD-101.
    # required data:
    # ra/dec of guide star candidates: in racol, deccol
    # PM information: in pmra, pmdec
    # parallax: currently N/A
    # flux: currently N/A
    # AgId: trivial to obtain from data structure
    # AgX, AgY (pixel coordinates): only computable with access to the full
    #   AG camera geometry
    output_design = input_design

    ntgt = len(targets[coldict["id"]])
    guidestars = pfs.datamodel.guideStars.GuideStars(
        targets[coldict["id"]],
        np.array([epoch] * ntgt),  # epoch
        targets[coldict["ra"]],
        targets[coldict["dec"]],
        targets[coldict["pmra"]],
        targets[coldict["pmdec"]],
        np.array([0.0] * ntgt),  # parallax
        targets["phot_g_mean_mag"],
        np.array(["??"] * ntgt),  # passband
        np.array([0.0] * ntgt),  # color
        targets["agid"],  # AG camera ID
        targets["agpix_x"],  # AG x pixel coordinate
        targets["agpix_y"],  # AG y pixel coordinate
        -42.0,  # telescope elevation, don't know how to obtain,
        0,  # numerical ID assigned to the GAIA catalogue
    )
    output_design.guideStars = guidestars
    output_design.write(dirName=args.design_dir)


def add_guidestars(args):
    import matplotlib.path as mppath
    import pfs.datamodel
    from astropy.time import Time
    from ets_shuffle import query_utils
    from ets_shuffle.convenience import flag_close_pairs
    from ets_shuffle.convenience import guidecam_geometry
    from ets_shuffle.convenience import plot_focal_plane
    from ets_shuffle.convenience import update_coords_for_proper_motion
    from pfs.utils.coordinates.CoordTransp import CoordinateTransform as ctrans
    from pfs.utils.coordinates.CoordTransp import ag_pfimm_to_pixel

    input_design = pfs.datamodel.PfsDesign.read(args.run_id, args.design_dir)
    raTel_deg, decTel_deg, pa_deg = (
        input_design.raBoresight,
        input_design.decBoresight,
        input_design.posAng,
    )

    # this should come from the pfsDesign as well, but is not yet in there
    # (DAMD-101)
    obs_time = args.observation_time

    guidestar_mag_max = args.guidestar_mag_max
    guidestar_neighbor_mag_min = args.guidestar_neighbor_mag_min
    guidestar_minsep_deg = args.guidestar_minsep_deg

    # guide star cam geometries
    agcoord = guidecam_geometry()

    # internal, technical parameters
    # set focal plane radius
    fp_rad_deg = 260.0 * 10.2 / 3600

    # Find guide star candidates

    # Query GAIA2 for a circular region containing all guide cam FOVs
    # Obtain all targets with g_mean_mag<=guidestar_neighbor_mag_min that have
    # proper motion information
    conn, table, coldict = query_utils.openGAIA2connection()
    racol, deccol = coldict["ra"], coldict["dec"]
    req_columns = [
        coldict["id"],
        racol,
        deccol,
        coldict["pmra"],
        coldict["pmdec"],
        "phot_g_mean_mag",
    ]
    constraints = [
        query_utils.build_circle_query(
            raTel_deg, decTel_deg, fp_rad_deg * 1.2, coldict
        ),
        query_utils.build_pm_query(coldict),
        query_utils.build_mag_query(guidestar_neighbor_mag_min, 0, "phot_g_mean_mag"),
    ]
    res = query_utils.run_query(conn, table, req_columns, constraints)
    # FIXME: run similar query, but without the PM requirement, to get a list of
    # potentially too-bright neighbours

    # adjust for proper motion
    epoch = Time(args.observation_time).jyear
    res[racol], res[deccol] = update_coords_for_proper_motion(
        res[racol],
        res[deccol],
        res[coldict["pmra"]],
        res[coldict["pmdec"]],
        2015.5,
        epoch,
    )

    # compute PFI coordinates
    tmp = np.array([res[racol], res[deccol]])
    tmp = ctrans(
        xyin=tmp,
        za=0.0,
        mode="sky_pfi",
        inr=0.0,
        pa=pa_deg,
        cent=np.array([raTel_deg, decTel_deg]),
        time=obs_time,
    )
    res["xypos"] = np.array([tmp[0, :], tmp[1, :]]).T

    # determine the subset of sources falling within the guide cam FOVs
    # For the moment I'm using matplotlib's path functionality for this task
    # Once the "pfi_sky" transformation direction is available in
    # pfs_utils.coordinates, we can do a direct polygon query for every camera,
    # which should be more efficient.
    targets = {}
    tgtcam = []
    for i in range(agcoord.shape[0]):
        p = mppath.Path(agcoord[i])
        # find all targets in the slighty enlarged FOV
        tmp = p.contains_points(res["xypos"], radius=1.0)  # 1mm more
        tdict = {}
        for key, val in res.items():
            tdict[key] = val[tmp]
        # eliminate close neighbors
        flags = flag_close_pairs(tdict[racol], tdict[deccol], guidestar_minsep_deg)
        for key, val in tdict.items():
            tdict[key] = val[np.invert(flags)]
        # eliminate all targets which are not bright enough to be guide stars
        flags = tdict["phot_g_mean_mag"] < guidestar_mag_max
        for key, val in tdict.items():
            tdict[key] = val[flags]
        # eliminate all targets which are not really in the camera's FOV
        flags = p.contains_points(tdict["xypos"])  # 1mm more
        for key, val in tdict.items():
            tdict[key] = val[flags]
        # add AG camera ID
        tdict["agid"] = [i] * len(tdict[coldict["id"]])
        # compute and add pixel coordinates
        tmp = []
        for pos in tdict["xypos"]:
            tmp.append(ag_pfimm_to_pixel(i, pos[0], pos[1]))
        tdict["agpix_x"] = np.array([x[0] for x in tmp])
        tdict["agpix_y"] = np.array([x[1] for x in tmp])
        # append the results for this camera to the full list
        tgtcam.append(tdict)
        for key, val in tdict.items():
            if key not in targets:
                targets[key] = val
            else:
                targets[key] = np.concatenate((targets[key], val))

    # Write the results to a new pfsDesign file. Data fields are according to
    # DAMD-101.
    # required data:
    # ra/dec of guide star candidates: in racol, deccol
    # PM information: in pmra, pmdec
    # parallax: currently N/A
    # flux: currently N/A
    # AgId: trivial to obtain from data structure
    # AgX, AgY (pixel coordinates): only computable with access to the full
    #   AG camera geometry
    output_design = input_design

    ntgt = len(targets[coldict["id"]])
    guidestars = pfs.datamodel.guideStars.GuideStars(
        targets[coldict["id"]],
        np.array([epoch] * ntgt),  # epoch
        targets[coldict["ra"]],
        targets[coldict["dec"]],
        targets[coldict["pmra"]],
        targets[coldict["pmdec"]],
        np.array([0.0] * ntgt),  # parallax
        targets["phot_g_mean_mag"],
        np.array(["??"] * ntgt),  # passband
        np.array([0.0] * ntgt),  # color
        targets["agid"],  # AG camera ID
        targets["agpix_x"],  # AG x pixel coordinate
        targets["agpix_y"],  # AG y pixel coordinate
        -42.0,  # telescope elevation, don't know how to obtain,
        0,  # numerical ID assigned to the GAIA catalogue
    )
    output_design.guideStars = guidestars
    output_design.write(dirName=args.design_dir)


def main():
    args = get_arguments()

    # gen_target_list(args)

    gen_target_list_from_targetdb(args)
    gen_assignment(args)
    add_guidestars(args)
    # add_guidestars_from_gaiadb(args)


if __name__ == "__main__":
    main()
