import pytest

from _appmap.event import describe_value
from _appmap.test.helpers import DictIncluding


def test_describe_value_does_not_call_class():
    """describe_value should not call __class__
    __class__ could be overloaded in the value and
    could cause side effects."""

    class WithOverloadedClass:
        # pylint: disable=missing-class-docstring,too-few-public-methods
        @property
        def __class__(self):
            raise Exception("__class__ called")

    describe_value(None, WithOverloadedClass())


class TestDictValue:
    @pytest.fixture
    def value(self):
        return {"id": 1, "contents": "some text"}

    def test_one_level_schema(self, value):
        actual = describe_value(None, value)
        assert actual == DictIncluding(
            {
                "properties": [
                    {"name": "id", "class": "builtins.int"},
                    {"name": "contents", "class": "builtins.str"},
                ]
            }
        )


class TestNestedDictValue:
    @pytest.fixture
    def value(self):
        return {"page": {"page_number": 1, "page_size": 20, "total": 2383}}

    def test_two_level_schema(self, value):
        actual = describe_value(None, value)
        assert actual == DictIncluding(
            {
                "properties": [
                    {
                        "name": "page",
                        "class": "builtins.dict",
                        "properties": [
                            {"name": "page_number", "class": "builtins.int"},
                            {"name": "page_size", "class": "builtins.int"},
                            {"name": "total", "class": "builtins.int"},
                        ],
                    }
                ]
            }
        )

    def test_respects_max_depth(self, value):
        expected = {"properties": [{"name": "page", "class": "builtins.dict"}]}
        actual = describe_value(None, value, max_depth=1)
        assert actual == DictIncluding(expected)


class TestListOfDicts:
    @pytest.fixture
    def value(self):
        return [{"id": 1, "contents": "some text"}, {"id": 2}]

    def test_an_array_containing_schema(self, value):
        actual = describe_value(None, value)
        assert actual["class"] == "builtins.list"
        assert actual["items"][0] == DictIncluding(
            {
                "class": "builtins.dict",
                "properties": [
                    {"name": "id", "class": "builtins.int"},
                    {"name": "contents", "class": "builtins.str"},
                ],
            }
        )
        assert actual["items"][1] == DictIncluding(
            {
                "class": "builtins.dict",
                "properties": [{"name": "id", "class": "builtins.int"}],
            }
        )


class TestNestedArrays:
    @pytest.fixture
    def value(self):
        return [[["one"]]]

    def test_arrays_ignore_max_depth(self, value):
        actual = describe_value(None, value, max_depth=1)
        expected = {
            "class": "builtins.list",
            "items": [
                {
                    "class": "builtins.list",
                    "items": [
                        {"class": "builtins.list", "items": [{"class": "builtins.str"}]}
                    ],
                }
            ],
        }
        assert actual == DictIncluding(expected)
