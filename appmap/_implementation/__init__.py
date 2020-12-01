from . import configuration
from .recording import recorder

recorder.add_filter(configuration.BuiltinFilter.load_config())
recorder.add_filter(configuration.ConfigFilter.load_config())
