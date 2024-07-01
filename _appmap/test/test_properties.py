"""Tests for methods decorated with @property"""

# pyright: reportMissingImports=false
# pylint: disable=import-error,import-outside-toplevel
import pytest
from _appmap.test.helpers import DictIncluding

pytestmark = [
    pytest.mark.appmap_enabled,
]


@pytest.fixture(autouse=True)
def setup(with_data_dir):  # pylint: disable=unused-argument
    # with_data_dir sets up sys.path so example_class can be imported
    pass


def test_getter_instrumented(events):
    from example_class import ExampleClass

    ec = ExampleClass()

    actual = ExampleClass.read_only.__doc__
    assert actual == "Read-only"

    assert ec.read_only == "read only"

    with pytest.raises(AttributeError, match=r".*(has no setter|can't set attribute).*"):
        # E           AttributeError: can't set attribute

        ec.read_only = "not allowed"

    with pytest.raises(AttributeError, match=r".*(has no deleter|can't delete attribute).*"):
        del ec.read_only

    assert len(events) == 2
    assert events[0].to_dict() == DictIncluding(
        {
            "event": "call",
            "defined_class": "example_class.ExampleClass",
            "method_id": "read_only (get)",
        }
    )


def test_accessible_instrumented(events):
    from example_class import ExampleClass

    ec = ExampleClass()
    assert ExampleClass.fully_accessible.__doc__ == "Fully-accessible"

    assert ec.fully_accessible == "fully accessible"

    ec.fully_accessible = "updated"
    # Check the value of the attribute directly, to avoid extra events
    assert ec._fully_accessible == "updated"  # pylint: disable=protected-access

    del ec.fully_accessible

    # assert len(events) == 6
    assert events[0].to_dict() == DictIncluding(
        {
            "event": "call",
            "defined_class": "example_class.ExampleClass",
            "method_id": "fully_accessible (get)",
        }
    )

    assert events[2].to_dict() == DictIncluding(
        {
            "event": "call",
            "defined_class": "example_class.ExampleClass",
            "method_id": "fully_accessible (set)",
        }
    )

    assert events[4].to_dict() == DictIncluding(
        {
            "event": "call",
            "defined_class": "example_class.ExampleClass",
            "method_id": "fully_accessible (del)",
        }
    )


def test_writable_instrumented(events):
    from example_class import ExampleClass

    ec = ExampleClass()
    assert ExampleClass.write_only.__doc__ == "Write-only"

    with pytest.raises(AttributeError, match=r".*(has no getter|unreadable attribute).*"):
        _ = ec.write_only

    ec.write_only = "updated example"

    assert len(events) == 2
    assert events[0].to_dict() == DictIncluding(
        {
            "event": "call",
            "defined_class": "example_class.ExampleClass",
            "method_id": "set_write_only (set)",
        }
    )
