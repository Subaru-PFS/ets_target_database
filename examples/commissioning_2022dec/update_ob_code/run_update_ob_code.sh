#!/bin/bash

set -euxo pipefail

# DRY_RUN="--dry_run"
DRY_RUN=""

python3 ./generate_ob_code.py \
    /work/monodera/Subaru-PFS/database_configs/config_pfsa-db01-gb_commissioning_2022nov.toml ${DRY_RUN}
