#!/usr/bin/env python3

import argparse
import datetime

import pandas as pd
import toml
from logzero import logger
from targetdb import targetdb


def main(conf, split_size=None):

    logger.info(f"Load config file {conf}.")
    config = toml.load(conf)

    logger.info(f"Connect to the database.")
    db = targetdb.TargetDB(**dict(config["targetdb"]))
    db.connect()

    # split_size = 500000
    i = 0

    while True:

        offset = i * split_size

        print(i, offset)

        logger.info(f"Fetch {split_size} objects from the {offset}-th object.")
        df_fluxstd = db.fetch_query(
            f"""SELECT fluxstd_id, filter_g, filter_r, filter_i, filter_z, filter_y, updated_at
            FROM fluxstd
            ORDER BY fluxstd_id
            LIMIT {split_size} OFFSET {offset};"""
        )

        print(df_fluxstd)

        if df_fluxstd.empty:
            logger.info(f"All objects has been fetched. Exit.")
            break

        df_fluxstd["filter_g"] = "g_ps1"
        df_fluxstd["filter_r"] = "r_ps1"
        df_fluxstd["filter_i"] = "i_ps1"
        df_fluxstd["filter_z"] = "z_ps1"
        df_fluxstd["filter_y"] = "y_ps1"

        utcnow = datetime.datetime.utcnow()
        df_fluxstd["updated_at"] = utcnow

        logger.info(
            f"Update the fluxstd table with filter names with the timestamp of {utcnow}"
        )
        db.update("fluxstd", df_fluxstd)

        i += 1

    logger.info(f"Close the database.")
    db.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "conf",
        type=str,
        # default="config.toml",
        help="Config file for the script to run. Must be a .toml file (mandatory)",
    )
    parser.add_argument(
        "--split_size",
        type=int,
        default=500000,
        help="Chunk size of updates (default: 500000)",
    )

    args = parser.parse_args()

    main(args.conf, args.split_size)
