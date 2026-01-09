#!/usr/bin/env python

from .targetdb import TargetDB

try:
    from ._version import version as __version__
except ImportError:
    # Fallback for development without build
    __version__ = "0.0.0+unknown"

__all__ = ["TargetDB", "__version__"]
