#!/bin/sh

PY_SCRIPT="targetdb_api_utils.py"
STARDATA_PREFIX="fstars_v1.0"

DB_CONF_FILE="../../../database_configs/targetdb_config.ini"
STARDATA_DIR="../../../../star_catalogs_ishigaki/commissioning_2022may/feather/"

SKYDATA_DIR="../../../../sky_catalog_murata/commissioning_2022may/feather/"
SKYDATA_PREFIX=""

if [ $HOSTNAME == "pfsa-usr01-gb.subaru.nao.ac.jp" ]; then
    DB_CONF_FILE="../../../database_configs/targetdb_config_pfsa-db01-gb.ini"
    STARDATA_DIR="../../../../star_catalog_ishigaki/commissioning_2022may/PFS_TargetList/feather/"
fi

# populate tables other than fluxstd and target
python ./${PY_SCRIPT} ${DB_CONF_FILE} --reset --skip_target --skip_fluxstd --skip_sky

# populate the fluxstd table
for fluxstd in ${STARDATA_DIR}/${STARDATA_PREFIX}*.feather; do
    if [ -f $fluxstd ]; then
        python ./${PY_SCRIPT} ${DB_CONF_FILE} \
            --skip_proposal_category \
            --skip_proposal \
            --skip_input_catalog \
            --skip_target_type \
            --skip_target \
            --skip_sky \
            --fluxstd $fluxstd
    fi
done

# # populate the sky table
# for sky in ${SKYDATA_DIR}/${SKYDATA_PREFIX}*.feather; do
#     if [ -f $sky ]; then
#         python ./${PY_SCRIPT} ${DB_CONF_FILE} \
#             --skip_proposal_category \
#             --skip_proposal \
#             --skip_input_catalog \
#             --skip_target_type \
#             --skip_target \
#             --skip_fluxstd \
#             --sky $sky
#     fi
# done
