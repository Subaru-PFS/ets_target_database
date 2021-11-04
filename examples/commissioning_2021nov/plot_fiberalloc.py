#!/usr/bin/env python

import argparse

import matplotlib.pyplot as plt
import matplotlib.style as style
from astropy.table import Table

# style.use("tableau-colorblind10")
style.use("seaborn-colorblind")


def main(pfsdesign, input_catalog, output_plot):

    tb_design_fiber = Table.read(pfsdesign, hdu=1)
    tb_design_guide = Table.read(pfsdesign, hdu=3)
    tb_input = Table.read(input_catalog, format="ascii.ecsv")

    print(tb_design_fiber, tb_design_guide, tb_input)

    fig = plt.figure()

    ax = fig.add_subplot(1, 1, 1, aspect="equal")

    ax.scatter(tb_input["R.A."], tb_input["Dec."], s=2 ** 2, ec="none", label="parent")
    ax.scatter(
        tb_design_fiber["ra"],
        tb_design_fiber["dec"],
        s=4 ** 2,
        ec="white",
        lw=0.1,
        label="assigned",
    )
    ax.scatter(
        tb_design_guide["ra"],
        tb_design_guide["dec"],
        s=6 ** 2,
        ec="0.2",
        lw=0.1,
        label="guide star",
    )

    ax.invert_xaxis()

    ax.set_xlabel("RA (deg)")
    ax.set_ylabel("Dec (deg)")

    plt.savefig(output_plot, bbox_inches="tight")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("pfsdesign", help="pfsDesign file")
    parser.add_argument("input_catalog", help="input catalog")
    parser.add_argument("output_plot", help="name of the figure")

    args = parser.parse_args()

    main(args.pfsdesign, args.input_catalog, args.output_plot)
