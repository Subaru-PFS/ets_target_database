#!/bin/bash

set -euxo pipefail

PY_SCRIPT="targetdb_api_utils.py"

echo "Working on ${HOSTNAME}"

DB_CONF_FILE="../../../../database_configs/config_pfsa-db01-gb_commissioning_2022nov.toml"

EXTERNALDATA_DIR="../../../../external_data/commissioning_2022nov/"

DRY_RUN="--dry_run"
# DRY_RUN=""

# # Populate input catalogs
# python3 ./${PY_SCRIPT} ${DB_CONF_FILE} \
#     --skip_proposal_category \
#     --skip_proposal \
#     --input_catalog ${EXTERNALDATA_DIR}/ga_targets/input_catalog_ga.csv \
#     --skip_target_type \
#     --skip_target \
#     --skip_fluxstd \
#     --skip_sky

# GA targets
python3 ./insert_ga_targets.py ${DB_CONF_FILE} \
    --infile ${EXTERNALDATA_DIR}/ga_targets/ga_targets_field.ecsv $DRY_RUN

python3 ./insert_ga_targets.py ${DB_CONF_FILE} \
    --infile ${EXTERNALDATA_DIR}/ga_targets/ga_targets_GC.ecsv $DRY_RUN
