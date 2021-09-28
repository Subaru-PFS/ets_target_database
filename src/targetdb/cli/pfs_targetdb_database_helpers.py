#!/usr/bin/env python

import argparse
import sys

from sqlalchemy import create_engine
from sqlalchemy_utils import create_database
from sqlalchemy_utils import database_exists
from sqlalchemy_utils import drop_database


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Create targetDB itself on PostgreSQL."
    )
    parser.add_argument(
        "dbinfo",
        type=str,
        help="Database URL (postgresql://user:password@hostname:port/dbname)",
    )

    args = parser.parse_args()

    return args


def main_create_database():
    args = get_arguments()

    print(args)

    engine = create_engine(args.dbinfo)

    if not database_exists(engine.url):
        print("Creating database: {:s}".format(args.dbinfo))
        create_database(engine.url)
    else:
        print("Database already exists: {:s}".format(args.dbinfo))


def main_drop_database():
    args = get_arguments()

    print(args)

    engine = create_engine(args.dbinfo)

    if database_exists(engine.url):
        print(
            "WARNING: you are going to delete the database, {:s}.".format(args.dbinfo)
        )
        proceed = query_yes_no("Proceed? ", default="no")
        if proceed:
            print("Dropping database: {:s}".format(args.dbinfo))
            drop_database(engine.url)
    else:
        print("Database does not exist: {:s}".format(args.dbinfo))


if __name__ == "__main__":
    pass
