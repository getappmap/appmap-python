from . import configuration
from . import env as appmapenv
from . import event
from . import metadata
from . import recording
from .py_version_check import check_py_version


def initialize(**kwargs):
    check_py_version()
    appmapenv.initialize(**kwargs)
    event.initialize()
    recording.initialize()
    configuration.initialize()  # needs to be initialized after recording
    metadata.initialize()

initialize()
