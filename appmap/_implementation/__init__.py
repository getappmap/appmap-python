from . import configuration
from . import env as appmapenv
from . import event
from . import metadata
from . import recording
from .py_version_check import check_py_version


def initialize(env=None):
    check_py_version()
    appmapenv.initialize(env)
    event.initialize()
    recording.initialize()
    configuration.initialize()  # needs to be initialized after recording
    metadata.initialize()

initialize()
