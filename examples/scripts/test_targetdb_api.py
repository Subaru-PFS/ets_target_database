#!/usr/bin/env python

import datetime

import pandas as pd

from targetdb import targetdb


def main():
    hostname = "localhost"
    port = 15432
    dbname = "targetdb"
    username = "admin"
    password = "admin"

    db = targetdb.TargetDB(
        hostname=hostname,
        port=port,
        dbname=dbname,
        username=username,
        passwd=password,
    )
    db.connect()

    res = db.fetch_all("proposal_category")
    print(res)

    # db.reset()
    # res = db.fetch_all("proposal_category")
    # print(res)

    # utcnow = datetime.datetime.utcnow()
    # df = pd.DataFrame(
    #     {
    #         "proposal_category_name": ["openuse", "keck", "gemini", "uh"],
    #         "proposal_category_description": [
    #             "Subaru openuse proposals",
    #             "Subaru-Keck time exchange proposals",
    #             "Subaru-Gemini time exchange proposals",
    #             "University of Hawaii proposals",
    #         ],
    #         "created_at": [utcnow, utcnow, utcnow, utcnow],
    #         "updated_at": [utcnow, utcnow, utcnow, utcnow],
    #     }
    # )

    # db.insert("proposal_category", df)
    # res = db.fetch_all("proposal_category")
    # print(res)

    # # this should make error as 'proposal_category_name` must be unique.
    # db.insert("proposal_category", df)
    # res = db.fetch_all("proposal_category")
    # print(res)

    res = db.fetch_query(
        "SELECT proposal_category_id FROM proposal_category WHERE proposal_category_name='uh';"
    )
    print(res)

    db.close()


if __name__ == "__main__":
    main()
