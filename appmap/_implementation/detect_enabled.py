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
    _initialized = False
    _logged_at_least_once = False

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
            enabled, log_level, message = cls._detect_should_enable(recording_method)
            cls._detected_for_method[recording_method] = enabled
            # don't log enabled messages more than once
            if (not cls._logged_at_least_once and logger.isEnabledFor(log_level)):
                cls._logged_at_least_once = True
                logger.log(log_level, message)
            return enabled

    @classmethod
    def any_enabled(cls):
        for m in RECORDING_METHODS:
            if cls.should_enable(m):
                return True
        return False

    @classmethod
    def _log_prefix(cls, should_enable, log_message):
        enabled_prefix = ""
        if not should_enable:
            enabled_prefix = "not "

        return dedent(
            f"AppMap recording is {enabled_prefix}enabled because {log_message}."
        )

    @classmethod
    def _detect_should_enable(cls, recording_method):
        if not recording_method:
            return False, logging.WARNING, cls._log_prefix(False, "no recording method is set")

        if recording_method not in RECORDING_METHODS:
            return False, logging.WARNING, cls._log_prefix(
                    False, f"{recording_method} is an invalid recording method"
            )

        # explicitly disabled or enabled
        if "APPMAP" in os.environ:
            if os.environ["APPMAP"].lower() == "false":
                return False, logging.INFO, cls._log_prefix(False, f"APPMAP=false")
            elif os.environ["APPMAP"].lower() == "true":
                return True, logging.INFO, cls._log_prefix(True, f"APPMAP=true")
            else:
                return False, logging.WARNING, cls._log_prefix(False, f"APPMAP={os.environ['APPMAP']} is an invalid option")

        # recording method explicitly disabled or enabled
        if recording_method:
            for one_recording_method in RECORDING_METHODS:
                if one_recording_method == recording_method.lower():
                    env_var = "_".join(["APPMAP", "RECORD", recording_method.upper()])
                    if env_var in os.environ:
                        if os.environ[env_var].lower() == "false":
                            return False, logging.INFO, cls._log_prefix(False, f"{env_var}=false")
                        elif os.environ[env_var].lower() == "true":
                            return True, logging.INFO, cls._log_prefix(True, f"{env_var}=true")
                        else:
                            return False, logging.WARNING, cls._log_prefix(False, f"{env_var}={os.environ[env_var]} is an invalid option")

        # check if name of APPMAP_RECORD_ env variable was defined incorrectly
        for env_var in os.environ:
            env_var_as_list = env_var.split("_")
            if (
                len(env_var_as_list) > 2
                and env_var_as_list[0] == "APPMAP"
                and env_var_as_list[1] == "RECORD"
            ):
                if not (env_var_as_list[2].lower() in RECORDING_METHODS):
                    return False, logging.WARNING, cls._log_prefix(False, f"{env_var} is an invalid recording method")

        # it's flask
        message, should_enable = cls.is_flask_and_should_enable()
        if should_enable in [True, False]:
            return should_enable, logging.INFO, cls._log_prefix(should_enable, f"{message}")

        # it's django
        message, should_enable = cls.is_django_and_should_enable()
        if should_enable in [True, False]:
            return should_enable, logging.INFO, cls._log_prefix(should_enable, f"{message}")

        if recording_method in RECORDING_METHODS:
            return True, logging.INFO, cls._log_prefix(True, f"will record by default")

        return False, logging.INFO, cls._log_prefix(False, f"it's not enabled by any configuration or framework")

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
