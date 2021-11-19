#!/bin/bash

# set -euxo pipefail

## create DB ##
# CREATE DATABASE dbname;

## connect to the database ##
# psql -h hostname -p port -U username -d dbname

## if necessary, delete all schema in the database as follows ##
# DROP SCHEMA PUBLIC CASCADE;
# CREATE SCHEMA PUBLIC;

cfg.parser() {
    #
    # Ref: https://gist.github.com/splaspood/1473761
    #
    fixed_file=$(cat $1 | sed 's/ = /=/g') # fix ' = ' to be '='
    IFS=$'\n' && ini=($fixed_file)         # convert to line-array
    ini=(${ini[*]//;*/})                   # remove comments
    ini=(${ini[*]/#[/\}$'\n'cfg.section.}) # set section prefix
    ini=(${ini[*]/%]/ \(})                 # convert text2function (1)
    ini=(${ini[*]/=/=\( })                 # convert item to array
    ini=(${ini[*]/%/ \)})                  # close array parenthesis
    ini=(${ini[*]/%\( \)/\(\) \{})         # convert text2function (2)
    ini=(${ini[*]/%\} \)/\}})              # remove extra parenthesis
    ini[0]=''                              # remove first element
    ini[${#ini[*]} + 1]='}'                # add the last brace
    eval "$(echo "${ini[*]}")"             # eval the result
}

# cfg.parser "targetdb_config.ini"
cfg.parser "../../../database_configs/targetdb_config_pfsa-db01-gb.ini"
cfg.section.dbinfo
cfg.section.schemacrawler

drop_all="--drop_all"
# drop_all=""
out_dir="./"
out_md="schema_targetdb_tables.md"
schema_md="--schema_md=${out_dir}/${out_md}"

## make schema ##
url="postgresql://${user}:${password}@${host}:${port}/${dbname}"

# echo $url

# exit

# # CAUTION: drop database
# pfs_targetdb_drop_database ${url}

# create database if it does not exist

echo "Creating database:"
pfs_targetdb_create_database ${url}
echo ""

echo "Creating schema:"
pfs_targetdb_create_schema ${url} ${drop_all}
echo ""

# exit

echo "Writing Markdown tables for the schema"
pfs_targetdb_generate_mdtable ${schema_md}
# python test_make_database.py ${url} ${drop_all} ${schema_md}
echo ""

success=$?

if [ $success -ne 0 ]; then
    echo ""
    echo "Failed during running models_target_db.py. Exit."
    echo ""
    exit 1
fi

# exit

{ # try
    # md-to-pdf schema_targetdb_tables.md
    md-to-pdf ${out_dir}/${out_md} --basedir ${out_dir}
} || { # catch
    echo "to convert md to pdf, you need to install some software such as md-to-pdf (https://github.com/simonhaenisch/md-to-pdf#readme)"
}

# exit

echo "Generating ER diagram:"
## make schema diagram ##
# SCHEMACRAWLERDIR="../../../schemacrawler-16.15.4-distribution/"

# echo $SCHEMACRAWLERDIR

# exit

# SL_INFO_LEVEL="standard"
# SC_INFO_LEVEL="detailed"
SC_INFO_LEVEL="maximum"

#   Options:
#   --log-level=<loglevel>
#      Set log level using one of OFF, SEVERE, WARNING, INFO, CONFIG, FINE,
#        FINER, FINEST, ALL
#      Optional, defaults to OFF
# SC_LOG_LEVEL="ALL"
# SC_LOG_LEVEL="CONFIG"
SC_LOG_LEVEL="SEVERE"

SC_OUTPUT_DIR=${out_dir}
SC_OUTPUT_FILE_PREFIX="schema_targetdb"

rm -f ${SC_OUTPUT_FILE_PREFIX}.pdf

./${SCHEMACRAWLERDIR}/_schemacrawler/schemacrawler.sh \
    --server=postgresql \
    --host=${host} \
    --port=${port} \
    --database=${dbname} \
    --schemas=public \
    --user=${user} \
    --password=${password} \
    --info-level=${SC_INFO_LEVEL} \
    --command=schema \
    --log-level=${SC_LOG_LEVEL} \
    --portable-names \
    --title='PFS Target Database (Prototype)' \
    --output-format=pdf \
    --output-file=${SC_OUTPUT_DIR}/${SC_OUTPUT_FILE_PREFIX}.pdf \
    --no-remarks
