#!/bin/bash

set -euxo pipefail

PY_SCRIPT="targetdb_api_utils.py"

DB_CONF_FILE="/work/monodera/Subaru-PFS/database_configs/config_pfsa-db01-gb_commissioning_2022nov.toml"

STARDATA_DIR="/work/monodera/Subaru-PFS/external_data/commissioning_2022nov/fluxstd/Fstar_v2.0/feather/v2.1/"

# populate the fluxstd table
for fluxstd in ${STARDATA_DIR}/*.feather; do
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
