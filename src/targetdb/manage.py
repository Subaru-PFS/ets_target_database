#!/usr/bin/env python3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base


def create_schema(dbinfo, drop_all=False):
    """
    dbinfo is something like this: postgresql://xxxxx:yyyyy@zzz.zzz.zzz.zz/dbname
    """

    engine = create_engine(dbinfo)

    if drop_all:
        Base.metadata.drop_all(engine)

    Base.metadata.create_all(engine)

    # Session = sessionmaker(bind=engine)
    # Session()
