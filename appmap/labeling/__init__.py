""" This module provides predefined labels for some common library functions.
For consistency, the labels are defined in YAML data files in this module,
structured exactly like the labels section in appmap.yml.
"""

from functools import lru_cache

import yaml
from importlib_resources import files

from _appmap.labels import LabelSet


@lru_cache(maxsize=None)
def presets():
    """Load the LabelSet of the presets included with appmap-python."""
    labels = []
    for resource in files(__name__).iterdir():
        if resource.suffix == ".yml":
            loaded = yaml.safe_load(resource.read_text())
            labels.append(loaded)
    return labels
