#!/usr/bin/env python3

import argparse

import logzero
from logzero import logger

from .. import draw_diagram


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Create the ER diagram of the database in PDF"
    )

    parser.add_argument(
        "conf",
        type=str,
        default="config.toml",
        help="Config file for the script to run. Must be a .toml file (default: config.toml)",
    )

    parser.add_argument(
        "--sc_info_level",
        type=str,
        default="maximum",
        help="SchemaCrawler's info level (default: maximum)",
    )
    parser.add_argument(
        "--sc_log_level",
        type=str,
        default="SEVERE",
        help="SchemaCrawler's log level (default: SEVERE)",
    )
    parser.add_argument(
        "--sc_outdir",
        type=str,
        default=".",
        help="Output directory (default: .)",
    )
    parser.add_argument(
        "--sc_outprefix",
        type=str,
        default="erdiagram_targetdb",
        help="Prefix for the output file (default: erdiagram_targetdb)",
    )
    parser.add_argument(
        "--sc_title",
        type=str,
        default="PFS Target Database",
        help="Title of the output ER diagram (default: PFS Target Database)",
    )
    parser.add_argument("--debug", action="store_true", help=argparse.SUPPRESS)

    args = parser.parse_args()

    return args


def main():

    args = get_arguments()

    if args.debug:
        logzero.loglevel(logzero.DEBUG)
    else:
        logzero.loglevel(logzero.INFO)

    logger.info(args)

    draw_diagram(
        args.conf,
        sc_info_level=args.sc_info_level,
        sc_log_level=args.sc_log_level,
        sc_outdir=args.sc_outdir,
        sc_outprefix=args.sc_outprefix,
        sc_title=args.sc_title,
        logger=logger,
    )


if __name__ == "__main__":
    main()
