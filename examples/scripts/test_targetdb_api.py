#!/usr/bin/env python

import argparse
import configparser
import datetime
import sys

import astropy.units as u
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord
from astropy.coordinates import search_around_sky
from logzero import logger
from targetdb import models
from targetdb import targetdb


def get_arguments():
    parser = argparse.ArgumentParser(description="Test targetDB API")
    parser.add_argument(
        "conf",
        type=str,
        default="targetdb_config.ini",
        help="Config file for targetDB (default: './targetdb_config.ini')",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset all tables in targetdb before playing with it. (Default: False)",
    )
    parser.add_argument(
        "--skip_proposal_category",
        action="store_true",
        help="Skip inserting test data into the proposal_category table (default: False)",
    )
    parser.add_argument(
        "--skip_proposal",
        action="store_true",
        help="Skip inserting test data into the proposal table (default: False)",
    )
    parser.add_argument(
        "--skip_input_catalog",
        action="store_true",
        help="Skip inserting test data into the input_catalog table (default: False)",
    )
    parser.add_argument(
        "--skip_target_type",
        action="store_true",
        help="Skip inserting test data into the target_type table (default: False)",
    )
    parser.add_argument(
        "--skip_target",
        action="store_true",
        help="Skip inserting test data into the target table (default: False)",
    )
    parser.add_argument(
        "--skip_unique_object",
        action="store_true",
        help="Skip inserting test data into the unique_object table (default: False)",
    )

    parser.add_argument(
        "--target",
        default="../data/target_s21b-en01.csv",
        help="Skip inserting test data into the target table (default: False)",
    )

    args = parser.parse_args()

    return args


def connect_db(conf=None):

    config = configparser.ConfigParser()
    config.read(conf)

    # print(dict(config["dbinfo"]))

    db = targetdb.TargetDB(**dict(config["dbinfo"]))

    db.connect()

    return db


def insert_simple(db, table=None, csv=None, df=None, return_defaults=False):

    if csv is not None and df is None:
        df_input = pd.read_csv(csv)
    elif csv is None and df is not None:
        df_input = df
    else:
        print("csv and df cannot be None at the same time. Exit.")
        exit()

    n_input = len(df_input.index)
    df_ret = None

    try:
        print("trying to insert data into {:s}...".format(table))

        utcnow = datetime.datetime.utcnow()
        df_input["created_at"] = [utcnow] * n_input
        df_input["updated_at"] = [utcnow] * n_input

        df_ret = db.insert(table, df_input, return_defaults=return_defaults)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        # print("no unique value in the input data is found. skip.")
        # exit()

    res = db.fetch_all(table)
    print(res)

    if return_defaults:
        return db, df_ret
    else:
        return db


def join_backref_values(df, db=None, table=None, key=None, check_key=None):

    res = db.fetch_all(table)
    df_joined = df.merge(
        res,
        how="left",
        left_on=key,
        right_on=key,
    )
    # print(df_joined)
    if df_joined[check_key].isna().any():
        print("There is at least one non-existing {:s}.".format(check_key))
        exit()
    return df_joined


def insert_proposal(db):
    df_proposal = pd.read_csv("../data/proposal.csv")
    n_proposal = len(df_proposal.index)

    df_joined = join_backref_values(
        df_proposal,
        db=db,
        table="proposal_category",
        key="proposal_category_name",
        check_key="proposal_category_id",
    )

    db = insert_simple(db, table="proposal", df=df_joined)

    return db


