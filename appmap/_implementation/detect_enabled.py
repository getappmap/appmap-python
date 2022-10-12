"""
Detect if AppMap is enabled.
"""

import importlib
import logging
import os
from textwrap import dedent

logger = logging.getLogger(__name__)

RECORDING_METHODS = ["pytest", "unittest", "remote", "requests"]

# Detects whether AppMap recording should be enabled. This test can be
# performed generally, or for a particular recording method. Recording
# can be enabled explicitly, for example via APPMAP=true, or it can be
# enabled implicitly, by running in a dev or test web application
# environment. Recording can also be disabled explicitly, using
# environment variables.
class DetectEnabled:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logger.debug("Creating the DetectEnabled object")
            cls._instance = super(DetectEnabled, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._detected_for_method = {}

    @classmethod
    def initialize(cls):
        cls._instance = None
        # because apparently __new__ and __init__ don't get called
        cls._detected_for_method = {}

    @classmethod
    def clear_cache(cls):
        cls._detected_for_method = {}

    @classmethod
    def is_appmap_repo(cls):
        return os.path.exists("appmap/__init__.py") and os.path.exists(
            "appmap/_implementation/__init__.py"
        )

    @classmethod
    def should_enable(cls, recording_method):
        """
        Should recording be enabled for the current recording method?
        """
        if recording_method in cls._detected_for_method:
            return cls._detected_for_method[recording_method]
        else:
            message, enabled = cls.detect_should_enable(recording_method)
            cls._detected_for_method[recording_method] = enabled
            if enabled:
                logger.warning(dedent(f"AppMap recording is enabled because {message}"))
            return enabled

    @classmethod
    def detect_should_enable(cls, recording_method):
        if not recording_method:
            return ["no recording method is set", False]

        if recording_method not in RECORDING_METHODS:
            return ["invalid recording method", False]

        # explicitly disabled or enabled
        if "APPMAP" in os.environ:
            if os.environ["APPMAP"] == "false":
                return ["APPMAP=false", False]
            elif os.environ["APPMAP"] == "true":
                return ["APPMAP=true", True]

        # recording method explicitly disabled or enabled
        if recording_method:
            for one_recording_method in RECORDING_METHODS:
                if one_recording_method == recording_method.lower():
                    env_var = "_".join(["APPMAP", "RECORD", recording_method.upper()])
                    if env_var in os.environ:
                        if os.environ[env_var] == "false":
                            return [f"{env_var}=false", False]
                        elif os.environ[env_var] == "true":
                            return [f"{env_var}=true", True]

        # it's flask
        message, should_enable = cls.is_flask_and_should_enable()
        if should_enable == True or should_enable == False:
            return [message, should_enable]

        # it's django
        message, should_enable = cls.is_django_and_should_enable()
        if should_enable == True or should_enable == False:
            return [message, should_enable]

        if recording_method in RECORDING_METHODS:
            return ["will record by default", True]

        return ["it's not enabled by any configuration or framework", False]

    @classmethod
    def is_flask_and_should_enable(cls):
        if "FLASK_DEBUG" in os.environ:
            if os.environ["FLASK_DEBUG"] == "1":
                return [f"FLASK_DEBUG={os.environ['FLASK_DEBUG']}", True]
            elif os.environ["FLASK_DEBUG"] == "0":
                return [f"FLASK_DEBUG={os.environ['FLASK_DEBUG']}", False]

        if "FLASK_ENV" in os.environ:
            if os.environ["FLASK_ENV"] == "development":
                return [f"FLASK_ENV={os.environ['FLASK_ENV']}", True]
            elif os.environ["FLASK_ENV"] == "production":
                return [f"FLASK_ENV={os.environ['FLASK_ENV']}", False]

        return ["it's not Flask", None]

    @classmethod
    def is_django_and_should_enable(cls):
        if (
            "DJANGO_SETTINGS_MODULE" in os.environ
            and os.environ["DJANGO_SETTINGS_MODULE"] != ""
        ):
            try:
                settings = importlib.import_module(os.environ["DJANGO_SETTINGS_MODULE"])
            except Exception as exn:
                settings = None
                return [
                    "couldn't load DJANGO_SETTINGS_MODULE={os.environ['DJANGO_SETTINGS_MODULE']}",
                    False,
                ]

            if settings:
                try:
                    # don't crash if the settings file doesn't contain
                    # a DEBUG variable
                    if settings.DEBUG == True:
                        return [
                            f"{os.environ['DJANGO_SETTINGS_MODULE']}.DEBUG={settings.DEBUG}",
                            True,
                        ]
                    elif settings.DEBUG == False:
                        return [
                            f"{os.environ['DJANGO_SETTINGS_MODULE']}.DEBUG={settings.DEBUG}",
                            False,
                        ]
                except AttributeError as exn:
                    # it wasn't set. it's ok. don't crash
                    # AttributeError: module 'app.settings_appmap_false' has no attribute 'DEBUG'
                    pass

            if settings:
                try:
                    # don't crash if the settings file doesn't contain
                    # an APPMAP variable
                    if (
                        settings.APPMAP == True
                        or str(settings.APPMAP).upper() == "true".upper()
                    ):
                        return [
                            f"{os.environ['DJANGO_SETTINGS_MODULE']}.APPMAP={settings.APPMAP}",
                            True,
                        ]
                    elif (
                        settings.APPMAP == False
                        or str(settings.APPMAP).upper() == "false".upper()
                    ):
                        return [
                            f"{os.environ['DJANGO_SETTINGS_MODULE']}.APPMAP={settings.APPMAP}",
                            False,
                        ]
                except AttributeError as exn:
                    # it wasn't set. it's ok. don't crash
                    # AttributeError: module 'app.settings_appmap_false' has no attribute 'APPMAP'
                    pass

        return ["it's not Django", None]
