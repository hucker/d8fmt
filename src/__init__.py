"""
Define API for d8fmt
"""

from importlib.metadata import PackageNotFoundError, version


# Fetch the version from package metadata
try:
    __version__ = version("d8fmt")
except PackageNotFoundError as e:
    __version__ = "unknown"

    import warnings

    warnings.warn(f"Package metadata is unavailable; falling back to version: {__version__}")

# Import attributes, functions, and classes to be exposed as part of the public API
from .d8fmt import (
    DATETIME_LOOKUP_TABLE,
    is_zone_free,
    ez_format,
    datetime_ez,
)
from .constants import CANONICAL_DATE

# Define the public API with __all__
__all__ = [
    "CANONICAL_DATE",
    "DATETIME_LOOKUP_TABLE",
    "is_zone_free",
    "ez_format",
    "datetime_ez",
]
