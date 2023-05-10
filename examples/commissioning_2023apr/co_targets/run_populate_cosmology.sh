#!/bin/bash

set -euxo pipefail

PY_SCRIPT="targetdb_api_utils.py"

DATADIR="/work/pfs/commissioning/2023apr/commissioning/data"
CONFFILE="/work/pfs/commissioning/2023apr/commissioning/configs/config.toml"

#DRYRUN="--dry_run"
DRYRUN=""

# # Populate input catalogs
# python3 ./${PY_SCRIPT} ${CONFFILE} \
#     --skip_proposal_category \
#     --proposal ${DATADIR}/proposal.csv \
#     --skip_input_catalog \
#     --skip_target_type \
#     --skip_target \
#     --skip_fluxstd \
#     --skip_sky

python ./append_cosmology_targets_2023apr.py \
    ${CONFFILE} ${DRYRUN} \
    --infile ${DATADIR}/hsc_pdr3_wide_run11_field2_417771_sampled.csv \
    --input_catalog "hscssp_pdr3_wide"
