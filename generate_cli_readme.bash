#!/bin/bash

set -e

typer targetdb.cli.cli_main utils docs --name pfs-targetdb-cli | sed 's/# `/## `/g' | sed 's/###/---\n\n###/g' | sed 's/`pfs-targetdb-cli\ /`/g'
