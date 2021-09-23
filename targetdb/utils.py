#!/usr/bin/env python

import sys

import pandas as pd

from .model import Base


def generate_schema_markdown(dbinfo, schema_md=sys.stdout):

    out_md = ""

    for t in Base.metadata.sorted_tables:

        out_md += "\n## {:s}\n\n".format(t.name)

        df = pd.DataFrame(
            [], columns=["name", "type", "primary_key", "autoincrement", "comment"]
        )

        for c in t.columns:

            if c.autoincrement == True:
                autoincrement = True
            else:
                autoincrement = False

            series = pd.Series(
                {
                    "name": c.name,
                    "type": c.type,
                    "primary_key": c.primary_key,
                    "autoincrement": autoincrement,
                    "comment": c.comment,
                },
            )

            df = df.append(series, ignore_index=True)

        out_md += df.to_markdown(index=False)

        out_md += "\n"

        # print(df.to_markdown(index=False))

    try:
        with open(schema_md, "w") as f:
            f.write(out_md)
    except TypeError:
        print(out_md)

    # return out_md
