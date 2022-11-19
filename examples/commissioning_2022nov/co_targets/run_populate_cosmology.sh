#!/bin/bash

set -euxo pipefail

PY_SCRIPT="targetdb_api_utils.py"

DATADIR="/work/monodera/Subaru-PFS/external_data/commissioning_2022nov/co_targets"
CONFFILE="/work/monodera/Subaru-PFS/database_configs/config_pfsa-db01-gb_commissioning_2022nov.toml"

DRYRUN="--dry_run"
# DRYRUN=""

# # Populate input catalogs
# python3 ./${PY_SCRIPT} ${CONFFILE} \
#     --skip_proposal_category \
#     --proposal ${DATADIR}/proposal.csv \
#     --skip_input_catalog \
#     --skip_target_type \
#     --skip_target \
#     --skip_fluxstd \
#     --skip_sky

python ./append_cosmology_targets_2022nov.py \
    ${CONFFILE} ${DRYRUN} \
    --infile ${DATADIR}/hsc_pdr3_dud_cos_281603.csv \
    --proposal_id "S22B-EN16-CO" \
    --input_catalog "hscssp_pdr3_dud"

python ./append_cosmology_targets_2022nov.py \
    ${CONFFILE} ${DRYRUN} \
    --infile ${DATADIR}/hsc_pdr3_wide_field1_283144_sampled.csv \
    --proposal_id "S22B-EN16-CO" \
    --input_catalog "hscssp_pdr3_wide"

python ./append_cosmology_targets_2022nov.py \
    ${CONFFILE} ${DRYRUN} \
    --infile ${DATADIR}/hsc_pdr3_wide_field2_283146_sampled.csv \
    --proposal_id "S22B-EN16-CO" \
    --input_catalog "hscssp_pdr3_wide"
