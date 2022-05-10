#!/usr/bin/env python3

import math
import os

import ets_fiber_assigner.netflow as nf
import numpy as np
from ics.cobraOps.Bench import Bench
from ics.cobraOps.BlackDotsCalibrationProduct import BlackDotsCalibrationProduct
from ics.cobraOps.cobraConstants import NULL_TARGET_ID
from ics.cobraOps.cobraConstants import NULL_TARGET_POSITION
from ics.cobraOps.CollisionSimulator2 import CollisionSimulator2
from ics.cobraOps.TargetGroup import TargetGroup
from procedures.moduleTest.cobraCoach import CobraCoach

# import argparse
# import configparser
# import matplotlib.path as mppath
# import pandas as pd
# import pfs.datamodel
# import psycopg2
# import psycopg2.extras
# from astropy import units as u
# from astropy.table import Table
# from astropy.time import Time
# from ets_shuffle import query_utils
# from ets_shuffle.convenience import flag_close_pairs
# from ets_shuffle.convenience import guidecam_geometry
# from ets_shuffle.convenience import update_coords_for_proper_motion
# from pfs.utils.coordinates.CoordTransp import ag_pfimm_to_pixel
# from pfs.utils.coordinates.CoordTransp import CoordinateTransform as ctrans
# from pfs.utils.pfsDesignUtils import makePfsDesign
# import tempfile
# import time
# from targetdb import targetdb


# This was needed for fixing some issues with the XML files.
# Can probably be simplified. Javier?
#
# NOTE: Do we still need the getBench function?
#
def getBench(
    pfs_instdata_dir,
    cobra_coach_dir,
    cobra_coach_module_version,
):

    os.environ["PFS_INSTDATA_DIR"] = pfs_instdata_dir
    cobraCoach = CobraCoach(
        "fpga", loadModel=False, trajectoryMode=True, rootDir=cobra_coach_dir
    )

    cobraCoach.loadModel(version="ALL", moduleVersion=cobra_coach_module_version)

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
    print("Cobras with zero link lengths: %i" % np.sum(zeroLinkLengths))

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
    print("Cobras with too long link lengths: %i" % np.sum(tooLongLinkLengths))

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


def register_objects(df, target_class=None):

    if target_class == "sci":
        # print(df["priority"])
        res = [
            nf.ScienceTarget(
                df["obj_id"][i],
                df["ra"][i],
                df["dec"][i],
                df["effective_exptime"][i],
                int(df["priority"][i]),
                target_class,
            )
            for i in range(df.index.size)
        ]
    elif target_class == "cal" or target_class == "sky":
        res = [
            nf.CalibTarget(
                df["obj_id"][i],
                df["ra"][i],
                df["dec"][i],
                target_class,
            )
            for i in range(df.index.size)
        ]
    else:
        raise ValueError(
            f"target_class '{target_class}' must be one of 'sci', 'cal', and 'sky'."
        )
    return res


