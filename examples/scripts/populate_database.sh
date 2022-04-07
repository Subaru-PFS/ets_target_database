#!/bin/sh

DB_CONF_FILE="../../../database_configs/targetdb_config.ini"
PY_SCRIPT="test_targetdb_api_comm_2021nov.py"
PY_SCRIPT_FLUXSTD="test_insert_fluxstd.py"
STARDATA_DIR="../../../external_data/"
STARDATA_FILE="Fstar_v1.0_part.csv"

python ./${PY_SCRIPT} ${DB_CONF_FILE} --reset --skip_target

python ./${PY_SCRIPT_FLUXSTD} ${DB_CONF_FILE} --fluxstd $STARDATA_DIR/$STARDATA_FILE

# for target in ${STARDATA_DIR}/${STARDATA_PREFIX}*.feather; do
#     python ./${PY_SCRIPT} ${DB_CONF_FILE} \
#         --skip_proposal_category \
#         --skip_proposal \
#         --skip_input_catalog \
#         --skip_target_type \
#         --target $target
# done