def check_duplication_by_separation(
    df1, df2, max_sep=0.5 * u.arcsec, skip_self=True, external=False
):

    # print(len(df1.index), len(df2.index))

    # dataframe for duplicated objects
    df_dup = pd.DataFrame(
        [],
        columns=[
            "index_1",
            "ra_1",
            "dec_1",
            "index_2",
            "ra_2",
            "dec_2",
            "sep",
            "unique_object_id",
        ],
    )

    if df1.empty:
        logger.error("The user-input dataframe is empty. Exit.")
        exit()

    if df2.empty:
        logger.info(
            "The catalog-registered dataframe is empty. Return the original dataframe and empty dataframe."
        )
        return df1, df_dup

    coord1 = SkyCoord(df1["ra"] * u.deg, df1["dec"] * u.deg, frame="icrs")
    coord2 = SkyCoord(df2["ra"] * u.deg, df2["dec"] * u.deg, frame="icrs")

    df1_index = df1.index.values
    df2_index = df2.index.values

    idx_coord, idx_catalog, sep2d, _ = search_around_sky(coord1, coord2, max_sep)

    # print("idx_coord: ", idx_coord)
    # print("idx_catalog: ", idx_catalog)
    # print("sep2d: ", sep2d.to("arcsec"))

    # create a list of unique object IDs (should be identical to np.arange(len(df.index)), though)
    idx_coord_unique, counts_coord = np.unique(idx_coord, return_counts=True)

    # print("idx_coord_unique:", idx_coord_unique)
    # print("counts_coord", counts_coord)

    if skip_self:
        idx_unique = idx_coord_unique[counts_coord == 1]
        idx_matched = idx_coord_unique[counts_coord > 1]
    else:
        # idx_unique = idx_coord_unique[counts_coord == 0]
        idx_matched = idx_coord_unique[counts_coord > 0]
        idx_unique = np.delete(df1.index.values, idx_matched)

    print("idx_unique: ", idx_unique)
    print("idx_matched: ", idx_matched)

    # array of cross matched object indexes which has already checked for duplication
    idx_matched_checked = []

    # array of unique objects in the list of objects matched with N>1 objects
    idx_matched_unique = []

    # loop over objects with >1 matched objects
    for i in range(idx_matched.size):

        idx_i = idx_matched[i]

        idx_matched_checked.append(idx_i)

        # True for matched objects for the i-th input object
        idx_matched_catalog = idx_catalog[idx_coord == idx_i]
        # print("idx_matched_catalog: ", idx_matched_catalog)

        # on-sky separation for the matched objects
        sep2d_matched = sep2d[idx_coord == idx_i]

        # is_checked_itself = False

        # loop over matched objects for the i-th input object
        for j in range(idx_matched_catalog.size):

            idx_j = idx_matched_catalog[j]

            # Skip if the j-th object is the i-th object itself when skip_self=False
            if skip_self and (df1_index[idx_i] == df2_index[idx_j]):
                do_process = False
            elif skip_self and (df1_index[idx_i] != df2_index[idx_j]):
                do_process = True
            else:
                do_process = True

            # if skip_self and (df1_index[idx_i] != df2_index[idx_j]):
            if do_process:
                # print("Processing: ", df1_index[idx_i], df2_index[idx_j])

                # Skip if the pair of i-j has been already checked
                if skip_self and (idx_j in idx_matched_checked):

                    logger.debug(
                        "Index pair (idx_i, idx_j) = ({:d} {:d}) of df1 has already been checked. SKip.".format(
                            idx_i, idx_j
                        )
                    )

                else:
                    # print("Processing index {:d} of df1.".format(idx_j))
                    if external:
                        unique_object_id = df2["unique_object_id"][idx_j]
                    else:
                        unique_object_id = -1

                    arr = np.array(
                        [
                            (
                                df1_index[idx_i],
                                df1["ra"][idx_i],
                                df1["dec"][idx_i],
                                df2_index[idx_j],
                                df2["ra"][idx_j],
                                df2["dec"][idx_j],
                                sep2d_matched[j].to("arcsec").value,
                                unique_object_id,
                            ),
                        ],
                        dtype=[
                            ("index_1", np.int64),
                            ("ra_1", float),
                            ("dec_1", float),
                            ("index_2", np.int64),
                            ("ra_2", float),
                            ("dec_2", float),
                            ("sep", float),
                            ("unique_object_id", np.int64),
                        ],
                    )
                    df_dup = df_dup.append(
                        pd.DataFrame(arr),
                        ignore_index=True,
                    )
                # if idx_i is not found in the already checked unique object with N>1 matched objects and duplicated objects,
                # add idx_i to the idx_matched_unique list
                if (idx_i not in idx_matched_unique) and (
                    idx_i not in df_dup["index_2"].values
                ):
                    idx_matched_unique.append(idx_i)

    print("idx_matched_unique: ", idx_matched_unique)
    df_unique = (
        pd.concat(
            [df1.loc[idx_unique], df1.loc[idx_matched_unique]],
            axis=0,
            join="inner",
            ignore_index=False,
            verify_integrity=True,
        )
        .sort_index()
        .reset_index(drop=False)
    )

    return df_unique, df_dup


def check_internal_duplication(df, max_sep=0.5 * u.arcsec):
    df_unique, df_dup = check_duplication_by_separation(
        df, df, max_sep=max_sep, skip_self=True
    )
    if (df_dup["unique_object_id"] == -1).all():
        logger.debug(
            "All unique_object_id of duplicated objects are -1 (correct value for the internal check)."
        )
    else:
        logger.error("unique_object_id for the duplications must be -1. Exit.")
        exit()

    return df_unique, df_dup


def check_external_duplication(df, db=None, max_sep=0.5 * u.arcsec):

    df_unique_object_all = db.fetch_all("unique_object")

    # print(df_unique_object_all)
    # print(df_unique_object_all.empty)

    df_unique, df_dup = check_duplication_by_separation(
        df,
        df_unique_object_all,
        max_sep=max_sep,
        skip_self=False,
        external=True,
    )

    return db, df_unique, df_dup


