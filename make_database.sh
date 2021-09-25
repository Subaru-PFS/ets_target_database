#!/bin/bash

# set -euxo pipefail

## create DB ##
# CREATE DATABASE dbname;

## connect to the database ##
# psql -h hostname -p port -U username -d dbname

## if necessary, delete all schema in the database as follows ##
# DROP SCHEMA PUBLIC CASCADE;
# CREATE SCHEMA PUBLIC;

hostname="localhost"
port="15432"
dbname="targetdb_test"
# dbname="postgres"
username="admin"
password="admin"
drop_all="--drop_all"
# drop_all=""
schema_md="--schema_md schema_targetdb_tables.md"

## make schema ##
url="postgresql://${username}:${password}@${hostname}:${port}/${dbname}"

python test_make_database.py ${url} ${drop_all} ${schema_md}

success=$?

# exit

if [ $success -ne 0 ]; then
    echo ""
    echo "Failed during running models_target_db.py. Exit."
    echo ""
    exit 1
fi

# exit

## make schema diagram ##
SCHEMACRAWLERDIR="../schemacrawler-16.15.4-distribution/"

# SL_INFO_LEVEL="standard"
SC_INFO_LEVEL="detailed"

#   Options:
#   --log-level=<loglevel>
#      Set log level using one of OFF, SEVERE, WARNING, INFO, CONFIG, FINE,
#        FINER, FINEST, ALL
#      Optional, defaults to OFF
# SC_LOG_LEVEL="CONFIG"
SC_LOG_LEVEL="SEVERE"

SC_OUTPUT_FILE_PREFIX="schema_targetdb"

rm -f ${SC_OUTPUT_FILE_PREFIX}.pdf

./${SCHEMACRAWLERDIR}/_schemacrawler/schemacrawler.sh \
    --server=postgresql \
    --host=${hostname} \
    --port=${port} \
    --database=${dbname} \
    --schemas=public \
    --user=${username} \
    --password=${password} \
    --info-level=${SC_INFO_LEVEL} \
    --command=schema \
    --log-level=${SC_LOG_LEVEL} \
    --portable-names \
    --title='PFS Target Database (Prototype)' \
    --output-format=pdf \
    --output-file=${SC_OUTPUT_FILE_PREFIX}.pdf \
    --no-remarks