def run_netflow(
    cobra_coach,
    bench,
    targets,
    target_fppos,
    class_dict,
    exptime,
    vis_cost=None,
    cobraMoveCost=None,
    collision_distance=0.0,
    elbow_collisions=True,
    gurobi=True,
    gurobiOptions=None,
    alreadyObserved=None,
    forbiddenPairs=None,
    cobraLocationGroup=None,
    minSkyTargetsPerLocation=None,
    locationGroupPenalty=None,
    cobraInstrumentRegion=None,
    minSkyTargetsPerInstrumentRegion=None,
    instrumentRegionPenalty=None,
):

    # We penalize targets near the edge of a patrol region slightly to reduce
    # the chance of endpoint collisions with unallocated Cobras
    # (see note below).
    def cobra_move_cost(dist):
        return 0.1 * dist

    done = False

    while not done:
        # compute observation strategy
        prob = nf.buildProblem(
            bench,
            targets,
            target_fppos,
            class_dict,
            exptime,
            vis_cost=vis_cost,
            cobraMoveCost=cobra_move_cost if cobraMoveCost is None else cobraMoveCost,
            collision_distance=collision_distance,
            elbow_collisions=elbow_collisions,
            gurobi=gurobi,
            gurobiOptions=gurobiOptions,
            alreadyObserved=alreadyObserved,
            forbiddenPairs=forbiddenPairs,
            cobraLocationGroup=cobraLocationGroup,
            minSkyTargetsPerLocation=minSkyTargetsPerLocation,
            locationGroupPenalty=locationGroupPenalty,
            cobraInstrumentRegion=cobraInstrumentRegion,
            minSkyTargetsPerInstrumentRegion=minSkyTargetsPerInstrumentRegion,
            instrumentRegionPenalty=instrumentRegionPenalty,
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
        for ivis, (vis, tp) in enumerate(zip(res, target_fppos)):
            selectedTargets = np.full(len(bench.cobras.centers), NULL_TARGET_POSITION)
            ids = np.full(len(bench.cobras.centers), NULL_TARGET_ID)
            for tidx, cidx in vis.items():
                selectedTargets[cidx] = tp[tidx]
                ids[cidx] = ""
            for i in range(selectedTargets.size):
                if selectedTargets[i] != NULL_TARGET_POSITION:
                    dist = np.abs(selectedTargets[i] - bench.cobras.centers[i])

            simulator = CollisionSimulator2(
                bench, cobra_coach, TargetGroup(selectedTargets, ids)
            )
            simulator.run()
            # If you want to see the result of the collision simulator, uncomment the next three lines
            #            from ics.cobraOps import plotUtils
            #            simulator.plotResults(paintFootprints=False)
            #            plotUtils.pauseExecution()
            #
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

    return res


def fiber_allocation(
    df_targets,
    df_fluxstds,
    df_sky,
    ra,
    dec,
    pa,
    n_fluxstd,
    n_sky,
    observation_time,
    conf,
    pfs_instdata_dir,
    cobra_coach_dir,
    cobra_coach_module_version,
):
    targets = register_objects(df_targets, target_class="sci")
    targets += register_objects(df_fluxstds, target_class="cal")
    targets += register_objects(df_sky, target_class="sky")

    # cobra_coach, bench = getBench(
    #     pfs_instdata_dir, cobra_coach_dir, cobra_coach_module_version
    # )

    os.environ["PFS_INSTDATA_DIR"] = pfs_instdata_dir
    cobra_coach = CobraCoach(
        "fpga", loadModel=False, trajectoryMode=True, rootDir=cobra_coach_dir
    )
    cobra_coach.loadModel(version="ALL", moduleVersion=cobra_coach_module_version)

    bench = Bench(layout="full")

    telescopes = [nf.Telescope(ra, dec, pa, observation_time)]

    # get focal plane positions for all targets and all visits
    target_fppos = [tele.get_fp_positions(targets) for tele in telescopes]

    # create the dictionary containing the costs and constraints for all classes
    # of targets
    # For the purpose of this demonstration we assume that all targets are
    # scientific targets with priority 1.
    class_dict = {
        "sci_P1": {
            "nonObservationCost": 10,
            "partialObservationCost": 100,
            "calib": False,
        },
        "cal": {
            "numRequired": n_fluxstd,
            "nonObservationCost": 1e6,
            "calib": True,
        },
        "sky": {
            "numRequired": n_sky,
            "nonObservationCost": 1e6,
            "calib": True,
        },
    }
    target_class_dict = {"sci_P1": 1, "sky": 2, "cal": 3}

    if math.isclose(
        df_targets["effective_exptime"].min(), df_targets["effective_exptime"].max()
    ):
        exptime = df_targets["effective_exptime"][0]
    else:
        raise ValueError("Exposure time is not identical for all objects.")

    already_observed = {}
    forbidden_pairs = []
    for i in range(1):
        forbidden_pairs.append([])

    res = run_netflow(
        cobra_coach,
        bench,
        targets,
        target_fppos,
        class_dict,
        exptime,
        vis_cost=None,
        cobraMoveCost=None,
        collision_distance=2.0,
        elbow_collisions=True,
        gurobi=conf["netflow"]["use_gurobi"],
        gurobiOptions=dict(conf["gurobi"]) if conf["netflow"]["use_gurobi"] else None,
        alreadyObserved=already_observed,
        forbiddenPairs=forbidden_pairs,
        cobraLocationGroup=None,
        minSkyTargetsPerLocation=None,
        locationGroupPenalty=None,
        cobraInstrumentRegion=None,
        minSkyTargetsPerInstrumentRegion=None,
        instrumentRegionPenalty=None,
    )

    return res[0], target_fppos[0], telescopes[0], targets, target_class_dict
