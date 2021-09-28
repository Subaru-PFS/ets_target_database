#!/usr/bin/env python

import configparser
import datetime

import pandas as pd
from targetdb import models
from targetdb import targetdb

# pd.options.display.max_columns = None


def connect_db(conf=None):

    config = configparser.ConfigParser()
    config.read(conf)

    print(dict(config["database"]))

    db = targetdb.TargetDB(**dict(config["database"]))

    db.connect()

    return db


def insert_simple(db, table=None, csv=None):
    df_input = pd.read_csv(csv)
    # df_input = pd.read_csv("../data/proposal_category.csv")
    n_input = len(df_input.index)

    try:
        print("trying to insert data into {:s}...".format(table))

        utcnow = datetime.datetime.utcnow()
        df_input["created_at"] = [utcnow] * n_input
        df_input["updated_at"] = [utcnow] * n_input

        db.insert(table, df_input)
    except:
        print("no unique value in the input data is found. skip.")

    res = db.fetch_all(table)
    print(res)

    return db


def insert_proposal(db):
    df_proposal = pd.read_csv("../data/proposal.csv")
    n_proposal = len(df_proposal.index)

    res = db.fetch_all("proposal_category")
    df_joined = df_proposal.merge(
        res,
        how="left",
        left_on="proposal_category_name",
        right_on="proposal_category_name",
    )
    print(df_joined)

    try:
        print("trying to insert data into proposal...")

        utcnow = datetime.datetime.utcnow()
        df_joined["created_at"] = [utcnow] * n_proposal
        df_joined["updated_at"] = [utcnow] * n_proposal

        db.insert("proposal", df_joined)
    except:
        print("no unique proposal_id is found. skip.")

    res = db.fetch_all("proposal")
    print(res)

    return db


def insert_target(db):
    df = pd.read_csv("../data/target_s21b-en01.csv")

    # extract_unique_objects_internally()

    # extract_unique_objects_with_existing_unique_object()


def main(conf=None, reset=False):

    db = connect_db(conf)

    if reset:
        db.reset()

    db = insert_simple(
        db, table="proposal_category", csv="../data/proposal_category.csv"
    )

    db = insert_proposal(db)

    db = insert_simple(db, table="input_catalog", csv="../data/input_catalog.csv")

    db = insert_simple(db, table="object_type", csv="../data/object_type.csv")

    db.close()


if __name__ == "__main__":
    conf = "targetdb_config.ini"
    # reset = True
    reset = False
    main(conf, reset=reset)
