#!/bin/sh

DB_CONF_FILE="../../../database_configs/targetdb_config_pfsa-db01-gb.ini"
PY_SCRIPT="test_targetdb_api_comm_2021nov.py"
STARDATA_DIR="../../../../star_catalogs_ishigaki/"
STARDATA_PREFIX="target_fstars_v0.3_s21b-en16"

python ./${PY_SCRIPT} ${DB_CONF_FILE} --reset --skip_target

for target in ${STARDATA_DIR}/${STARDATA_PREFIX}*.feather; do
    python ./${PY_SCRIPT} ${DB_CONF_FILE} \
        --skip_proposal_category \
        --skip_proposal \
        --skip_input_catalog \
        --skip_target_type \
        --target $target
done
