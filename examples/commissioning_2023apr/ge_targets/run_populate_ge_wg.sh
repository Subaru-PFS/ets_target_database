#!/bin/bash

#set -euxo pipefail

PY_SCRIPT="targetdb_api_utils.py"

DATADIR="/work/pfs/commissioning/2023apr/commissioning/data/ge_targets"
CONFFILE="/work/pfs/commissioning/2023apr/commissioning/configs/config.toml"

DRYRUN="--dry_run"
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

#python ./append_ge_wg_targets_additional_2023apr.py \
#    ${CONFFILE} ${DRYRUN} \
#    --infile ${DATADIR}/RQG_y_brightest.cat \
#    --input_catalog "hscssp_pdr3_dud"

DATADIR="/work/pfs/commissioning/2023apr/commissioning/data"

#python ./append_ge_specz_targets_2023apr.py \
#    ${CONFFILE} ${DRYRUN} \
#    --infile ${DATADIR}/hsc_pdr3_dud_en1_418030.csv \
#    --input_catalog "hscssp_pdr3_dud" \
#    --proposal_id "S22B-EN16-CO"

#python ./append_ge_photometric_targets_2023apr.py \
#    ${CONFFILE} ${DRYRUN} \
#    --infile ${DATADIR}/hsc_pdr3_dud_cos_418033.csv \
#    --input_catalog "hscssp_pdr3_dud" \
#    --proposal_id "S22B-EN16-CO"

#python ./append_ge_photometric_targets_2023apr.py \
#    ${CONFFILE} ${DRYRUN} \
#    --infile ${DATADIR}/hsc_pdr3_dud_en1_418032.csv \
#    --input_catalog "hscssp_pdr3_dud" \
#    --proposal_id "S22B-EN16-CO"

#python ./append_ge_emission_targets_2023apr.py \
#    ${CONFFILE} ${DRYRUN} \
#    --infile ${DATADIR}/hsc_pdr3_dud_en1_418054.csv \
#    --input_catalog "hscssp_pdr3_dud" \
#    --proposal_id "S22B-EN16-CO"

python ./append_ge_specz_deep_targets_2023apr.py \
    ${CONFFILE} ${DRYRUN} \
    --infile ${DATADIR}/hsc_pdr3_dud_en1_418030.csv \
    --input_catalog "hscssp_pdr3_dud" \
    --proposal_id "S22B-EN16-CO"
