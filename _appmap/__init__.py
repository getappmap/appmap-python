"""PYTEST_DONT_REWRITE"""

from . import configuration, event, importer, metadata, recorder, recording, web_framework
from . import env as appmapenv
from .py_version_check import check_py_version


def initialize(**kwargs):
    check_py_version()
    appmapenv.initialize(**kwargs)
    event.initialize()
    importer.initialize()
    recorder.initialize()
    configuration.initialize()  # needs to be initialized after recorder
    metadata.initialize()
    web_framework.initialize()
    recording.initialize()


initialize()
