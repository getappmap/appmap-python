from . import env
from . import event
from . import recording
from . import configuration
from .py_version_check import check_py_version


def initialize():
    check_py_version()
    env.initialize()
    event.initialize()
    recording.initialize()
    configuration.initialize()


initialize()
