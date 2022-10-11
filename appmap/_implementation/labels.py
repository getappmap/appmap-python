from collections import defaultdict
from typing import Dict, List, Optional, Union

from .importer import Filterable


class labels:
    def __init__(self, *args):
        self._labels = args

    def __call__(self, fn):
        # For simplicity, set _appmap_labels right on the
        # function. We'll delete it when we instrument the function.
        setattr(fn, "_appmap_labels", self._labels)
        return fn


Label = str
FunctionName = str  # fully qualified
Config = Dict[Label, Union[FunctionName, List[FunctionName]]]


class LabelSet:
    """A set of labels defined to be applied on specific functions."""

    def __init__(self, config: Optional[Config] = None):
        """Create the LabelSet, optionally pre-populating it with the provided config."""
        self.labels = defaultdict(list)
        if config:
            self.append(config)

    def append(self, config: Config):
        """Update this LabelSet to contain definitions from the config."""
        for label, functions in config.items():
            if isinstance(functions, str):
                functions = (functions,)
            for function in functions:
                self.labels[function].append(label)

    def apply(self, function: Filterable) -> Optional[List[Label]]:
        """Searches the labelset for the function and applies any applicable labels.
        Returns them."""
        applicable = self.labels.get(function.fqname, None)
        if not applicable:
            return None
        labels(*applicable)(function.obj)
        return applicable

    def __repr__(self):
        if not self.labels:
            return "LabelSet()"
        inverted = defaultdict(list)
        for function, labels in self.labels.items():
            for label in labels:
                inverted[label].append(function)
        return "LabelSet(%s)" % dict(inverted)
