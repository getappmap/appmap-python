import pytest

from appmap.wrapt import BoundFunctionWrapper, FunctionWrapper


@pytest.mark.appmap_enabled
@pytest.mark.usefixtures("with_data_dir")
class TestLabels:
    def test_labeled(self, verify_example_appmap):
        def check_labels(self, to_dict):
            if self.name == "labeled_method":
                assert list(self.labels) == ["super", "important"]
            ret = to_dict(self)
            return ret

        verify_example_appmap(check_labels, "labeled_method")

    def test_unlabeled(self, verify_example_appmap):
        def check_labels(self, to_dict):
            if self.name == "instance_method":
                assert not self.labels
            ret = to_dict(self)
            return ret

        verify_example_appmap(check_labels, "instance_method")

    def test_class_instrumented_by_preset(self, verify_example_appmap):
        def check_labels(*_):
            from http.client import (  # pyright: ignore[reportMissingImports] pylint: disable=import-error,import-outside-toplevel
                HTTPConnection,
            )

            assert isinstance(
                HTTPConnection.request, BoundFunctionWrapper
            ), "HTTPConnection.request should be instrumented"

            assert not isinstance(
                HTTPConnection.getresponse, BoundFunctionWrapper
            ), "HTTPConnection.getresponse should not be instrumented"

        verify_example_appmap(check_labels, "instance_method")

    def test_mod_instrumented_by_preset(self, verify_example_appmap):
        def check_labels(*_):
            import yaml  # pylint: disable=import-outside-toplevel

            assert isinstance(
                yaml.scan, FunctionWrapper
            ), "yaml.scan should be instrumented"

            assert not isinstance(
                yaml.emit, FunctionWrapper
            ), "yaml.emit should not be instrumented"

        verify_example_appmap(check_labels, "instance_method")

    def test_function_only_in_mod(self, verify_example_appmap):
        def check_labels(*_):
            # pylint: disable=import-outside-toplevel
            import hmac

            # pylint: enable=import-outside-toplevel
            #
            # It would be good to do this test, too (even though we're testing that module functions
            # are labeled by presets). hmac.create_digest is a builtin-function, though, so this
            # won't work until https://github.com/getappmap/appmap-python/issues/216 is fixed.
            #
            # assert isinstance(
            #     hmac.create_digest, FunctionWrapper
            # ), "hmac.compare_digest should be instrumented"

            assert not isinstance(
                hmac.HMAC.update, BoundFunctionWrapper
            ), "hmac.HMAC.update should not be instrumented"

        verify_example_appmap(check_labels, "instance_method")
