from . import configuration
from . import env
from . import event
from . import recording
from .py_version_check import check_py_version


def initialize():
    check_py_version()
    env.initialize()
    event.initialize()
    recording.initialize()
    configuration.initialize()  # needs to be initialized after recording


initialize()
