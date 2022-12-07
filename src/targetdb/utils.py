#!/usr/bin/env python

import datetime
import os
import subprocess
import sys

import logzero
import pandas as pd
import toml
from logzero import logger

from .models import Base


def read_conf(conf_file):
    config = toml.load(conf_file)
    return config


def generate_schema_markdown(schema_md=sys.stdout):

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

            df_tmp = pd.DataFrame(
                data={
                    "name": [c.name],
                    "type": [c.type],
                    "primary_key": [c.primary_key],
                    "autoincrement": [autoincrement],
                    "comment": [c.comment],
                },
            )
            df = pd.concat(
                [df, df_tmp],
                ignore_index=True,
            )

        out_md += df.to_markdown(index=False)

        out_md += "\n"

        # print(df.to_markdown(index=False))

    try:
        with open(schema_md, "w") as f:
            f.write(out_md)
    except TypeError:
        print(out_md)

    # return out_md


def draw_diagram(
    conf_file,
    sc_info_level="maximum",
    sc_log_level="SEVERE",
    sc_outdir=".",
    sc_outprefix="erdiagram_targetdb",
    sc_title="PFS Target Database",
    logger=logger,
):

    conf = read_conf(conf_file)

    time_string = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    outfile = os.path.join(sc_outdir, f"{sc_outprefix}-{time_string}.pdf")

    comm = [
        f"{os.path.join(conf['schemacrawler']['SCHEMACRAWLERDIR'],'_schemacrawler/bin/schemacrawler.sh')}",
        f"--command=schema",
        f"--server=postgresql",
        f"--host={conf['targetdb']['db']['host']}",
        f"--port={conf['targetdb']['db']['port']}",
        f"--database={conf['targetdb']['db']['dbname']}",
        f"--schemas=public",
        f"--user={conf['targetdb']['db']['user']}",
        f"--password={conf['targetdb']['db']['password']}",
        f"--info-level={sc_info_level}",
        f"--log-level={sc_log_level}",
        f"--portable-names",
        f"--title={sc_title}",
        f"--output-format=pdf",
        f"--output-file={outfile}",
        f"--no-remarks",
    ]

    logger.debug(f"{comm}")

    subprocess.run(comm, shell=False)


# /work/monodera/schemacrawler/_schemacrawler/bin/schemacrawler.sh --command=schema --server=postgresql --host=pfsa-db01-gb --port=5433 --database=targetdb_comm2022may --schemas=public --user=pfs --password=pfs_hilo_opdb --info-level=maximum --log-level=SEVERE --portable-names --title=PFS Target Database --output-format=pdf --output-file=./erdiagram_targetdb-2022-10-19T19:12:06.pdf --no-remarks
