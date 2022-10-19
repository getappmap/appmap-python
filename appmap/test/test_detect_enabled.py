"""
Test detecting if AppMap is enabled
"""
import os
import unittest
from unittest.mock import patch

import pytest

from appmap._implementation.detect_enabled import RECORDING_METHODS, DetectEnabled
from appmap._implementation.testing_framework import file_delete


class TestDetectEnabled:
    @staticmethod
    def setup_method():
        DetectEnabled.clear_cache()

    @patch.dict(os.environ, {"APPMAP": "false"})
    def test_none__appmap_disabled(self):
        assert DetectEnabled.should_enable(None) == False

    @patch.dict(os.environ, {"APPMAP": "False"})
    def test_none__appmap_disabled_mixed_case(self):
        assert DetectEnabled.should_enable(None) == False

    @patch.dict(os.environ, {"APPMAP": "true"})
    def test_none__appmap_enabled(self):
        # if there's no recording method then it's disabled
        assert DetectEnabled.should_enable(None) == False

    @patch.dict(os.environ, {"APPMAP": "True"})
    def test_none__appmap_enabled_mixed_case(self):
        assert DetectEnabled.should_enable(None) == False

    @patch.dict(os.environ, {"APPMAP": "invalid_value"})
    def test_none__appmap_invalid_value(self):
        assert DetectEnabled.should_enable(None) == False

    def test_invalid__no_envvar(self):
        assert DetectEnabled.should_enable("invalid_recording_method") == False

    @patch.dict(os.environ, {"APPMAP": "true"})
    def test_invalid__appmap_enabled(self):
        assert DetectEnabled.should_enable("invalid_recording_method") == False

    @patch.dict(os.environ, {"APPMAP": "false"})
    def test_some__appmap_disabled(self):
        for recording_method in RECORDING_METHODS:
            assert DetectEnabled.should_enable(recording_method) == False

    @patch.dict(os.environ, {"APPMAP": "true"})
    def test_some__appmap_enabled(self):
        for recording_method in RECORDING_METHODS:
            assert DetectEnabled.should_enable(recording_method) == True

    recording_methods_as_true = {
        "_".join(["APPMAP", "RECORD", recording_method.upper()]): "true"
        for recording_method in RECORDING_METHODS
    }

    @patch.dict(os.environ, recording_methods_as_true)
    def test_some__recording_method_enabled(self):
        for recording_method in RECORDING_METHODS:
            assert DetectEnabled.should_enable(recording_method) == True

    recording_methods_as_true_mixed_case = {
        key: "True" for key in recording_methods_as_true.keys()
    }

    @patch.dict(os.environ, recording_methods_as_true_mixed_case)
    def test_some__recording_method_enabled_mixed_case(self):
        for recording_method in RECORDING_METHODS:
            assert DetectEnabled.should_enable(recording_method) == True

    recording_methods_as_true_invalid = {"APPMAP_RECORD_INVALID": "true"}

    @patch.dict(os.environ, recording_methods_as_true_invalid)
    def test_some__recording_method_enabled_invalid(self):
        for recording_method in RECORDING_METHODS:
            assert DetectEnabled.should_enable(recording_method) == False

    recording_methods_as_false = {
        "_".join(["APPMAP", "RECORD", recording_method.upper()]): "false"
        for recording_method in RECORDING_METHODS
    }

    @patch.dict(os.environ, recording_methods_as_false)
    def test_some__recording_method_disabled(self):
        for recording_method in RECORDING_METHODS:
            assert DetectEnabled.should_enable(recording_method) == False

    recording_methods_as_false_mixed_case = {
        key: "False" for key in recording_methods_as_false.keys()
    }

    @patch.dict(os.environ, recording_methods_as_false_mixed_case)
    def test_some__recording_method_disabled_mixed_case(self):
        for recording_method in RECORDING_METHODS:
            assert DetectEnabled.should_enable(recording_method) == False


class TestDetectEnabledFlask:
    @staticmethod
    def setup_method():
        DetectEnabled.clear_cache()

    def test__none(self):
        assert DetectEnabled.should_enable(None) == False

    @patch.dict(os.environ, {"FLASK_APP": "app.py"})
    def test__flask_app(self):
        assert DetectEnabled.should_enable(None) == False

    @patch.dict(os.environ, {"FLASK_DEBUG": "0"})
    def test__flask_debug_0(self):
        assert DetectEnabled.should_enable("requests") == False

    @patch.dict(os.environ, {"FLASK_DEBUG": "1"})
    def test__flask_debug_1(self):
        assert DetectEnabled.should_enable("requests") == True

    @patch.dict(os.environ, {"FLASK_ENV": "production"})
    def test__flask_env_production(self):
        assert DetectEnabled.should_enable("requests") == False

    @patch.dict(os.environ, {"FLASK_ENV": "development"})
    def test__flask_env_development(self):
        assert DetectEnabled.should_enable("requests") == True


class TestDetectEnabledDjango:
    @staticmethod
    def setup_method():
        DetectEnabled.clear_cache()

    def test__none(self):
        assert DetectEnabled.should_enable(None) == False

    def driver(
        self,
        data_dir,
        monkeypatch,
        django_settings_module,
        basename_settings,
        extra_settings_content,
        expected,
    ):
        settings_content = (
            """
# If the SECRET_KEY isn't defined we get the misleading error message
# CommandError: You must set settings.ALLOWED_HOSTS if DEBUG is False.
SECRET_KEY = "3*+d^_kjnr2gz)4q2m(&&^%$p4fj5dk3%lz4pl3g4m-%6!gf&)"

# Must set ROOT_URLCONF else we get
# AttributeError: 'Settings' object has no attribute 'ROOT_URLCONF'
ROOT_URLCONF = "app.urls"

MIDDLEWARE = ["appmap.django.Middleware"]

"""
            + extra_settings_content
            + """
"""
        )
        monkeypatch.syspath_prepend(data_dir / "django")
        monkeypatch.setenv("DJANGO_SETTINGS_MODULE", django_settings_module)
        filename = data_dir / "django" / "app" / basename_settings
        try:
            with open(filename, "w") as f:
                f.write(settings_content)
            monkeypatch.chdir(str(data_dir / "django"))
            assert DetectEnabled.should_enable("requests") == expected
        finally:
            file_delete(filename)

    def test__debug_false(self, data_dir, monkeypatch):
        self.driver(
            data_dir,
            monkeypatch,
            "app.settings_debug_false",
            "settings_debug_false.py",
            "DEBUG = False",
            False,
        )

    def test__debug_true(self, data_dir, monkeypatch):
        self.driver(
            data_dir,
            monkeypatch,
            "app.settings_debug_true",
            "settings_debug_true.py",
            "DEBUG = True",
            True,
        )

    # note this is APPMAP = False in the settings, not the env
    def test__appmap_false(self, data_dir, monkeypatch):
        self.driver(
            data_dir,
            monkeypatch,
            "app.settings_appmap_false",
            "settings_appmap_false.py",
            "APPMAP = False",
            False,
        )

    def test__appmap_true(self, data_dir, monkeypatch):
        self.driver(
            data_dir,
            monkeypatch,
            "app.settings_appmap_true",
            "settings_appmap_true.py",
            "APPMAP = True",
            True,
        )
