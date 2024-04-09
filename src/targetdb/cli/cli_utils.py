#!/usr/bin/env python3

import os

import pandas as pd
from astropy.table import Table
from loguru import logger

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def load_config(config_file):
    with open(config_file, "rb") as fp:
        config = tomllib.load(fp)
    return config


def load_input_data(input_file, logger=logger):
    _, ext = os.path.splitext(input_file)
    if ext == ".csv":
        df = pd.read_csv(input_file)
    elif ext == ".feather":
        df = pd.read_feather(input_file)
    elif ext == ".ecsv":
        df = Table.read(input_file).to_pandas()
    else:
        logger.error(f"Unsupported file extension: {ext}")
        raise ValueError(f"Unsupported file extension: {ext}")
    return df
