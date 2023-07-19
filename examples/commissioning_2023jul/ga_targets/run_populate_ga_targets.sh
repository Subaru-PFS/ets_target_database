#!/bin/bash

#set -euxo pipefail

PY_SCRIPT="targetdb_api_utils.py"

echo "Working on ${HOSTNAME}"

DATADIR="/work/pfs/commissioning/2023jul/commissioning/data/ga_targets_2023jul"
CONFFILE="/work/pfs/commissioning/2023jul/commissioning/configs/config.toml"

#DRY_RUN="--dry_run"
DRY_RUN=""

# INSERT INTO input_catalog (input_catalog_id, input_catalog_name, input_catalog_description, created_at, updated_at) VALUES (90006, 'eng_ngc7078', 'NGC7078 for the engineering run in July 2023', current_timestamp, current_timestamp);
# INSERT INTO input_catalog (input_catalog_id, input_catalog_name, input_catalog_description, created_at, updated_at) VALUES (90007, 'eng_ngc7089', 'NGC7089 for the engineering run in July 2023', current_timestamp, current_timestamp);
# INSERT INTO input_catalog (input_catalog_id, input_catalog_name, input_catalog_description, created_at, updated_at) VALUES (90008, 'eng_ngc7099', 'NGC7099 for the engineering run in July 2023', current_timestamp, current_timestamp);

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

#python3 ./insert_ga_targets.py ${CONFFILE} \
#    --infile ${DATADIR}/ga_targets_GC_NGC7078.ecsv --proposal_id S23A-EN16 $DRY_RUN

#python3 ./insert_ga_targets.py ${CONFFILE} \
#    --infile ${DATADIR}/ga_targets_GC_NGC7089.ecsv --proposal_id S23A-EN16 $DRY_RUN

python3 ./insert_ga_targets.py ${CONFFILE} \
    --infile ${DATADIR}/ga_targets_GC_NGC7099.ecsv --proposal_id S23A-EN16 $DRY_RUN
