#!/usr/bin/env python3

import argparse
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import toml
from astropy.table import Table
from astropy.time import Time
from astropy.utils import iers
from logzero import logger
from pfs.utils.fiberids import FiberIds

import pointing_utils.dbutils as dbutils
import pointing_utils.designutils as designutils
import pointing_utils.nfutils as nfutils


def main(infile, outdir):

    tb_pfs_design = Table.read(infile)

    gfm = FiberIds()  # 2604
    fiber_ids = gfm.fiberId
    fiber_xpos = gfm.x
    fiber_ypos = gfm.y

    x_alloc, y_alloc = np.full(len(fiber_ids), np.nan), np.full(len(fiber_ids), np.nan)

    print(tb_pfs_design)

    for i in range(len(fiber_ids)):
        idx_fiber = tb_pfs_design["fiberId"] == fiber_ids[i]
        if np.any(idx_fiber):
            x_alloc[i], y_alloc[i] = tb_pfs_design["pfiNominal"][idx_fiber][0]

    print(x_alloc - fiber_xpos, y_alloc - fiber_ypos)

    fig = plt.figure()

    ax = fig.add_subplot(1, 1, 1, aspect="equal")

    ax.scatter(x_alloc - fiber_xpos, y_alloc - fiber_ypos, s=3 ** 2)

    ax.set_xlabel("x(allocated) - x(gfm) [mm]")
    ax.set_ylabel("y(allocated) - y(gfm) [mm]")

    plt.savefig(os.path.join(outdir, "cobra_delta_xy.pdf"), bbox_inches="tight")


if __name__ == "__main__":
    pfs_design_dir = "design"
    pfs_design_file = "design/pfsDesign-0x394747913dbcfa8d.fits"
    outdir = "check"
    main(pfs_design_file, outdir)
