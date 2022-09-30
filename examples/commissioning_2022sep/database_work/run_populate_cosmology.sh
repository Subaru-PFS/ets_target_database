#!/bin/bash

DATADIR="/work/monodera/Subaru-PFS/external_data/commissioning_2022sep/cosmology"
CONFFILE="../../../../database_configs/config_pfsa-db01-gb_commissioning_2022may.toml"

DRYRUN="--dry_run"
# DRYRUN=""

python ./append_cosmology_targets_2022sep.py \
    ${CONFFILE} ${DRYRUN} \
    --infile ${DATADIR}/hsc_pdr3_dud_deep23_247881.csv

python ./append_cosmology_targets_2022sep.py \
    ${CONFFILE} ${DRYRUN} \
    --infile ${DATADIR}/hsc_pdr3_dud_xmm_247882.csv
