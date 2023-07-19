#!/bin/bash

set -euxo pipefail

PY_SCRIPT="targetdb_api_utils.py"

DATADIR="/work/pfs/commissioning/2023jul/commissioning/data/ge_targets_2023jul"
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

python ./append_ge_specz_targets_2023jul.py \
    ${CONFFILE} ${DRYRUN} \
    --infile ${DATADIR}/hsc_pdf3_dud_run12_en1_422712.csv \
    --input_catalog "hscssp_pdr3_dud"

python ./append_ge_specz_targets_2023jul.py \
    ${CONFFILE} ${DRYRUN} \
    --infile ${DATADIR}/hsc_pdf3_dud_run12_d23_422713.csv \
    --input_catalog "hscssp_pdr3_dud"