def insert_target(db, args, max_sep=0.5 * u.arcsec):

    logger.info("Loading data from {:s}".format(args.target))
    df = pd.read_csv(args.target)

    # copy dataframe (may not be needed)
    df_target_tmp = df.copy()

    # add target_type_name as SCIENCE by default for openuse proposals
    df_target_tmp["target_type_name"] = ["SCIENCE"] * len(df_target_tmp.index)

    backref_tables = ["proposal", "input_catalog", "target_type"]
    backref_keys = ["proposal_id", "input_catalog_name", "target_type_name"]
    backref_check_keys = ["proposal_id", "input_catalog_id", "target_type_id"]

    for i in range(len(backref_tables)):
        df_target_tmp = join_backref_values(
            df_target_tmp,
            db=db,
            table=backref_tables[i],
            key=backref_keys[i],
            check_key=backref_check_keys[i],
        )

    # check duplication with a certain separation "within" the input objects
    logger.info("Check duplication within the input data")
    df_unique_internal, df_duplicate_internal = check_internal_duplication(
        df_target_tmp,
        max_sep=max_sep,
        # df_target_tmp[:120],
        # max_sep=12 * u.arcsec,
    )
    df_unique_internal.rename(columns={"index": "index_original"}, inplace=True)

    df_unique_internal.to_csv("test_unique_internal.csv", index=False)
    df_duplicate_internal.to_csv("test_duplicate_internal.csv", index=False)

    print("#")
    print("# Result of internal duplication check")
    print("#")

    print("# unique objects: ")
    print(df_unique_internal)

    if df_duplicate_internal.empty:
        logger.info(
            "No duplication found within the input data with a maximum search separation of {:s}.  This is a good sign.".format(
                max_sep
            )
        )
    else:
        logger.error(
            "Internal duplication(s) found within the input data with a maximum search separation of {:s}".format(
                max_sep
            )
        )
        print("# duplicated objects: ")
        print(df_duplicate_internal)
        logger.info(
            "Please check test_duplicate_internal.csv for the duplicated objects."
        )
        # df_duplicate_internal.to_csv("test_duplicate_internal.csv", index=False)
        exit()

    logger.info(
        "Checking duplication with existing unique objects in the unique_object table"
    )
    db, df_unique_external, df_duplicate_external = check_external_duplication(
        df_unique_internal,
        db=db,
        max_sep=max_sep,
    )
    # df_unique_external.rename(columns={"index": "index_"}, inplace=True)
    df_unique_external.to_csv("test_unique_external.csv", index=False)
    df_duplicate_external.to_csv("test_duplicate_external.csv", index=False)

    print("#")
    print("# Result of external duplication check")
    print("#")

    print("# unique objects: ")
    print(df_unique_external)

    print("# duplicated objects: ")
    print(df_duplicate_external)

    if df_unique_external.empty:
        logger.info(
            "No unique object is found.  Nothing is inserted in the unique_object table."
        )
        df_target = df_unique_internal.copy()

        df_target["user_ra"] = df_target["ra"]
        df_target["user_dec"] = df_target["dec"]
        df_target["user_epoch"] = df_target[
            "epoch"
        ]  # TODO: need to check epoch as well...
        df_target["unique_object_id"] = df_duplicate_external["unique_object_id"]
        df_target["match_distance"] = df_duplicate_external["sep"]

        db = insert_simple(db, table="target", df=df_target)

    else:
        if args.skip_unique_object:
            logger.info("Skip inserting data into the unique_object table")

        else:
            # TODO: Insert unique objects into unique_object table with return_default=True
            # TODO: Make a DataFrame by putting necessary information like above
            # TODO: Insert targets into target table

            logger.info("Inserting unique_object")

            df_unique_object = df_unique_external.copy()[["ra", "dec", "epoch"]]
            print(df_unique_object)

            db, df_ret_unique_object = insert_simple(
                db, table="unique_object", df=df_unique_object, return_defaults=True
            )
            print(df_ret_unique_object)

            # print(df_ret["target_id"])

    return db


def main():

    args = get_arguments()

    db = connect_db(args.conf)

    if args.reset:
        logger.info("Reset database tables.")
        db.reset()

    if not args.skip_proposal_category:
        logger.info("Inserting sample data into the proposal_category table")
        db = insert_simple(
            db, table="proposal_category", csv="../data/proposal_category.csv"
        )

    if not args.skip_proposal:
        logger.info("Inserting sample data into the proposal table")
        db = insert_proposal(db)

    if not args.skip_input_catalog:
        logger.info("Inserting sample data into the input_catalog table")
        db = insert_simple(db, table="input_catalog", csv="../data/input_catalog.csv")

    if not args.skip_target_type:
        logger.info("Inserting sample data into the target_type table")
        db = insert_simple(db, table="target_type", csv="../data/target_type.csv")

    if not args.skip_target:
        logger.info("Inserting sample data into the target/unique_object table")
        db = insert_target(db, args, max_sep=0.5 * u.arcsec)

    db.close()


if __name__ == "__main__":
    # conf = "targetdb_config.ini"
    # reset = True
    # reset = False
    main()
