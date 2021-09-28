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


def insert_proposal_category(db):
    df_proposal_category = pd.read_csv("../data/proposal_category.csv")
    n_proposal_category = len(df_proposal_category.index)

    try:
        print("trying to insert data into proposal_category...")

        utcnow = datetime.datetime.utcnow()
        df_proposal_category["created_at"] = [utcnow] * n_proposal_category
        df_proposal_category["updated_at"] = [utcnow] * n_proposal_category

        db.insert("proposal_category", df_proposal_category)
    except:
        print("no unique proposal_category_name is found. skip.")

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


def main(conf=None):

    db = connect_db(conf)

    # db.reset()

    # db = insert_proposal_category(db)

    # db = insert_proposal(db)

    db.close()


if __name__ == "__main__":
    conf = "targetdb_config.ini"
    main(conf)
