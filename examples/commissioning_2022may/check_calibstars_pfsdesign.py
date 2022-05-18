#!/usr/bin/env python3

import argparse
import logging
import os

# matplotlib.use("agg")  # isort:skip
import matplotlib.pyplot as plt
import numpy as np
import toml
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.table import Table
from ics.cobraCharmer.pfiDesign import PFIDesign
from ics.cobraOps.Bench import Bench
from logzero import logger
from pfs.utils.coordinates.CoordTransp import CoordinateTransform
from pfs.utils.fiberids import FiberIds
from procedures.moduleTest.cobraCoach import CobraCoach
from targetdb import targetdb

from targetdb_api_utils import join_backref_values

# import matplotlib  # isort:skip


# logging.getLogger("matplotlib.font_manager").disabled = True
logging.getLogger("matplotlib").setLevel(logging.ERROR)


def load_ref_catalog(infile, db):

    logger.info(f"Load the reference catalog ({infile})")
    tbref = Table.read(infile)
    proposal_id = tbref.meta["proposal_id"]

    dfref = tbref.to_pandas()
    dfref.rename(
        columns={"input_catalog": "input_catalog_name"},
        inplace=True,
    )
    dfref["proposal_id"] = proposal_id
    dfref["target_type_name"] = "SCIENCE"

    backref_tables = ["proposal", "input_catalog", "target_type"]
    backref_keys = ["proposal_id", "input_catalog_name", "target_type_name"]
    backref_check_keys = ["proposal_id", "input_catalog_id", "target_type_id"]

    for i in range(len(backref_tables)):
        dfref = join_backref_values(
            dfref,
            db=db,
            table=backref_tables[i],
            key=backref_keys[i],
            check_key=backref_check_keys[i],
        )

    return dfref


def load_design(pfs_design):
    logger.info(f"Load the pfsDesign file ({pfs_design})")
    tb = Table.read(pfs_design, hdu=1)
    return tb


def plot_pfi_design(
    pfs_design,
    # tb_design,
    plotfile="test_pfi_design.pdf",
    fiber_id_matched=None,
    obj_id_matched=None,
    gfm=FiberIds(),
    stylesheet="tableau-colorblind10",
    xmin=-250,
    xmax=250,
    ymin=-250,
    ymax=250,
):
    # NOTE: the result is an astropy.Table object
    tb_design = load_design(pfs_design)

    x_alloc = np.full(len(gfm.fiberId), np.nan)
    y_alloc = np.full(len(gfm.fiberId), np.nan)

    for i in range(x_alloc.size):
        idx_fiber = tb_design["fiberId"] == gfm.fiberId[i]
        if np.any(idx_fiber):
            x_alloc[i], y_alloc[i] = tb_design["pfiNominal"][idx_fiber][0]

    with plt.style.context(stylesheet):
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_aspect("equal", "box")

        for i_sm in range(4):
            idx_sm = gfm.spectrographId == (i_sm + 1)
            ax.scatter(
                gfm.x[idx_sm],
                gfm.y[idx_sm],
                s=5 ** 2,
                c="none",
                marker="o",
                edgecolors=f"C{i_sm}",
                linewidth=0.25,
                label=f"SM{i_sm +1} (gfm)",
            )

        for i_sm in range(4):
            idx_sm = gfm.spectrographId == (i_sm + 1)
            ax.scatter(
                x_alloc[idx_sm],
                y_alloc[idx_sm],
                s=5 ** 2,
                c=f"C{i_sm}",
                marker="o",
                edgecolors="none",
                label=f"SM{i_sm +1} (design)",
            )

        for i_match in range(len(fiber_id_matched)):
            idx_matched = tb_design["fiberId"] == fiber_id_matched[i_match]
            ax.scatter(
                [tb_design["pfiNominal"][idx_matched][0][0]],
                [tb_design["pfiNominal"][idx_matched][0][1]],
                s=7.5 ** 2,
                c="orangered",
                marker="o",
                alpha=0.75,
                label=f"obj_id: {obj_id_matched[i_match]}",
            )

        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)

        ax.set_xlabel("X (PFI mm)")
        ax.set_ylabel("Y (PFI mm)")

        ax.legend(bbox_to_anchor=(1, 1), loc="upper left", frameon=False)

        ax.set_title(f"{os.path.basename(pfs_design)}")

        plt.savefig(plotfile, bbox_inches="tight")


