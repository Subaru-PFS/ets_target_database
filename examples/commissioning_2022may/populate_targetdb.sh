#!/bin/sh

# DB_CONF_FILE="../../../database_configs/targetdb_config_pfsa-db01-gb.ini"
DB_CONF_FILE="../../../database_configs/targetdb_config.ini"
PY_SCRIPT="targetdb_api_utils.py"
STARDATA_DIR="../../../../star_catalogs_ishigaki/commissioning_2022may/feather/"
STARDATA_PREFIX="target_fstars_v1.0_s22a-en16"

# populate tables other than fluxstd and target
python ./${PY_SCRIPT} ${DB_CONF_FILE} --reset --skip_target --skip_fluxstd

# populate the fluxstd table
for fluxstd in ${STARDATA_DIR}/${STARDATA_PREFIX}*.feather; do
    python ./${PY_SCRIPT} ${DB_CONF_FILE} \
        --skip_proposal_category \
        --skip_proposal \
        --skip_input_catalog \
        --skip_target_type \
        --skip_target \
        --fluxstd $fluxstd
done