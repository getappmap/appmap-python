import json
import pytest

import numpy as np

from _appmap.generation import AppMapEncoder


@pytest.mark.appmap_enabled
@pytest.mark.usefixtures("with_data_dir")
class TestGeneration:
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

    def test_docstring(self, verify_example_appmap):
        def check_comment(self, to_dict):
            if self.name == "with_docstring":
                assert self.comment == "docstrings can have\nmultiple lines"
            ret = to_dict(self)
            return ret

        verify_example_appmap(check_comment, "with_docstring")

    def test_comment(self, verify_example_appmap):
        def check_comment(self, to_dict):
            if self.name == "with_comment":
                assert self.comment == "# comments can have\n# multiple lines\n"
            ret = to_dict(self)
            return ret

        verify_example_appmap(check_comment, "with_comment")

    def test_none(self, verify_example_appmap):
        def check_comment(self, to_dict):
            if self.name == "instance_method":
                assert not self.comment
            ret = to_dict(self)
            return ret

        verify_example_appmap(check_comment, "instance_method")

class TestAppMapEncoder:
    def test_np_int64_type(self):
        data = {
            "value": np.int64(42),
        }
        json_str = json.dumps(data, cls=AppMapEncoder)
        assert '{"value": "42"}' == json_str

    def test_np_array_type(self):
        data = {
            "value": np.array([0, 1, 2, 3])
        }
        json_str = json.dumps(data, cls=AppMapEncoder)
        assert '{"value": "[0 1 2 3]"}' == json_str