def check_calibstars(
    pfs_design,
    plotfile,
    conf=None,
    ref=None,
    sm=None,
    pfs_instdata_dir=None,
    cobra_coach_dir=".",
):

    config = toml.load(conf)

    logger.info(f"Connect to the database.")
    db = targetdb.TargetDB(**dict(config["targetdb"]))
    db.connect()

    # NOTE: the result is a pandas.DataFrame object
    df_ref = load_ref_catalog(ref, db)

    # NOTE: the result is an astropy.Table object
    tb_design = load_design(pfs_design)

    logger.info("Load the grand fiber map")
    gfm = FiberIds()  # 2604

    logger.info("Check reference objects in pfsDesign")
    is_matched = False

    fiber_id_matched = []
    obj_id_matched = []
    sm_matched = []

    for i in range(df_ref.index.size):
        idx_match = tb_design["objId"] == df_ref["obj_id"][i]
        if np.any(idx_match):
            is_matched = True
            fiber_id = tb_design["fiberId"][idx_match].value[0]
            fiber_id_matched.append(fiber_id)
            obj_id_matched.append(tb_design["objId"][idx_match].value[0])
            sm_matched.append(gfm.spectrographId[fiber_id - 1])
            # FIXME: fiber_id shouldn't be used directly as one cannot assume it's sorted by fiberId.
            logger.info(
                f"""Match in the catalog found!
                obj_id (ref): {df_ref['obj_id'][i]}
                obj_id (design): {tb_design["objId"][idx_match].value[0]}
                input_catalog_name: {df_ref['input_catalog_name'][i]}
                (ra_ref, dec_ref) = ({df_ref['ra'][i]}, {df_ref['dec'][i]})
                (ra_design, dec_design) = ({df_ref['ra'][i]}, {df_ref['dec'][i]})
                fiberId: {fiber_id}
                cobraId: {gfm.cobraId[fiber_id - 1]}
                spectrograph: {gfm.spectrographId[fiber_id - 1]}
                pfiNominal: ({tb_design["pfiNominal"][idx_match].value[0][0]:.3f}, {tb_design["pfiNominal"][idx_match].value[0][1]:.3f})"""
            )

    logger.info("Close connection to the database")
    db.close()

    if not is_matched:
        logger.warning("No match found in the pfsDesign.")

    # calculate a distance to the nearest neighbor cobra in a given spectrograph
    # FIXME: this is very inefficient search, I guess.
    if sm is not None:

        hdu_design = fits.open(pfs_design)

        os.environ["PFS_INSTDATA_DIR"] = pfs_instdata_dir
        cobra_coach = CobraCoach(
            "fpga", loadModel=False, trajectoryMode=True, rootDir=cobra_coach_dir
        )

        cobra_coach.loadModel(version="ALL", moduleVersion=None)

        calibration_product = cobra_coach.calibModel

        # load Bench with the default setting
        bench = Bench(layout="full")

        # copy values into calibration_product using the default Bench object
        calibration_product.status = bench.cobras.status.copy()
        calibration_product.tht0 = bench.cobras.tht0.copy()
        calibration_product.tht1 = bench.cobras.tht1.copy()
        calibration_product.phiIn = bench.cobras.phiIn.copy()
        calibration_product.phiOut = bench.cobras.phiOut.copy()
        calibration_product.L1 = bench.cobras.L1.copy()
        calibration_product.L2 = bench.cobras.L2.copy()

        # Limit spectral modules
        gfm = FiberIds()  # 2604
        cobra_ids_use = np.array([], dtype=np.uint16)
        for sm_use in sm:
            cobra_ids_use = np.append(cobra_ids_use, gfm.cobrasForSpectrograph(sm_use))

        # set Bad Cobra status for unused spectral modules
        for cobra_id in range(calibration_product.nCobras):
            if cobra_id not in cobra_ids_use:
                calibration_product.status[cobra_id] = ~PFIDesign.COBRA_OK_MASK

        # load Bench with the updated calibration products
        bench = Bench(
            layout="calibration",
            calibrationProduct=calibration_product,
        )
        x_cobras = np.full(bench.cobras.nCobras, np.nan)
        y_cobras = np.full(bench.cobras.nCobras, np.nan)

        for i_gfm in range(len(gfm.fiberId)):
            if (
                (gfm.cobraId[i_gfm] >= 0)
                and (gfm.cobraId[i_gfm] <= bench.cobras.nCobras)
                and (bench.cobras.status[gfm.cobraId[i_gfm] - 1] == 1)
            ):
                x_cobras[gfm.cobraId[i_gfm] - 1] = gfm.x[i_gfm]
                y_cobras[gfm.cobraId[i_gfm] - 1] = gfm.y[i_gfm]

        for i_matched, fiber_id in enumerate(fiber_id_matched):

            if sm_matched[i_matched] == sm:
                logger.info(
                    f"Congratulations! The investigated object is already in SM{sm[0]}."
                )
                continue

            idx_fiber = tb_design["fiberId"] == fiber_id
            x_alloc, y_alloc = tb_design["pfiNominal"][idx_fiber].value[0]
            d_cobras2 = np.power(x_cobras - x_alloc, 2) + np.power(
                y_cobras - y_alloc, 2
            )
            # print(d_cobras2)
            i_cobra_min = np.nanargmin(d_cobras2)
            # print(x_cobras[i_cobra_min], y_cobras[i_cobra_min])

            radec = CoordinateTransform(
                np.array([x_cobras[i_cobra_min], y_cobras[i_cobra_min]]).reshape(
                    (2, 1)
                ),
                "pfi_sky",
                pa=hdu_design[0].header["POSANG"],
                cent=np.array(
                    [hdu_design[0].header["RA"], hdu_design[0].header["DEC"]],
                ).reshape((2, 1)),
            )
            # print(radec[0], radec[1])
            coord_alloc = SkyCoord(
                tb_design["ra"][idx_fiber].value[0] * u.deg,
                tb_design["dec"][idx_fiber].value[0] * u.deg,
                frame="icrs",
            )
            coord_design = SkyCoord(
                hdu_design[0].header["RA"] * u.deg,
                hdu_design[0].header["DEC"] * u.deg,
                frame="icrs",
            )
            coord_dest = SkyCoord(
                radec[0][0] * u.deg, radec[1][0] * u.deg, frame="icrs"
            )
            d_ra, d_dec = coord_alloc.spherical_offsets_to(coord_dest)
            # print(d_ra.to(u.arcmin), d_dec.to(u.arcmin))
            coord_design_dest = coord_design.spherical_offsets_by(
                *coord_dest.spherical_offsets_to(coord_alloc)
            )
            # print(coord_design_dest)
            logger.info(
                f"""Currently, the investigated object is in SM{sm_matched[i_matched]}.
                Following changes for the pointing coordinate should move the target to the nearest cobra in SM{sm[0]}
                ra: {coord_design_dest.ra:.5f},
                dec: {coord_design_dest.dec:.5f},
                pa: {hdu_design[0].header['POSANG']}
                """
            )

    # create plot if the flag is True
    if plotfile is not None:
        # stylesheet="seaborn-colorblind"
        # stylesheet = "tableau-colorblind10"
        logger.info(f"Plot is created as {plotfile}")
        plot_pfi_design(
            pfs_design,
            plotfile=plotfile,
            fiber_id_matched=fiber_id_matched,
            obj_id_matched=obj_id_matched,
        )
    else:
        logger.info("No plot is created")

    return is_matched


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "pfs_design", type=str, help="pfsDesign file with the full path."
    )
    parser.add_argument(
        "--plotfile",
        type=str,
        default=None,
        help="Output filename with the full path for a PFI plot (default: None)",
    )
    parser.add_argument(
        "--conf",
        type=str,
        default=None,
        help="Configuration file (.toml). Same as the main script.",
    )
    parser.add_argument(
        "--ref",
        type=str,
        default="targets_S22A-EN16.ecsv",
        help="input file for Yamashita-san's catalog. (default: targets_S22A-EN16.ecsv)",
    )
    parser.add_argument(
        "--sm",
        type=int,
        nargs="+",
        default=[1],
        help="target spectrograph ID to be checked. (default: None)",
    )
    parser.add_argument(
        "--pfs_instdata_dir",
        type=str,
        default="/Users/monodera/Dropbox/NAOJ/PFS/Subaru-PFS/pfs_instdata/",
        help="Location of pfs_instdata (default: /Users/monodera/Dropbox/NAOJ/PFS/Subaru-PFS/pfs_instdata/)",
    )
    parser.add_argument(
        "--cobra_coach_dir",
        type=str,
        default=".",
        help="path for temporary cobraCoach files (default: .)",
    )

    args = parser.parse_args()

    is_matched = check_calibstars(
        args.pfs_design,
        args.plotfile,
        args.conf,
        args.ref,
        args.sm,
        args.pfs_instdata_dir,
        args.cobra_coach_dir,
    )
