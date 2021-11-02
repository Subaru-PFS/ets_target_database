#!/bin/sh

DB_CONF_FILE="targetdb_config_pfsa-db01-gb.ini"
PY_SCRIPT="test_targetdb_api_comm_2021nov.py"

python ./${PY_SCRIPT} ${DB_CONF_FILE} --reset --skip_target

for target in data/target_fstars_s21b-en16-0000??.feather; do
    python ./${PY_SCRIPT} ${DB_CONF_FILE} \
        --skip_proposal_category \
        --skip_proposal \
        --skip_input_catalog \
        --skip_target_type \
        --target $target
done
