#!/bin/sh

PY_SCRIPT="targetdb_api_utils.py"

if [ $HOSTNAME == "pfsa-usr01-gb.subaru.nao.ac.jp" ]; then
    DB_CONF_FILE="../../../database_configs/targetdb_config_pfsa-db01-gb_commissioning_2022may.ini"
else
    DB_CONF_FILE="../../../database_configs/targetdb_config.ini"
fi

STARDATA_DIR="../../../external_data/commissioning_2022may/fluxstd_ishigaki/feather/"
STARDATA_PREFIX="fluxstd_v1.0"

SKYDATA_DIR="../../../external_data/commissioning_2022may/sky_murata/feather/"
SKYDATA_PREFIX=""

COSMOLOGY_DIR="../../../external_data/commissioning_2022may/cosmology/"

MISCDATA_DIR="../../../external_data/commissioning_2022may/misc/"

RESET_ALL=false

while true; do
    read -p "Do you wish to reset ALL tables in targetDB? [y(es)/n(o)]" yn
    case $yn in
    [Yy]*)
        RESET_ALL=true
        break
        ;;
    [Nn]*)
        RESET_ALL=false
        break
        ;;
    *) echo "Please answer yes or no." ;;
    esac
done

if [ ${RESET_ALL} = true ]; then
    echo "RESETTING ALL TABLES"
    python ./${PY_SCRIPT} ${DB_CONF_FILE} \
        --reset all \
        --skip_proposal_category \
        --skip_proposal \
        --skip_input_catalog \
        --skip_target_type \
        --skip_target \
        --skip_fluxstd \
        --skip_sky
fi

while true; do
    read -p "Do you wish to ingest data into proposal_category, proposal, input_catalog, and target_type tables in targetDB? [y(es)/n(o)]" yn
    case $yn in
    [Yy]*)
        INSERT_MISC=true
        break
        ;;
    [Nn]*)
        INSERT_MISC=false
        break
        ;;
    *) echo "Please answer yes or no." ;;
    esac
done

# populate tables other than fluxstd and target by resetting all tables
if [ $INSERT_MISC == true ]; then
    python ./${PY_SCRIPT} ${DB_CONF_FILE} \
        --proposal_category ${MISCDATA_DIR}/proposal_category.csv \
        --proposal ${MISCDATA_DIR}/proposal.csv \
        --input_catalog ${MISCDATA_DIR}/input_catalog.csv \
        --target_type ${MISCDATA_DIR}/target_type.csv \
        --skip_target \
        --skip_fluxstd \
        --skip_sky
fi

# populate the sky table
for sky in ${SKYDATA_DIR}/*.feather; do
    if [ -f $sky ]; then
        echo $sky
        python ./${PY_SCRIPT} ${DB_CONF_FILE} \
            --reset sky \
            --skip_proposal_category \
            --skip_proposal \
            --skip_input_catalog \
            --skip_target_type \
            --skip_target \
            --skip_fluxstd \
            --sky $sky
    fi
done

# populate the target table
for target in ${COSMOLOGY_DIR}/*.fits; do
    if [ -f $target ]; then
        python ./${PY_SCRIPT} ${DB_CONF_FILE} \
            --reset target \
            --skip_proposal_category \
            --skip_proposal \
            --skip_input_catalog \
            --skip_target_type \
            --skip_fluxstd \
            --skip_sky \
            --target $target
    fi
done

# populate the fluxstd table
for fluxstd in ${STARDATA_DIR}/${STARDATA_PREFIX}*.feather; do
    if [ -f $fluxstd ]; then
        python ./${PY_SCRIPT} ${DB_CONF_FILE} \
            --skip_proposal_category \
            --skip_proposal \
            --skip_input_catalog \
            --skip_target_type \
            --skip_target \
            --skip_sky \
            --fluxstd $fluxstd
    fi
done
