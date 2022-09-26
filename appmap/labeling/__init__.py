""" This module provides predefined labels for some common library functions.
For consistency, the labels are defined in YAML data files in this module,
structured exactly like the labels section in appmap.yml.
"""

import yaml
from importlib_resources import files

from .._implementation.labels import LabelSet


def presets() -> LabelSet:
    """Load the LabelSet of the presets included with appmap-python."""
    labels = LabelSet()
    for resource in files(__name__).iterdir():
        if resource.suffix == ".yml":
            labels.append(yaml.safe_load(resource.read_text()))
    return labels
