#!/bin/sh

python ./test_targetdb_api_comm_2021nov.py targetdb_config.ini --reset --skip_target

for target in data/target_fstars_s21b-en16-0000??.csv; do
    python ./test_targetdb_api_comm_2021nov.py \
        targetdb_config.ini \
        --skip_proposal_category \
        --skip_proposal \
        --skip_input_catalog \
        --skip_target_type \
        --target $target
done
