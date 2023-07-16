#!/bin/bash

set -euxo pipefail

PY_SCRIPT="targetdb_api_utils.py"

DATADIR="/work/pfs/commissioning/2023jul/commissioning/data/co_targets_2023jul"
CONFFILE="/work/pfs/commissioning/2023jul/commissioning/configs/config.toml"

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

python ./append_cosmology_targets_2023jul.py \
    ${CONFFILE} ${DRYRUN} \
    --infile ${DATADIR}/hsc_pdr3_wide_run12_field1_422660_sampled.csv \
    --input_catalog "hscssp_pdr3_wide"

python ./append_cosmology_targets_2023jul.py \
    ${CONFFILE} ${DRYRUN} \
    --infile ${DATADIR}/hsc_pdr3_wide_run12_field1_422661_sampled.csv \
    --input_catalog "hscssp_pdr3_wide"
