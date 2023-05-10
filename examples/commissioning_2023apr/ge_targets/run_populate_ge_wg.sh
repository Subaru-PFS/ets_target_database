#!/bin/bash

#set -euxo pipefail

PY_SCRIPT="targetdb_api_utils.py"

DATADIR="/work/pfs/commissioning/2023apr/commissioning/data/ge_targets"
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

#python ./append_ge_wg_targets_2023apr.py \
#    ${CONFFILE} ${DRYRUN} \
#    --infile ${DATADIR}/ge_run11_wg_cos.csv \
#    --input_catalog "hscssp_pdr3_dud"

#python ./append_ge_wg_targets_2023apr.py \
#    ${CONFFILE} ${DRYRUN} \
#    --infile ${DATADIR}/ge_run11_wg_en1.csv \
#    --input_catalog "hscssp_pdr3_dud"

python ./append_ge_wg_targets_additional_2023apr.py \
    ${CONFFILE} ${DRYRUN} \
    --infile ${DATADIR}/RQG_y_brightest.cat \
    --input_catalog "hscssp_pdr3_dud"
